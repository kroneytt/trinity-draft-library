-- Trinity Draft - Automated 3-Player Draft
local STATE = "IDLE"
local ACTIVE_EXPANSION = nil
local ROUND = 1
local PACKS_OPENED_THIS_ROUND = 0
local TOTAL_PACKS_OPENED = 0
local PLAYERS = {"Red", "Green", "Blue"}
local PACK_SIZE = 13

local draftZones = {}
local passReady = {Red=false, Green=false, Blue=false}

function onLoad()
    math.randomseed(os.time())
    
    -- Find Draft Zones
    for _, obj in ipairs(getAllObjects()) do
        if obj.getName() == "DraftZone_Red" then draftZones["Red"] = obj
        elseif obj.getName() == "DraftZone_Green" then draftZones["Green"] = obj
        elseif obj.getName() == "DraftZone_Blue" then draftZones["Blue"] = obj
        end
    end
    
    createMainUI()
    createPassButtons()
end

function createMainUI()
    Global.UI.setXml(
    [[
    <Defaults>
        <Panel rectAlignment="MiddleCenter" color="#333333E6" outline="#000000" outlineSize="2" />
        <Button fontSize="18" textColor="#FFFFFF" colors="#444444|#555555|#333333|#000000" />
        <Text fontSize="24" color="#FFFFFF" outline="#000000" outlineSize="1" />
    </Defaults>
    
    <Panel id="setupPanel" width="400" height="200" offsetXY="0 0" active="true">
        <VerticalLayout padding="20 20 20 20" spacing="10">
            <Text>Start Draft</Text>
            <HorizontalLayout spacing="10">
                <Button id="btnTD01" onClick="startDraft(TD-01)">Play TD-01</Button>
                <Button id="btnTD02" onClick="startDraft(TD-02)">Play TD-02</Button>
            </HorizontalLayout>
        </VerticalLayout>
    </Panel>
    
    <Panel id="statusPanel" width="400" height="100" offsetXY="0 300" color="#000000B3" active="false">
        <Text id="statusText" color="#FFD700" fontSize="20">Round 1</Text>
    </Panel>
    
    <Panel id="restartPanel" width="300" height="150" offsetXY="0 0" active="false">
        <VerticalLayout padding="10 10 10 10" spacing="10">
            <Button onClick="continueDraft()">Continue (Next 9 Packs)</Button>
            <Button onClick="restartDraft()">Reshuffle and Restart</Button>
        </VerticalLayout>
    </Panel>
    ]]
    )
end

function createPassButtons()
    local btnParams = {
        click_function = "clickPass",
        function_owner = Global,
        label = "Pass Pack",
        width = 1200, height = 400, font_size = 200,
        color = {0.2, 0.6, 0.2}, font_color = {1,1,1}
    }
    
    for _, p in ipairs(PLAYERS) do
        local z = draftZones[p]
        if z then
            local pos = z.getPosition()
            pos.y = pos.y + 1
            btnParams.position = pos
            -- Spawn an invisible token to attach the button to
            local token = spawnObject({
                type = "BlockSquare",
                position = pos,
                sound = false
            })
            token.setInvisibleTo({"Red","Green","Blue","Black","White"})
            token.setLock(true)
            token.setName("PassBtn_"..p)
            token.createButton(btnParams)
        end
    end
end

function clickPass(obj, color, alt_click)
    -- Find which player's button this is
    local pName = obj.getName():sub(9)
    if pName ~= color and color ~= "Black" then
        broadcastToColor("You cannot pass someone else's pack!", color, {1,0,0})
        return
    end
    
    if STATE ~= "DRAFTING" then return end
    if passReady[pName] then return end
    
    passReady[pName] = true
    obj.editButton({index=0, label="Ready!", color={0.5,0.5,0.5}})
    
    checkAllPassed()
end

function checkAllPassed()
    if passReady["Red"] and passReady["Green"] and passReady["Blue"] then
        -- All passed, execute pass logic
        executePass()
    end
end

function getMasterDeck(expansion)
    for _, obj in ipairs(getAllObjects()) do
        if obj.tag == "Deck" and obj.getGMNotes() == "master_pool_"..expansion then
            return obj
        end
    end
    return nil
end

