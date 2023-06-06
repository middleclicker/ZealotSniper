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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('zealot.log')
file_handler.setLevel(logging.DEBUG)

log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(log_format)

logger.addHandler(file_handler)
# logging.basicConfig(filename='zealot.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.DEBUG)

AIM_STEPS = 3
SPIN_STEPS = 2
CONFIDENCE_THRESHOLD = 0.7

logger.debug(f"Aim steps: {AIM_STEPS}")
logger.debug(f"Spin steps: {SPIN_STEPS}")
logger.debug(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")

def get_screen_resolution():
    monitor = get_monitors()[0]  # Assuming a single monitor setup
    width = monitor.width
    height = monitor.height
    return width, height

screen_width, screen_height = get_screen_resolution()
center_width = screen_width/2
center_height = screen_height/2

logger.debug(f"Screen width: {screen_width}")
logger.debug(f"Screen height: {screen_height}")
logger.debug(f"Center width: {center_width}")
logger.debug(f"Center height: {center_height}")

model = torch.hub.load('ultralytics/yolov5', 'custom', path='runs/train/exp/weights/best.pt')
model.cuda()

logger.info("Initialization finished")
logger.info("###############################")
logger.info("         Zealot Sniper         ")
logger.info("###############################")

def generate_vectors(target, num_steps):
    vectors = []
    current_vector = [0, 0]
    while num_steps > 0:
        xDist = target[0]-current_vector[0]
        yDist = target[1]-current_vector[1]
        if num_steps == 1:
            vectors.append([xDist, yDist])
            break
        x = random.uniform(xDist/(num_steps+1), yDist/(num_steps-1))
        y = random.uniform(xDist/(num_steps+1), yDist/(num_steps-1))
        current_vector[0] += x
        current_vector[1] += y
        vectors.append([x, y])
        num_steps -= 1

    return vectors

def doMouseMovement(zealot):
    target_x = zealot[0]
    target_y = zealot[1]+8 # 8 pixel offset from window border

    target_vector = [target_x-center_width, target_y-center_height]
    transitional_vectors = generate_vectors(target_vector, AIM_STEPS)
    for vector in transitional_vectors:
        py.move(vector[0], vector[1])

    logger.debug("Shot the scythe")
    py.click(button='right')

def spinAround():
    transitional_vectors = generate_vectors((-center_width, 0), SPIN_STEPS)
    for vector in transitional_vectors:
        py.move(vector[0], vector[1])

def calcDist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1-x2, 2) + math.pow(y1-y2, 2))

def runProgram(event):
    logger.info("Starting script")
    continuousNoDetection = 0
    py.keyDown('shift')
    py.keyDown('w')
    while True:
        if keyboard.is_pressed("r"): # Doesn't work for some reason. Move cursor to corner of screen (pyautogui failsafe) or CTRL-C
            sys.exit()
        im = ImageGrab.grab()
        results = model(im)
        results = results.pandas().xyxy[0]
        closestDist = 10000
        closestRow = {}
        for index, row in results.iterrows():
            if row['confidence'] < CONFIDENCE_THRESHOLD:
                continue
            centerX = (row['xmin']+row['xmax'])/2
            centerY = (row['ymin']+row['ymax'])/2
            currentDist = calcDist(centerX, centerY, center_width, center_height)
            if row['name'] == "SpecialZealot": # TODO: Make a second class for special zealots
                closestRow = row.to_dict()
                closestDist = currentDist
                break
            if currentDist < closestDist:
                closestRow = row.to_dict()
                closestDist = currentDist

        if not closestRow:
            if continuousNoDetection > 10:
                continuousNoDetection = 0
                logger.debug("No zealots found, spinning around")
                spinAround()
            else:
                continuousNoDetection += 1
            continue

        logger.debug(f"Closest row: {closestRow}")
        centerCoord = ((closestRow['xmin']+closestRow['xmax'])/2, (closestRow['ymin']+closestRow['ymax'])/2)
        doMouseMovement(centerCoord)
        logger.debug(f"Current Coordinate: {centerCoord}")
        logger.debug(f"Distance from last: {closestDist}")
        logger.debug("--------")

key_to_listen = "x"
keyboard.on_press_key(key_to_listen, runProgram)

keyboard.wait("r")
