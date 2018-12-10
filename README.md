# Eggbot

This repo will contain files for creating your own eggbot and controlling it.

## Usage

### Hardware

1. Build the eggbot
2. Program it with GRBL

### Software

#### Create a .gcode file
Create a .gcode file using the Inkscape plugin *Gcodetool*. See [this link](https://www.norwegiancreations.com/2015/08/an-intro-to-g-code-and-how-to-generate-it-using-inkscape/) for an example how to do it.

#### Convert the .gcode file to Eggbot-compatible format
To convert a .gcode file *design.gcode* for usage with the eggbot, pass it through the converter *eggbot_gconvert.py*:
```bash
python3 eggbot_gconvert.py design.gcode
```

This creates a file with the name *design.eggbot.gcode*.

#### Send the Eggbot-compatible file to the Eggbot controller
This requires some software that talks over serial port with the GRBL controller in the Eggbot. A common tool that works well is the [Universal Gcode Sender](https://github.com/winder/Universal-G-Code-Sender).