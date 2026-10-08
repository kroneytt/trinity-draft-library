-- Trinity Draft - Table layout + automated 3-player draft (Global script)
--
-- TABLE: the three playmats form a triangle. Each mat's top edge (Reserve, Life,
-- Wall corners) faces the centre, as in the rulebook (pp. 26-27, 36). The middle
-- of the triangle is the shared area for basic colour cards and Trinity Counters,
-- and the mats' angled corners meet where the Wall cards go.
--
-- Mats are scaled from a real card measured in-game, so the printed card
-- outlines on the mat match the cards. All mat sizes below are in "card widths" (cw).
--
-- DRAFT (one pack at a time):
--   * 9 packs of 13 cards are opened one after another.
--   * The open pack goes into the hand of the player whose turn it is (a hand is
--     private, so nobody else sees the pack).
--   * That player drags ONE card from their hand onto their own playmat. It is
--     stacked face down on their PICKS pile (the deck slot) and the rest of the
--     pack moves into the next player's hand automatically.
--   * Odd packs travel clockwise, even packs anti-clockwise, until the pack is empty.
--   * The first pick of each pack rotates Red -> Green -> Blue, so every player
--     opens 3 packs and ends with exactly 39 cards (13 cards = 5 + 4 + 4 per pack).
--
-- Seats seen from above (+x right, +z up): Red = bottom, Green = top-left,
-- Blue = top-right. Clockwise is therefore Red -> Green -> Blue -> Red.

local NUM_PACKS  = 9
local PACK_SIZE  = 13
local PLAYERS    = {"Red", "Green", "Blue"}
local ANGLE      = {Red = 0, Green = 120, Blue = 240}   -- seat rotation (rotY), must match build_tts_save.py

local NEXT_CLOCKWISE     = {Red = "Green", Green = "Blue",  Blue  = "Red"}
local NEXT_ANTICLOCKWISE = {Red = "Blue",  Blue  = "Green", Green = "Red"}

-- Playmat geometry, measured from images/playmat.jpg (1024 x 595 px, one card = 120 px wide).
local MAT_PX_W, MAT_PX_H, CARD_PX_W = 1024, 595, 120
local function px(x, y)   -- playmat pixel -> mat-local {right, forward} in card widths
    return {(x - MAT_PX_W / 2) / CARD_PX_W, (MAT_PX_H / 2 - y) / CARD_PX_W}
end
local MAT_ZONES = {
    deck   = px(908, 307),                                              -- 山札 slot = PICKS pile during the draft
    epics  = {MAT_PX_W / 2 / CARD_PX_W + 0.9, px(908, 307)[2]},         -- just outside the mat, beside the deck
}
local MAT_GAP_CW   = 0.15   -- small gap between neighbouring mats at the triangle corners
local HAND_BEHIND  = 2.0    -- hand zone distance behind the mat's back edge, in cw
local PICK_CONFIRM_SECONDS = 1.0   -- grace period to drag a pick back before the pack moves on

-- Battle components (rulebook pp. 26-27). Distances in card widths (cw).
local COMPONENT_BASE = "https://raw.githubusercontent.com/kroneytt/trinity-draft-library/main/images/components/"
local RESERVE_POS   = px(514, 16)       -- top centre of the mat, half overhanging towards the middle
local WALL_DIST     = 3.0               -- wall card centre, from the table centre towards each triangle corner
-- Squares on the Wall card, along its length (image 1200 px tall = 1.4 cw), from player A's end to B's end.
local WALL_SQUARES  = {-0.4375, -0.142, 0.152, 0.446}
local COUNTER_SIDE  = 0.30              -- Trinity Counter side; Reserve triangle slots are 0.33 cw
local NUM_COUNTERS  = 30
local WALL_PAIRS    = {{"Red", "Green"}, {"Green", "Blue"}, {"Blue", "Red"}}   -- A -> B is clockwise
local atan2 = math.atan2 or math.atan
local pickLabels = {}

local LAID_OUT = false
local MAT_YAW  = 0          -- extra mat rotation; the "Rotate playmats" button toggles 0 / 180

