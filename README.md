# Pendot L

Pendot L is a prototype font for writing education in the Latin script. It is incomplete and will change considerably. Please do not use this as a source of derivatives. A much more useful font will eventually be released that will be a better source. Thank you!


## Minimal setup

On Ubuntu/macOS you need:

- a recent version python3 to handle the virtual environment (3.10+)
- other python3 dependencies will be installed via the Makefile calling the requirements.txt
- GNU make to run the Makefile
- ``sudo apt install make automake``  for Ubuntu
- ``brew install make`` for macOS

The CI (GitHub Action) installs ttfautohint

## Build steps

``make build`` : Builds the fonts and places them in the fonts/ directory

``make test`` : Runs Fontbakery tests and generates reports in md and html in out/fontbakery

``make clean`` : Removes generated files from the build, including the virtual environment folder(s)

``make images`` : Generates drawbot proof image(s)