function startDraft(player, exp)
    ACTIVE_EXPANSION = exp
    ROUND = 1
    TOTAL_PACKS_OPENED = 0
    STATE = "DRAFTING"
    
    Global.UI.setAttribute("setupPanel", "active", "false")
    Global.UI.setAttribute("restartPanel", "active", "false")
    Global.UI.setAttribute("statusPanel", "active", "true")
    
    local other_exp = (exp == "TD-01") and "TD-02" or "TD-01"
    for _, obj in ipairs(getAllObjects()) do
        local name = obj.getName()
        local notes = obj.getGMNotes() or ""
        if name:find("%(" .. other_exp .. "%)") or notes:find("master_pool_" .. other_exp) then
            obj.destruct()
        end
    end

    local deck = getMasterDeck(ACTIVE_EXPANSION)
    if deck then deck.shuffle() end
    
    dealRound()
end

function dealRound()
    Global.UI.setAttribute("statusText", "text", "Round " .. ROUND .. "\nPassing: " .. getPassDirection())
    
    local other_exp = (exp == "TD-01") and "TD-02" or "TD-01"
    for _, obj in ipairs(getAllObjects()) do
        local name = obj.getName()
        local notes = obj.getGMNotes() or ""
        if name:find("%(" .. other_exp .. "%)") or notes:find("master_pool_" .. other_exp) then
            obj.destruct()
        end
    end

    local deck = getMasterDeck(ACTIVE_EXPANSION)
    if not deck then 
        broadcastToAll("Error: Master deck not found!", {1,0,0})
        return
    end
    
    -- Deal 13 cards to each player's draft zone
    for _, p in ipairs(PLAYERS) do
        local z = draftZones[p]
        if z then
            -- Deal 13 cards forming a deck
            local pos = z.getPosition()
            pos.y = pos.y + 0.5
            -- Take 13 cards
            for i=1, PACK_SIZE do
                deck.takeObject({
                    position = pos,
                    flip = true,
                    smooth = false
                })
            end
        end
    end
    
    resetPassButtons()
    broadcastToAll("Round " .. ROUND .. " started! Pick a card and hit Pass.", {0,1,0})
end

function getPassDirection()
    if ROUND == 2 then return "Right (Anti-Clockwise)" end
    return "Left (Clockwise)"
end

function executePass()
    -- Gather the decks in the draft zones
    local currentPacks = {}
    for _, p in ipairs(PLAYERS) do
        currentPacks[p] = nil
        local z = draftZones[p]
        for _, obj in ipairs(z.getObjects()) do
            if obj.type == "Deck" or obj.type == "Card" then
                currentPacks[p] = obj
                break
            end
        end
    end
    
    -- Check if packs are empty (i.e. round over)
    local allEmpty = true
    for _, p in ipairs(PLAYERS) do
        if currentPacks[p] then allEmpty = false end
    end
    
    if allEmpty then
        -- End of Round
        ROUND = ROUND + 1
        TOTAL_PACKS_OPENED = TOTAL_PACKS_OPENED + 3
        if ROUND > NUM_ROUNDS then
            endDraft()
        else
            dealRound()
        end
        return
    end
    
    -- Move packs to next player
    local nextP = {}
    if ROUND == 2 then
        nextP = {Red="Blue", Blue="Green", Green="Red"} -- Right
    else
        nextP = {Red="Green", Green="Blue", Blue="Red"} -- Left
    end
    
    for p, pack in pairs(currentPacks) do
        local targetP = nextP[p]
        local z = draftZones[targetP]
        local pos = z.getPosition()
        pos.y = pos.y + 1
        pack.setPositionSmooth(pos)
    end
    
    resetPassButtons()
    broadcastToAll("Packs passed " .. getPassDirection() .. ".", {0.8,0.8,0.8})
end

function resetPassButtons()
    passReady = {Red=false, Green=false, Blue=false}
    for _, obj in ipairs(getAllObjects()) do
        if obj.getName():match("^PassBtn_") then
            obj.editButton({index=0, label="Pass Pack", color={0.2, 0.6, 0.2}})
        end
    end
end

function endDraft()
    STATE = "POST_DRAFT"
    Global.UI.setAttribute("statusText", "text", "Draft Complete!")
    Global.UI.setAttribute("restartPanel", "active", "true")
    broadcastToAll("Draft is complete! Build your decks.", {1,1,0})
end

function continueDraft(player)
    ROUND = 1
    STATE = "DRAFTING"
    Global.UI.setAttribute("restartPanel", "active", "false")
    dealRound()
end

function restartDraft(player)
    -- Group all cards back to the master deck
    -- In a real scenario we'd script gathering them, but for now we prompt players
    broadcastToAll("Please drag all cards back into the master deck manually before starting a new set.", {1,0,0})
    Global.UI.setAttribute("restartPanel", "active", "false")
    Global.UI.setAttribute("setupPanel", "active", "true")
    Global.UI.setAttribute("statusPanel", "active", "false")
end