local STATE = "IDLE"        -- IDLE | DEALING | DRAFTING | MOVING | POST_DRAFT
local ACTIVE_EXPANSION = nil
local PACK = 1              -- 1..NUM_PACKS
local TURN = nil            -- colour whose turn it is
local packCards = {}        -- GUID -> true for cards still in the open pack
local pileOf    = {}        -- GUID -> colour, for cards already picked
local pickCount = {Red = 0, Green = 0, Blue = 0}
local picksZones = {}       -- colour -> scripting zone over the PICKS pile
local pendingPick = nil     -- GUID of a card dropped on the pile but not yet confirmed

------------------------------------------------------------------ helpers

-- Plain-text containment test.  NOTE: do not use string.find with a pattern
-- here: "-" is a quantifier in Lua patterns, so "TD-02" never matches itself.
local function contains(s, sub)
    return s ~= nil and s:find(sub, 1, true) ~= nil
end

local function kind(obj)
    return obj.type or obj.tag
end

local function packSize(obj)
    if obj == nil then return 0 end
    if kind(obj) == "Deck" then return #obj.getObjects() end
    return 1
end

local function isClockwise() return PACK % 2 == 1 end
local function directionText() return isClockwise() and "clockwise" or "anti-clockwise" end
local function nextPlayer(color)
    return (isClockwise() and NEXT_CLOCKWISE or NEXT_ANTICLOCKWISE)[color]
end

local function getMasterDeck(expansion)
    for _, obj in ipairs(getObjects()) do
        if kind(obj) == "Deck" and obj.getGMNotes() == "master_pool_" .. expansion then
            return obj
        end
    end
    return nil
end

local function updateStatus(text)
    Global.UI.setValue("statusText", text)
end

------------------------------------------------------------------ table layout

local CW, MAT_W, MAT_D, SEAT_R = 2.0, 17.0, 10.0, 10.0   -- replaced by calibrate()

local function rad(c) return math.rad(ANGLE[c]) end

-- Mat-local (right, forward) in cw -> world position. "forward" points at the table centre.
local function seatPoint(color, right, forward, y)
    local a = rad(color)
    local rx, rz = math.cos(a), -math.sin(a)       -- player's right
    local fx, fz = math.sin(a),  math.cos(a)       -- towards the centre
    local cx, cz = -fx * SEAT_R, -fz * SEAT_R      -- mat centre
    return {cx + (rx * right + fx * forward) * CW, y, cz + (rz * right + fz * forward) * CW}
end

local function findByNotes(notes)
    for _, obj in ipairs(getObjects()) do
        if obj.getGMNotes() == notes then return obj end
    end
    return nil
end

local function calibrate()
    -- Card width from any deck (all cards share one size).
    local sample = findByNotes("master_pool_TD-01") or findByNotes("master_pool_TD-02")
    if sample then CW = sample.getBoundsNormalized().size.x end

    -- Scale every mat so it is exactly MAT_PX_W / CARD_PX_W cards wide.
    local targetW = CW * MAT_PX_W / CARD_PX_W
    for _, p in ipairs(PLAYERS) do
        local mat = findByNotes("playmat_" .. p)
        if mat then
            local w = mat.getBoundsNormalized().size.x
            if w > 0 then
                local f, sc = targetW / w, mat.getScale()
                mat.setScale({sc.x * f, sc.y, sc.z * f})
            end
            MAT_D = mat.getBoundsNormalized().size.z / CW   -- after scaling, in cw
        end
    end
    MAT_W = MAT_PX_W / CARD_PX_W
    if MAT_D <= 0 or MAT_D > MAT_W then MAT_D = MAT_W * MAT_PX_H / MAT_PX_W end

    -- Mats' top edges form an equilateral triangle with side = mat width + gap.
    local side = MAT_W + MAT_GAP_CW
    SEAT_R = (side / (2 * math.sqrt(3)) + MAT_D / 2) * CW   -- world units

    -- Warn if the triangle does not fit on the table.
    local reach = math.sqrt((SEAT_R + MAT_D * CW / 2) ^ 2 + (MAT_W * CW / 2) ^ 2)
    local ok, tbl = pcall(function() return Tables.getTableObject() end)
    if ok and tbl then
        local size = tbl.getBounds().size
        local half = math.min(size.x, size.z) / 2
        if reach > half then
            printToAll(string.format("[TD layout] Mats reach %.1f from centre but the table is only %.1f - switch to a bigger table.", reach, half), {1, 0.5, 0})
        end
    end
    log(string.format("[TD layout] card width %.2f, mat %.2f x %.2f cw, seat radius %.2f", CW, MAT_W, MAT_D, SEAT_R))
