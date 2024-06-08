import cv2
import json
import numpy as np
import time
import pyautogui
import keyboard
import os
import sys
from AutoRemoveList import AutoRemoveList

# load app config
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

pyautogui.PAUSE = config['detect']['click_frequency']
pause = False

banned_space = AutoRemoveList(delay=config['detect']['banned_time'])


def is_far_enough(centers, new_center, min_distance=40):
    for center in centers:
        distance = np.sqrt((center[0] - new_center[0]) ** 2 + (center[1] - new_center[1]) ** 2)
        if distance < min_distance:
            return False
    return True


def mask(centers, hsv, type_p='blum', left=0, top=0):
    mask_layer = cv2.inRange(
        hsv,
        tuple(config['detect']["hsv"][type_p]['lower']),
        tuple(config['detect']["hsv"][type_p]['upper'])
    )

    contours, _ = cv2.findContours(mask_layer, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        contour_size = cv2.contourArea(contour)

        if contour_size < config['detect']['minimal_area']:
            continue

        M = cv2.moments(contour)
        if M['m00'] != 0:
            cX = int(M['m10'] / M['m00'])
            cY = int(M['m01'] / M['m00'])

            center = (cX, cY)

            if type_p == 'replay' and contour_size > 2000:
                centers[type_p].append(center)
                click(center, left, top)
                continue

            if is_far_enough(centers['bomb'], center, config['detect']['safe_distance']) and is_far_enough(banned_space.get(), center, config['detect']['banned_space']):
                if config['interact'] and type_p == 'blum':
                    click(center, left, top)
                centers[type_p].append(center)

            if type_p == 'bomb':
                centers['blum'] = [center for center in centers['blum'] if
                                   is_far_enough(centers['bomb'], center, config['detect']['safe_distance'])]
                centers['ice'] = [center for center in centers['ice'] if
                                  is_far_enough(centers['bomb'], center, config['detect']['safe_distance'])]
                if contour_size > 1000:
                    centers[type_p].append(center)

    return mask_layer


def click(center, left, top):
    screen_x = left + center[0]
    screen_y = top + center[1]

    banned_space.add((screen_x, screen_y))

    pyautogui.click(screen_x, screen_y + config['detect']['click_offset'])
    # pyautogui.moveTo(screen_x, screen_y+config['detect']['click_offset'], duration=0)


def render(image, centers, type_p='blum'):
    for center in centers[type_p]:
        cv2.circle(
            image,
            center,
            config['render'][type_p]['radius'],
            config['render'][type_p]['color'],
            -1
        )


def autocrop():
    tg_windows = pyautogui.getWindowsWithTitle("TelegramDesktop")

    if len(tg_windows) > 1:
        raise Exception('[AutoCropError] close all telegram windows except blum game')
    if len(tg_windows) == 0:
        raise Exception('[AutoCropError] open blum game')

    blum_window = tg_windows[0]

    return (blum_window.left, blum_window.top + 200, blum_window.width, blum_window.height)


def loop():
    left, top, width, height = autocrop() if config['autoCrop'] else tuple(config['window'].values())

    screenshot = pyautogui.screenshot(region=(left, top, width, height))

    open_cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2HSV)

    centers = {
        'blum': [],
        'bomb': [],
        'ice': [],
        'replay': []
    }

    layers = {}

    if 'screenshot' in config['render']['layers']:
        layers['screenshot'] = open_cv_image

    # detect all particles
    for type_p in config['detect']['types']:
        mask_layer = mask(centers, hsv, type_p, left, top)
        if f"mask:{type_p}" in config['render']['layers']:
            layers[f"mask:{type_p}"] = mask_layer

    # render layers
    if len(config['render']['layers']):
        image = np.zeros((height, width, 3), np.uint8)

        for type_p in config['detect']['types']:
            render(image, centers, type_p)

        if 'centers' in config['render']['layers']:
            layers['centers'] = image

        for layer in layers.keys():
            cv2.imshow(layer, layers[layer])

    if config['detect']['frame_frequency'] > 0:
        time.sleep(config['detect']['frame_frequency'])


while True:
    if not pause:
        loop()

    cv2.waitKey(1) & 0xFF

    # pause script
    if keyboard.is_pressed('p'):
        print("PAUSE")
        pause = not pause
        time.sleep(0.5)

    # stop script
    if keyboard.is_pressed('q'):
        cv2.destroyAllWindows()
        break

    # restart script
    if keyboard.is_pressed('r'):
        cv2.destroyAllWindows()
        os.execv(sys.executable, ['python'] + sys.argv)
