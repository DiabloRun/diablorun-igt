# Diablo.run IGT
This tool tracks Diablo II: Resurrected loading screens and pauses LiveSplit game time if it detects one.

## Requirements
* [LiveSplit](http://livesplit.org/)
* [Server Component](https://github.com/LiveSplit/LiveSplit.Server/releases/download/1.8/LiveSplit.Server_1.8.zip) for LiveSplit

## Guide
### Setting up LiveSplit
1. Install LiveSplit [Server Component](https://github.com/LiveSplit/LiveSplit.Server/releases/download/1.8/LiveSplit.Server_1.8.zip).
2. Extract the files and add the two .dll files to your LiveSplit\Components folder.
3. Edit LiveSplit layout and **Add** > **Control** > **LiveSplit Server**.
4. Save layout and right click LiveSplit > **Control** > **Start Server**.
5. Make sure you have a timer that tracks "game time".

### Setting up Diablo.run IGT
1. [Download latest release](https://github.com/DiabloRun/diablorun-igt/releases/tag/21.10.15-pre2)
2. Run diablorun-igt.exe

Everything is setup! Launch the game, start the timer and see if it pauses correctly during loading screens.
