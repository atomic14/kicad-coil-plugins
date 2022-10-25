[![Demo Video](https://img.youtube.com/vi/CDhlx_VMpCc/0.jpg)](https://www.youtube.com/watch?v=CDhlx_VMpCc)

# Getting set up

## Running the notebook locally

Make sure you have python3 installed. Then run the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

## Getting KiCad set up

Add the plugin to KiCad by symbolically linking it to the `kicad_plugins` directory.

```bash
ln -s ${PWD}/coil_plugin.py ~/Documents/KiCad/6.0/scripting/plugins/coil_plugin.py
```

## You can order the PCBs directly from PCBWay (or download the Gerbers) from these links

The project is still very experimental - so there are no guarantees that these will work or do anything useful...

* 6 circular coils - https://www.pcbway.com/project/shareproject/Proof_of_concept_6_coil_spiral_PCB_stator_23ae7370.html
* 6 wedge coils - https://www.pcbway.com/project/shareproject/Proof_of_concept_6_coil_wedge_PCB_stator_c231a379.html
* 12 wedge coils - https://www.pcbway.com/project/shareproject/Proof_of_concept_12_coil_wedge_PCB_stator_c54d9374.html
