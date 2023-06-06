# Zealot Sniper

Snipes zealots for you with frozen scythe in hypixel skyblock with computer vision.

## Installation

Install YOLOv5's dependencies
```bash
pip install -r requirements.txt
```
Install any of these if they are not present
```python
import torch
import pandas
from PIL import ImageGrab
import keyboard
from screeninfo import get_monitors
import random
import pyautogui as py
import sys
import math
import logging
```
(e.g.) `pip install pyautogui`

## Usage
Set the window to fullscreen
```bash
python run.py
```
If there are zealots on screen, the script will shoot

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License
Check [LICENSE](LICENSE) for more info
