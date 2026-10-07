import re

with open("tts/lua/Global.lua", "r", encoding="utf-8") as f:
    lua = f.read()

new_xml = """    <Defaults>
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
    </Panel>"""

# We need to replace everything between Global.UI.setXml(\n    [[\n and \n    ]]\n    )
lua = re.sub(r'Global\.UI\.setXml\(\s*\[\[.*?\]\]\s*\)', f'Global.UI.setXml(\n    [[\n{new_xml}\n    ]]\n    )', lua, flags=re.DOTALL)

with open("tts/lua/Global.lua", "w", encoding="utf-8") as f:
    f.write(lua)

print("Fixed UI in Global.lua")