end

local function rotateMats()
    for _, p in ipairs(PLAYERS) do
        local mat = findByNotes("playmat_" .. p)
        if mat then mat.setRotation({0, ANGLE[p] + MAT_YAW, 0}) end
    end
end

local function pilePoint(color, height)
    local d = MAT_ZONES.deck
    return seatPoint(color, d[1], d[2], 1.6 + (height or 0) * 0.02)
end

function layoutTable()
    calibrate()

    local mats = {}
    for _, p in ipairs(PLAYERS) do
        local mat = findByNotes("playmat_" .. p)
        if mat then
            mat.setLock(false)
            mat.setPosition(seatPoint(p, 0, 0, 2))
            mat.setRotation({0, ANGLE[p] + MAT_YAW, 0})
            table.insert(mats, mat)
        end

        -- PICKS zone covers the whole mat: dropping a card anywhere on your own mat
        -- counts as your pick (it is then stacked on the deck slot).
        local z = picksZones[p]
        if z then
            z.setPosition(seatPoint(p, 0, 0, 2))
            z.setRotation({0, ANGLE[p], 0})
            z.setScale({MAT_W * CW, 4, MAT_D * CW})
        end

        -- Hand sits behind the mat, facing the centre.
        local back = -(MAT_D / 2 + HAND_BEHIND)
        Player[p].setHandTransform({
            position = seatPoint(p, 0, back, 4),
            rotation = {0, ANGLE[p], 0},
            scale    = {MAT_W * CW, 5, 4},
        })
    end

    local function finish()
        for _, m in ipairs(mats) do m.setLock(true) end
        placeCards()
        LAID_OUT = true
    end
    -- Once the mats have settled on the table, lock them and place the cards.
    Wait.condition(finish, function()
        for _, m in ipairs(mats) do if not m.resting then return false end end
        return true
    end, 5, finish)
end

local function seatDir(c)          -- unit vector from the table centre towards a seat
    local a = rad(c)
    return -math.sin(a), -math.cos(a)
end

local function norm(x, z) local l = math.sqrt(x * x + z * z); return x / l, z / l end

-- Wall card between seats A and B: centre, unit vector A->B along the card, and yaw.
local function wallGeometry(a, b)
    local ax, az = seatDir(a)
    local bx, bz = seatDir(b)
    local vx, vz = norm(ax + bx, az + bz)          -- towards the triangle corner between them
    local ux, uz = norm(bx - ax, bz - az)          -- along the card, from A's side to B's side
    local yaw = math.deg(atan2(ux, uz))
    return {vx * WALL_DIST * CW, vz * WALL_DIST * CW}, {ux, uz}, yaw
end

