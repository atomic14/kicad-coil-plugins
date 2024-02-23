Traceback (most recent call last):

File "/Users/dspeith/Documents/KiCad/7.0/scripting/plugins/coil_plugin.py", line 146, in Run
# pcb_txt.Rotate(pcbnew.VECTOR2I_MM(x, y), text["angle"])

File "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/pcbnew.py", line 9262, in Rotate
return _pcbnew.BOARD_ITEM_Rotate(self, aRotCentre, aAngle)

TypeError: in method 'BOARD_ITEM_Rotate', argument 3 of type 'EDA_ANGLE const &'




--------



Traceback (most recent call last):

File "/Users/dspeith/Documents/KiCad/7.0/scripting/plugins/coil_plugin.py", line 146, in Run
pcb_txt.Rotate(pcbnew.VECTOR2I_MM(x, y), text["angle"])

File "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/pcbnew.py", line 9262, in Rotate
return _pcbnew.BOARD_ITEM_Rotate(self, aRotCentre, aAngle)

TypeError: in method 'BOARD_ITEM_Rotate', argument 3 of type 'EDA_ANGLE const &'




Traceback (most recent call last):

File "/Users/dspeith/Documents/KiCad/7.0/scripting/plugins/coil_plugin.py", line 149, in Run
text["size"] * pcbnew.IU_PER_MM,

AttributeError: module 'pcbnew' has no attribute 'IU_PER_MM'

Traceback (most recent call last):

File "/Users/dspeith/Documents/KiCad/7.0/scripting/plugins/coil_plugin.py", line 149, in Run
text["size"] * pcbnew.EDA_IU_SCALE.IU_PER_MM,

AttributeError: module 'pcbnew' has no attribute 'IU_PER_MM'



Traceback (most recent call last):

File "/Users/dspeith/Documents/KiCad/7.0/scripting/plugins/coil_plugin.py", line 147, in Run
pcb_txt.SetTextSize(

File "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/pcbnew.py", line 2772, in SetTextSize
return _pcbnew.EDA_TEXT_SetTextSize(self, aNewSize)

TypeError: in method 'EDA_TEXT_SetTextSize', argument 2 of type 'VECTOR2I const &'

