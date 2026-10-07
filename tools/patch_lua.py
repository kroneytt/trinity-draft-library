import re

with open("tts/lua/Global.lua", "r", encoding="utf-8") as f:
    lua = f.read()

cleanup_code = """    local other_exp = (exp == "TD-01") and "TD-02" or "TD-01"
    for _, obj in ipairs(getAllObjects()) do
        local name = obj.getName()
        local notes = obj.getGMNotes() or ""
        if name:find("%(" .. other_exp .. "%)") or notes:find("master_pool_" .. other_exp) then
            obj.destruct()
        end
    end
"""

lua = lua.replace('    local deck = getMasterDeck(ACTIVE_EXPANSION)', cleanup_code + '\n    local deck = getMasterDeck(ACTIVE_EXPANSION)')

with open("tts/lua/Global.lua", "w", encoding="utf-8") as f:
    f.write(lua)
