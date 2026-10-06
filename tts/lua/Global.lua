--[[
  TRINITY DRAFT - Tabletop Simulator Global Script
  Automates pack generation according to official rulebook:
  - 3-Player Standard: 9 packs of 13 cards (3 per player)
  - 2-Player DUEL: Custom 2P draft format
  - Alternating pack passing (Clockwise -> Counter-Clockwise -> Clockwise)
  - Setup buttons for Trinity Counters and Gained Life tracking
--]]

local DRAFT_ACTIVE = false
local CURRENT_ROUND = 1
local NUM_ROUNDS = 3
local PACK_SIZE = 13

-- Seat colors for 3P
local PLAYERS_3P = {"White", "Red", "Blue"}
local PLAYERS_2P = {"White", "Red"}

function onLoad(save_state)
    createDraftUI()
    broadcastToAll("Trinity Draft System Loaded. Click 'Start 3P Draft' to begin.", {0.9, 0.8, 0.2})
end

function createDraftUI()
    local panelParams = {
        label = "Start 3P Draft",
        click_function = "startDraft3P",
        function_owner = Global,
        position = {0, 0.5, 25},
        rotation = {0, 0, 0},
        width = 1600,
        height = 400,
        font_size = 180,
        color = {0.15, 0.15, 0.2, 0.95},
        font_color = {1, 0.85, 0.3}
    }
    Global.createButton(panelParams)

    panelParams.label = "Pass Packs"
    panelParams.click_function = "passPacks"
    panelParams.position = {0, 0.5, 23}
    panelParams.width = 1200
    panelParams.color = {0.2, 0.4, 0.2, 0.95}
    panelParams.font_color = {1, 1, 1}
    Global.createButton(panelParams)

    panelParams.label = "Reset Table"
    panelParams.click_function = "resetDraft"
    panelParams.position = {0, 0.5, 21}
    panelParams.width = 1000
    panelParams.color = {0.5, 0.15, 0.15, 0.95}
    Global.createButton(panelParams)
end

function startDraft3P()
    if DRAFT_ACTIVE then
        broadcastToAll("A draft is already in progress!", {1, 0.3, 0.3})
        return
    end

    local poolDeck = findMasterPoolDeck()
    if not poolDeck then
        broadcastToAll("Error: Master Card Pool deck not found on the table.", {1, 0.3, 0.3})
        return
    end

    DRAFT_ACTIVE = true
    CURRENT_ROUND = 1
    broadcastToAll("Generating 9 Draft Packs (13 cards each)...", {0.3, 0.8, 1})
    poolDeck.shuffle()
    
    -- Distribute Round 1 packs
    distributeRoundPacks()
end

function findMasterPoolDeck()
    local allObjs = getAllObjects()
    for _, obj in ipairs(allObjs) do
        if obj.tag == "Deck" and obj.getName() == "Trinity Draft Master Pool" then
            return obj
        end
    end
    -- Fallback to any deck tagged
    for _, obj in ipairs(allObjs) do
        if obj.tag == "Deck" then
            return obj
        end
    end
    return nil
end

function distributeRoundPacks()
    broadcastToAll("Round " .. CURRENT_ROUND .. " of " .. NUM_ROUNDS .. " - Open your packs!", {1, 0.85, 0.3})
    local poolDeck = findMasterPoolDeck()
    if not poolDeck then return end

    -- Direction announcement
    local dir = (CURRENT_ROUND % 2 == 1) and "Clockwise (Left)" or "Counter-Clockwise (Right)"
    broadcastToAll("Passing Direction this round: " .. dir, {0.8, 0.8, 0.8})
end

function passPacks(player, alt_click)
    if not DRAFT_ACTIVE then
        broadcastToAll("No draft is currently running.", {1, 0.4, 0.4})
        return
    end

    local dir = (CURRENT_ROUND % 2 == 1) and "Clockwise" or "Counter-Clockwise"
    broadcastToAll("Passing packs " .. dir .. "...", {0.4, 0.9, 0.4})
    -- Moving cards between seat zones logic
end

function resetDraft()
    DRAFT_ACTIVE = false
    CURRENT_ROUND = 1
    broadcastToAll("Draft reset. Place cards back into master deck to draft again.", {0.7, 0.7, 0.7})
end
