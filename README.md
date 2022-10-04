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

This is a bit of a pain as KiCad comes with its own python installation. You'll need to install any required dependencies into this installation.

```bash
cd /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin
./pip3 install numpy scikit-spatial
```

You can now link any plugins that you want to make available to KiCad by symbolic linking them into the `kicad_plugins` directory.

```bash
ln -s ${PWD}/coil_plugin_v2.py ~/Documents/KiCad/6.0/scripting/plugins/coil_plugin_v2.py
```
