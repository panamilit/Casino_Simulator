# CASINO SIMULATOR (Python)

# Author: panamilit

Pixel-style casino simulator.

Includes Coin Flip game with:
- Manual play
- Flat bet simulation
- Martingale simulation

UI built with Tkinter + PNG assets + background music.

## Features
- Player profile (name + balance)
- Shared balance across modes
- Logs panel + export logs
- Settings popup (music volume, export logs)
- Pixel-art interface + soundtrack

## Tech stack
- Python 3.11+
- Tkinter (built-in)
- Pillow (image loading)
- pygame (music)

## Project structure

casino_simulator/
    casino/
        __init__.py
        player.py
        games.py
        simulation.py
    assets/
        fonts/
            PixelifySans-VariableFont_wght
        *.png
        *.mp3
    main_ui.py
    main.py
    requirements.txt
    README.md



## Installation (Windows / PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main_ui.py
 ```


## Controls

Manual: play one round at a time
Flat bet / Martingale: runs animated simulation step-by-step

Settings: volume slider + export logs


## Roadmap (future updates)

- Roulette (red/black)
- Slots
- Statistics screen
- Better animations (coin flip frames)