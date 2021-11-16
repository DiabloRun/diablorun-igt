# Diablo.run IGT

This tool tracks Diablo II: Resurrected loading screens and pauses LiveSplit game time if it detects one.

## Requirements

- [LiveSplit](http://livesplit.org/)
- [Server Component](https://github.com/LiveSplit/LiveSplit.Server/releases/download/1.8/LiveSplit.Server_1.8.zip) for LiveSplit

## Guide

### Setting up LiveSplit

1. Install LiveSplit [Server Component](https://github.com/LiveSplit/LiveSplit.Server/releases/download/1.8/LiveSplit.Server_1.8.zip).
2. Extract the files and add the two .dll files to your LiveSplit\Components folder.
3. Edit LiveSplit layout and **Add** > **Control** > **LiveSplit Server**.
4. Save layout and right click LiveSplit > **Control** > **Start Server**.
5. Make sure you have a timer that tracks "game time".

### Setting up Diablo.run IGT

1. [Download latest release](https://github.com/DiabloRun/diablorun-igt/releases)
2. Run diablorun-igt.exe

Everything is setup! Launch the game, start the timer and see if it pauses correctly during loading screens. Note that you need to click "Start Server" through LiveSplit every time you open it. It doesn't start automatically.

## Development

Currently only Windows is supported as the win32 API is used to capture the screen.

1. Create a virtualenv - eg `python -m venv .venv`
2. Install dependencies using `pip install -r requirements.txt`
3. Run tests using `python test.py`
4. Run the program using `python main.py`
5. Build using pyinstaller - eg `pyinstaller --noconsole main.py`