function placeCards()
    local y = 3
    local inr = (MAT_W + MAT_GAP_CW) / (2 * math.sqrt(3))   -- centre to each mat's top edge, cw

    -- Master pools wait outside the triangle, beyond the corner between Green and Blue.
    local poolZ = (2 * inr + 2.0) * CW
    local m1, m2 = findByNotes("master_pool_TD-01"), findByNotes("master_pool_TD-02")
    if m1 then m1.setPosition({-0.7 * CW, y, poolZ}); m1.setRotation({0, 180, 180}) end
    if m2 then m2.setPosition({ 0.7 * CW, y, poolZ}); m2.setRotation({0, 180, 180}) end

    -- (1) Reserve: top centre of each mat, landscape, ability text towards its owner.
    for _, p in ipairs(PLAYERS) do
        local r = findByNotes("reserve_" .. p)
        if r then
            r.setPosition(seatPoint(p, RESERVE_POS[1], RESERVE_POS[2], 2))
            r.setRotation({0, ANGLE[p] - 90, 0})
            r.setLock(true)
        end
    end

    -- (4) Wall cards between each pair of players, diagonally in front of the Reserves.
    for _, pair in ipairs(WALL_PAIRS) do
        local w = findByNotes("wallcard_" .. pair[1] .. "_" .. pair[2])
        if w then
            local c, _, yaw = wallGeometry(pair[1], pair[2])
            w.setPosition({c[1], 2, c[2]})
            w.setRotation({0, yaw, 0})
            w.setLock(true)
            local snaps = {}
            for _, off in ipairs(WALL_SQUARES) do
                table.insert(snaps, {position = {0, 0.1, off * CW}, rotation = {0, 0, 0}, rotation_snap = true})
            end
            w.setSnapPoints(snaps)
        end
    end

    -- (3) Basic colour cards in the centre (Red, Yellow / Purple, Blue as drawn on p.27).
    local grid = {Red = {-0.55, 0.75}, Yellow = {0.55, 0.75}, Purple = {-0.55, -0.75}, Blue = {0.55, -0.75}}
    for col, g in pairs(grid) do
        local d = findByNotes("colordeck_" .. col)
        if d then d.setPosition({g[1] * CW, y, g[2] * CW}); d.setRotation({0, 0, 0}) end
    end

    -- (3) Trinity Counters: a bag of 30 in the centre, towards the Green/Blue corner.
    local bag = findByNotes("counter_bag")
    if bag then
        bag.setPosition({0, y, 2.0 * CW})
        fillCounterBag(bag)
    end

    -- Each player's Epics beside their deck slot. The two expansions get separate
    -- spots: decks dropped on top of each other merge into one deck in TTS.
    placeEpics()
end

local EPIC_OFFSET = {["TD-01"] = 0, ["TD-02"] = 1.6}   -- extra cw towards the centre

function placeEpics(onlyExpansion)
    for _, obj in ipairs(getObjects()) do
        local notes = obj.getGMNotes() or ""
        for _, p in ipairs(PLAYERS) do
            for exp, off in pairs(EPIC_OFFSET) do
                if notes == "epics_" .. p .. "_" .. exp then
                    local e = MAT_ZONES.epics
                    local f = onlyExpansion and 0 or off
                    obj.setPosition(seatPoint(p, e[1], e[2] + f, 3))
                    obj.setRotation({0, ANGLE[p], 180})
                end
            end
        end
    end
end

local function tokenData(name, notes, image, thickness, stackable, pos, yaw, scale)
    return {
        Name = "Custom_Token", Nickname = name, GMNotes = notes,
        Transform = {posX = pos[1], posY = pos[2], posZ = pos[3], rotX = 0, rotY = yaw, rotZ = 0,
                     scaleX = scale, scaleY = 1, scaleZ = scale},
        CustomImage = {ImageURL = COMPONENT_BASE .. image, ImageSecondaryURL = "", ImageScalar = 1.0, WidthScale = 0.0,
                       CustomToken = {Thickness = thickness, MergeDistancePixels = 15.0, StandUp = false, Stackable = stackable}},
    }
end

-- Spawns one token, waits for its image, then rescales it so it is `width` world units wide.
local function spawnSizedToken(data, width, done)
    spawnObjectData({data = data, callback_function = function(o)
        local function size()
            local w = o.getBoundsNormalized().size.x
            if w > 0 then
                local sc = o.getScale()
                local f = width / w
                o.setScale({sc.x * f, sc.y, sc.z * f})
            end
            if done then done(o) end
        end
        Wait.condition(size, function() return not o.loading_custom end, 10, size)
    end})
end

-- 30 triangular Trinity Counters, each sized to sit inside a Reserve triangle slot.
function fillCounterBag(bag)
    if #bag.getObjects() > 0 then return end
    local here = bag.getPosition()
    for i = 1, NUM_COUNTERS do
        local data = tokenData("Trinity Counter", "trinity_counter", "trinity_counter.png", 0.15, true,
                               {here.x, here.y + 3 + i * 0.1, here.z}, 0, 1)
        spawnSizedToken(data, COUNTER_SIDE * CW, function(o) bag.putObject(o) end)
    end
end

