import cv2
import json
import numpy as np
import time
import pyautogui
import sys

# sys.tracebacklimit = 0

# load app config
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

pyautogui.PAUSE = config['detect']['click_frequency']


def is_far_enough(centers, new_center, min_distance=40):
    for center in centers:
        distance = np.sqrt((center[0] - new_center[0]) ** 2 + (center[1] - new_center[1]) ** 2)
        if distance < min_distance:
            return False
    return True


def mask(centers, hsv, type_p='blum'):
    mask_layer = cv2.inRange(
        hsv,
        tuple(config['detect']["hsv"][type_p]['lower']),
        tuple(config['detect']["hsv"][type_p]['upper'])
    )

    contours, _ = cv2.findContours(mask_layer, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < config['detect']['minimal_area']:
            continue

        M = cv2.moments(contour)
        if M['m00'] != 0:
            cX = int(M['m10'] / M['m00'])
            cY = int(M['m01'] / M['m00'])

            center = (cX, cY)

            if is_far_enough(centers['bomb'], center, config['detect']['safe_distance']):
                if config['interact'] and type_p == 'blum':
                    click(center)
                centers[type_p].append(center)

            if type_p == 'bomb':
                centers['blum'] = [center for center in centers['blum'] if
                                   is_far_enough(centers['bomb'], center, config['detect']['safe_distance'])]
                centers['ice'] = [center for center in centers['ice'] if
                                  is_far_enough(centers['bomb'], center, config['detect']['safe_distance'])]

    return mask_layer


def click(center):
    screen_x = config['window']['left'] + center[0]
    screen_y = config['window']['top'] + center[1]
    pyautogui.click(screen_x, screen_y + 30)
    # pyautogui.moveTo(screen_x, screen_y+30, duration=0)


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
    screenshot = pyautogui.screenshot(
        region=(blum_window.left + 30, blum_window.top + 100, blum_window.width - 60, blum_window.height - 260))

    return screenshot


def loop():
    screenshot = autocrop() if config['autoCrop'] else pyautogui.screenshot(region=tuple(config['window'].values()))

    if not screenshot:
        raise Exception('screenshot not received')

    open_cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2HSV)

    centers = {
        'blum': [],
        'bomb': [],
        'ice': []
    }

    layers = {}

    if 'screenshot' in config['render']['layers']:
        layers['screenshot'] = open_cv_image

    # detect all particles
    for type_p in config['detect']['types']:
        mask_layer = mask(centers, hsv, type_p)
        if f"mask:{type_p}" in config['render']['layers']:
            layers[f"mask:{type_p}"] = mask_layer

    # render layers
    if len(config['render']['layers']):
        image = np.zeros((config['window']['height'], config['window']['width'], 3), np.uint8)

        for type_p in config['detect']['types']:
            render(image, centers, type_p)

        if 'centers' in config['render']['layers']:
            layers['centers'] = image

        for layer in layers.keys():
            cv2.imshow(layer, layers[layer])

    if config['detect']['frame_frequency'] > 0:
        time.sleep(config['detect']['frame_frequency'])


while True:
    loop()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
