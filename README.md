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