-- Wall markers ("the line"), placed once the first player is known (rulebook p.26 step 4):
--   1st player: both of their walls one square towards themselves
--   2nd player: their left wall one square towards themselves
--   3rd player: both walls one square towards the opponent (Favourable)
-- Play goes clockwise, and the next player clockwise sits on your left, so this means:
--   wall(1st,2nd) and wall(3rd,1st) on the 1st player's side, wall(2nd,3rd) on the 2nd player's side.
function placeWallMarkers(first)
    for _, obj in ipairs(getObjects()) do
        if obj.getGMNotes() == "wall_marker" then obj.destruct() end
    end
    for _, pair in ipairs(WALL_PAIRS) do
        local a, b = pair[1], pair[2]
        local c, u, yaw = wallGeometry(a, b)
        local off = (b == first) and WALL_SQUARES[3] or WALL_SQUARES[2]   -- square next to the middle, on that side
        local pos = {c[1] + u[1] * off * CW, 2.4, c[2] + u[2] * off * CW}
        spawnSizedToken(tokenData("Wall", "wall_marker", "wall_marker.png", 0.12, false, pos, yaw, 1), 1.15 * CW)
    end
end

-- Buttons on the post-draft panel: onClick="setFirstPlayer(Red)" etc.
function setFirstPlayer(player, first)
    if first ~= "Red" and first ~= "Green" and first ~= "Blue" then return end
    local second = NEXT_CLOCKWISE[first]
    local third  = NEXT_CLOCKWISE[second]
    placeWallMarkers(first)
    Global.UI.setAttribute("restartPanel", "active", "false")
    updateStatus("Battle: " .. first .. " -> " .. second .. " -> " .. third .. " (clockwise)")
    broadcastToAll("Turn order: 1st " .. first .. ", 2nd " .. second .. ", 3rd " .. third .. ". Walls placed: " ..
        first .. " has both walls one square towards them, " .. second .. " has their left wall towards them, " ..
        third .. " starts with both walls Favourable. Everyone draws 5, then: Awakening! Trinity Draft!", {1, 1, 0.6})
end

-- Button on the setup panel: if a mat image appears upside down, this turns all
-- three mats 180 degrees (the layout of cards and zones does not change).
function toggleMatRotation(player)
    MAT_YAW = (MAT_YAW == 0) and 180 or 0
    rotateMats()
end

------------------------------------------------------------------ save / load

function onSave()
    return JSON.encode({laidOut = LAID_OUT, matYaw = MAT_YAW})
end

function onLoad(saved)
    math.randomseed(os.time())
    local ok, data = pcall(function() return JSON.decode(saved or "") end)
    if ok and type(data) == "table" then
        if data.laidOut then LAID_OUT = true end
        if data.matYaw then MAT_YAW = data.matYaw end
    end

    for _, obj in ipairs(getObjects()) do
        local name  = obj.getName() or ""
        local notes = obj.getGMNotes() or ""
        for _, p in ipairs(PLAYERS) do
            if name == "PicksZone_" .. p or notes == "pickszone_" .. p then
                picksZones[p] = obj
            end
        end
    end
    for _, p in ipairs(PLAYERS) do
        if not picksZones[p] then
            printToAll("Picks zone for " .. p .. " not found - rebuild the save with tools/build_tts_save.py", {1, 0, 0})
        end
    end

    createMainUI()
    if not LAID_OUT then Wait.frames(layoutTable, 10) end
end

------------------------------------------------------------------ UI

