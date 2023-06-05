import torch
import pandas
from PIL import ImageGrab
import keyboard
from screeninfo import get_monitors
import random
import time
import pyautogui as py
import numpy as np
import sys
import math

AIM_STEPS = 3
SPIN_STEPS = 2

def get_screen_resolution():
    monitor = get_monitors()[0]  # Assuming a single monitor setup
    width = monitor.width
    height = monitor.height
    return width, height

screen_width, screen_height = get_screen_resolution()
print("Screen Width:", screen_width)
print("Screen Height:", screen_height)

center_width = screen_width/2
center_height = screen_height/2

model = torch.hub.load('ultralytics/yolov5', 'custom', path='runs/train/exp/weights/best.pt')
model.cuda()

def generate_vectors(target, num_steps):
    vectors = []
    current_vector = [0, 0]
    while num_steps > 0:
        if num_steps == 1:
            vectors.append([target[0]-current_vector[0], target[1]-current_vector[1]])
            break
        x = random.uniform((target[0]-current_vector[0])/(num_steps+1), (target[0]-current_vector[0])/(num_steps-1))
        y = random.uniform((target[1]-current_vector[1])/(num_steps+1), (target[1]-current_vector[1])/(num_steps-1))
        current_vector[0] += x
        current_vector[1] += y
        vectors.append([x, y])
        num_steps -= 1

    return vectors

def doMouseMovement(zealot):
    target_x = zealot[0]
    target_y = zealot[1]+8 # 8 pixel offset
    target_vector = [0, 0]
    target_vector[0] = target_x-center_width
    target_vector[1] = target_y-center_height

    transitional_vectors = generate_vectors(target_vector, AIM_STEPS)
    for vector in transitional_vectors:
        py.move(vector[0], vector[1])

    py.click(button='right')

def spinAround():
    transitional_vectors = generate_vectors((-center_width, 0), SPIN_STEPS)
    for vector in transitional_vectors:
        py.move(vector[0], vector[1])

def runProgram(event):
    lastCoord = (center_width, center_height)
    continuousNoDetection = 0
    py.keyDown('shift')
    py.keyDown('w')
    while True:
        if keyboard.is_pressed("r"):
            sys.exit()
        print("--------")
        im = ImageGrab.grab()
        results = model(im)
        results = results.pandas().xyxy[0]
        closestDist = 10000
        closestRow = {}
        for index, row in results.iterrows():
            if row['confidence'] >= 0.7:
                currentDist = math.sqrt(math.pow((row['xmin']+row['xmax'])/2-center_width, 2) + math.pow((row['ymin']+row['ymax'])/2-center_height, 2))
                if currentDist < closestDist:
                    print(row)
                    closestRow = row.to_dict()
                    closestDist = currentDist

        if not closestRow:
            print("Skipped because of low confidence value")
            if continuousNoDetection > 10:
                continuousNoDetection = 0
                spinAround()
            else:
                continuousNoDetection += 1
            continue

        print(closestRow)
        doMouseMovement(((closestRow['xmin']+closestRow['xmax'])/2, (closestRow['ymin']+closestRow['ymax'])/2))
        lastCoord = ((closestRow['xmin']+closestRow['xmax'])/2, (closestRow['ymin']+closestRow['ymax'])/2)
        print("Current Coordinate: ", lastCoord)
        print("Distance from last: ", closestDist)

key_to_listen = "x"
keyboard.on_press_key(key_to_listen, runProgram)

keyboard.wait("r")