function createMainUI()
    -- Reminder: escape & as &amp; in XML or the whole UI fails to parse.
    Global.UI.setXml([[
    <Defaults>
        <Panel rectAlignment="MiddleCenter" color="#333333E6" outline="#000000" outlineSize="2" />
        <Button fontSize="18" textColor="#FFFFFF" colors="#444444|#555555|#333333|#000000" />
        <Text fontSize="24" color="#FFFFFF" outline="#000000" outlineSize="1" />
    </Defaults>

    <Panel id="setupPanel" width="420" height="250" offsetXY="0 0" active="true">
        <VerticalLayout padding="20 20 20 20" spacing="10">
            <Text>Start Draft</Text>
            <HorizontalLayout spacing="10" preferredHeight="60">
                <Button id="btnTD01" onClick="startDraft(TD-01)">Play TD-01</Button>
                <Button id="btnTD02" onClick="startDraft(TD-02)">Play TD-02</Button>
            </HorizontalLayout>
            <Button onClick="toggleMatRotation" fontSize="14" preferredHeight="34">Playmat upside down? Rotate playmats 180</Button>
        </VerticalLayout>
    </Panel>

    <Panel id="statusPanel" width="520" height="110" rectAlignment="UpperCenter" offsetXY="0 -20" color="#000000B3" active="false">
        <Text id="statusText" color="#FFD700" fontSize="20">Pack 1</Text>
    </Panel>

    <Panel id="turnPanel" width="560" height="120" rectAlignment="LowerCenter" offsetXY="0 230" color="#0B3D2EE6" active="false" visibility="Red">
        <VerticalLayout padding="12 12 8 8" spacing="4">
            <Text fontSize="30" color="#7CFFC4">YOUR PICK</Text>
            <Text fontSize="17">Drag ONE card from your hand onto your playmat.
The rest of the pack goes to the next player automatically.</Text>
        </VerticalLayout>
    </Panel>

    <Panel id="restartPanel" width="440" height="300" offsetXY="0 0" active="false">
        <VerticalLayout padding="14 14 12 12" spacing="8">
            <Text fontSize="22">Battle set-up: who goes first?</Text>
            <Text fontSize="14">Decide with rock-paper-scissors (p.26), then click. Play goes clockwise.</Text>
            <HorizontalLayout spacing="8" preferredHeight="50">
                <Button onClick="setFirstPlayer(Red)" colors="#8E1B26|#A8232F|#6E1520|#000000">Red</Button>
                <Button onClick="setFirstPlayer(Green)" colors="#1F6B32|#27843E|#175226|#000000">Green</Button>
                <Button onClick="setFirstPlayer(Blue)" colors="#1D4F91|#245FAD|#163C6E|#000000">Blue</Button>
            </HorizontalLayout>
            <Button onClick="continueDraft" preferredHeight="40">Draft again (next 9 packs)</Button>
            <Button onClick="restartDraft" preferredHeight="40">Reshuffle and Restart</Button>
        </VerticalLayout>
    </Panel>
    ]])
end

local function refreshStatus()
    if not TURN then return end
    updateStatus("Pack " .. PACK .. "/" .. NUM_PACKS .. " (" .. directionText() .. ")" ..
                 "\n" .. TURN .. " is picking  -  Red " .. pickCount.Red ..
                 " | Green " .. pickCount.Green .. " | Blue " .. pickCount.Blue .. "  of 39")
end

------------------------------------------------------------------ draft: setup

-- exp arrives as the "value" of onClick="startDraft(TD-01)"
function startDraft(player, exp)
    if STATE ~= "IDLE" then return end
    if not LAID_OUT then
        broadcastToAll("Table is still being set up, try again in a second.", {1, 0.6, 0})
        return
    end
    if exp ~= "TD-01" and exp ~= "TD-02" then
        broadcastToAll("Unknown expansion: " .. tostring(exp), {1, 0, 0})
        return
    end

    ACTIVE_EXPANSION = exp

    -- Remove everything that belongs to the other expansion (master pool + epics).
    local other = (exp == "TD-01") and "TD-02" or "TD-01"
    for _, obj in ipairs(getObjects()) do
        if contains(obj.getName(), "(" .. other .. ")")
           or contains(obj.getGMNotes(), "master_pool_" .. other) then
            obj.destruct()
        end
    end

    -- The chosen expansion's 4 Epics move onto each player's Epic spot.
    Wait.frames(function() placeEpics(exp) end, 5)

    local deck = getMasterDeck(exp)
    if not deck then
        broadcastToAll("Error: master deck for " .. exp .. " not found!", {1, 0, 0})
        return
    end
    deck.shuffle()

    Global.UI.setAttribute("setupPanel", "active", "false")
    Global.UI.setAttribute("restartPanel", "active", "false")
    Global.UI.setAttribute("statusPanel", "active", "true")
    beginDraft()
end

local function showPickLabels(on)
    for _, l in ipairs(pickLabels) do if not l.isDestroyed() then l.destruct() end end
    pickLabels = {}
    if not on then return end
    for _, p in ipairs(PLAYERS) do
        local d = MAT_ZONES.deck
        local label = spawnObject({type = "3DText", position = seatPoint(p, d[1], d[2] + 0.95, 1.3),
                                   rotation = {90, ANGLE[p], 0}})
        label.TextTool.setValue("PICKS")
        label.TextTool.setFontSize(48)
        table.insert(pickLabels, label)
    end
end

function beginDraft()
    showPickLabels(true)
    PACK = 1
    pickCount = {Red = 0, Green = 0, Blue = 0}
    broadcastToAll("Draft starts! When the pack arrives in your hand, drag ONE card onto your playmat. " ..
                   "It goes face down on your PICKS pile and the rest of the pack moves on by itself.", {0, 1, 0})
    Wait.time(openPack, 1)
end

-- Player who opens pack k: Red, Green, Blue, Red, ... so everyone opens 3 packs.
local function packOpener(k)
    return PLAYERS[((k - 1) % #PLAYERS) + 1]
end

function openPack()
    local deck = getMasterDeck(ACTIVE_EXPANSION)
    if not deck or packSize(deck) < PACK_SIZE then
        broadcastToAll("Not enough cards left in the master deck. Use Reshuffle and Restart.", {1, 0, 0})
        endDraft()
        return
    end

    STATE = "DEALING"
    TURN = packOpener(PACK)
    packCards = {}
    deck.deal(PACK_SIZE, TURN)
    refreshStatus()
    broadcastToAll("Pack " .. PACK .. " opened by " .. TURN .. ", passing " .. directionText() .. ".", {0.8, 0.8, 0.8})

    -- Remember which cards make up the pack once they have landed in the hand.
    Wait.time(function()
        local n = 0
        for _, c in ipairs(Player[TURN].getHandObjects()) do
            if pileOf[c.getGUID()] == nil then packCards[c.getGUID()] = true; n = n + 1 end
        end
        if n == 0 then
            broadcastToAll("Pack " .. PACK .. " could not be put into " .. TURN .. "'s hand. " ..
                "Check that the save has a " .. TURN .. " hand zone (rebuild it with tools/build_tts_save.py).", {1, 0.3, 0.3})
            STATE = "IDLE"
            return
        end
        startTurn()
    end, 1)
end

function startTurn()
    STATE = "DRAFTING"
    pendingPick = nil
    refreshStatus()
    Global.UI.setAttribute("turnPanel", "visibility", TURN)
    Global.UI.setAttribute("turnPanel", "active", "true")
    broadcastToColor("Your pick! Drag one card from your hand onto your playmat.", TURN, {0.4, 1, 0.4})
end

------------------------------------------------------------------ draft: picking

local function zoneOwner(zone)
    for _, p in ipairs(PLAYERS) do
        if picksZones[p] == zone then return p end
    end
    return nil
end

-- Pack cards (not yet picked) currently sitting on a player's PICKS pile.
local function packCardsOnPile(color)
    local list = {}
    local z = picksZones[color]
    if not z then return list end
    for _, obj in ipairs(z.getObjects()) do
        if packCards[obj.getGUID()] then table.insert(list, obj) end
    end
    return list
end

function onObjectEnterZone(zone, obj)
    local owner = zoneOwner(zone)
    if not owner or not packCards[obj.getGUID()] then return end
    if STATE ~= "DRAFTING" then return end

    if owner ~= TURN then
        broadcastToAll("It is " .. TURN .. "'s pick - that card goes back to " .. TURN .. ".", {1, 0.5, 0.3})
        obj.deal(1, TURN)
        return
    end

    local onPile = packCardsOnPile(owner)
    if #onPile > 1 then
        broadcastToColor("Only one card per pick - take " .. (#onPile - 1) .. " back into your hand.", owner, {1, 0.4, 0.4})
        pendingPick = nil
        return
    end
    pendingPick = obj.getGUID()
    Wait.time(function() confirmPick(owner, pendingPick) end, PICK_CONFIRM_SECONDS)
end

function onObjectLeaveZone(zone, obj)
    local owner = zoneOwner(zone)
    if owner and owner == TURN and pendingPick == obj.getGUID() then
        pendingPick = nil      -- dragged back before it was confirmed
    end
end

function confirmPick(color, guid)
    if STATE ~= "DRAFTING" or color ~= TURN or guid == nil or pendingPick ~= guid then return end
    local onPile = packCardsOnPile(color)
    if #onPile ~= 1 or onPile[1].getGUID() ~= guid then return end

    local card = onPile[1]
    STATE = "MOVING"
    addToPile(color, card)

    local rest = {}
    for _, c in ipairs(Player[color].getHandObjects()) do
        if packCards[c.getGUID()] then table.insert(rest, c) end
    end

    if #rest == 0 then
        finishPack()
    elseif #rest == 1 then
        -- Last card of the pack: it simply goes to the next player's pile.
        local nxt = nextPlayer(color)
        addToPile(nxt, rest[1])
        broadcastToAll("Last card of pack " .. PACK .. " goes to " .. nxt .. ".", {0.8, 0.8, 0.8})
        finishPack()
    else
        passRest(rest, nextPlayer(color))
    end
end

-- Puts a card face down on a player's PICKS pile.
function addToPile(color, card)
    local guid = card.getGUID()
    packCards[guid] = nil
    pileOf[guid] = color
    pickCount[color] = pickCount[color] + 1
    card.setRotation({0, ANGLE[color], 180})
    card.setPositionSmooth(pilePoint(color, pickCount[color]), false, true)
end

-- Moves the rest of the pack out of one hand and deals it into the next player's hand.
-- (Cards are first lifted out face down so the hand releases them cleanly.)
function passRest(cards, toColor)
    for i, c in ipairs(cards) do
        c.setRotation({0, 0, 180})
        c.setPosition({0, 4 + i * 0.05, 0})
    end
    Wait.time(function()
        for _, c in ipairs(cards) do c.deal(1, toColor) end
        TURN = toColor
        Wait.time(startTurn, 1)
    end, 0.3)
end

function finishPack()
    PACK = PACK + 1
    if PACK > NUM_PACKS then
        endDraft()
    else
        Wait.time(openPack, 1)
    end
end

------------------------------------------------------------------ after the draft

function endDraft()
    STATE = "POST_DRAFT"
    TURN = nil
    showPickLabels(false)
    Global.UI.setAttribute("turnPanel", "active", "false")
    -- Gather each player's pile into one face-down deck on their deck slot.
    Wait.time(function()
        for _, p in ipairs(PLAYERS) do
            local mine = {}
            for _, obj in ipairs(getObjects()) do
                if pileOf[obj.getGUID()] == p then table.insert(mine, obj) end
            end
            if #mine > 1 then group(mine) end
        end
    end, 1.5)
    updateStatus("Draft Complete!  Red " .. pickCount.Red .. " | Green " .. pickCount.Green ..
                 " | Blue " .. pickCount.Blue .. " cards")
    Global.UI.setAttribute("restartPanel", "active", "true")
    broadcastToAll("Draft complete! Your 39 picks are face down on your deck slot " ..
                   "(right-click > Search to look through them). Build a 23-card Main Deck and a 16-card Life Deck, " ..
                   "choose your Epic, then pick who goes first.", {1, 1, 0})
end

function continueDraft(player)
    if STATE ~= "POST_DRAFT" then return end
    local deck = getMasterDeck(ACTIVE_EXPANSION)
    if not deck or packSize(deck) < PACK_SIZE * NUM_PACKS then
        broadcastToAll("Not enough cards left for another full draft. Use Reshuffle and Restart.", {1, 0, 0})
        return
    end
    Global.UI.setAttribute("restartPanel", "active", "false")
    pileOf = {}
    beginDraft()
end

function restartDraft(player)
    -- Collecting every drafted card back into the master deck is not automated yet.
    broadcastToAll("Please drag all cards back into the master deck, then reload the save to start a new draft.", {1, 0, 0})
    Global.UI.setAttribute("restartPanel", "active", "false")
end
