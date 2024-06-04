import cv2
import json
import numpy as np
import pyautogui
import time

# load app config
with open('config.json', 'r') as config_file:
    config = json.load(config_file)


def is_far_enough(centers, new_center, min_distance=40):
    for center in centers:
        distance = np.sqrt((center[0] - new_center[0])**2 + (center[1] - new_center[1])**2)
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

            if all(is_far_enough(centers[type_b], center, config['detect']['safe_distance']) for type_b in config['detect']['types']):
                centers[type_p].append(center)

    return mask_layer


def click(center):
    screen_x = config['window']['left'] + center[0]
    screen_y = config['window']['top'] + center[1]
    pyautogui.click(screen_x, screen_y)


def render(image, centers, type_p='blum'):
    for center in centers[type_p]:
        cv2.circle(
            image,
            center,
            config['render'][type_p]['radius'],
            config['render'][type_p]['color'],
            -1
        )


def loop():
    screenshot = pyautogui.screenshot(region=tuple(config['window'].values()))
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
        layers[f"mask:{type_p}"] = mask(centers, hsv, type_p)

    # collect all blums
    if config['interact']:
        for center in centers['blum']:
            click(center)

    # render layers
    if len(config['render']['layers']):
        image = np.zeros((config['window']['height'], config['window']['width'], 3), np.uint8)

        for type_p in config['detect']['types']:
            render(image, centers, type_p)

        if 'centers' in config['render']['layers']:
            layers['centers'] = image

        for layer in layers.keys():
            cv2.imshow(layer, layers[layer])

    time.sleep(config['detect']['frequency'])


while True:
    loop()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()
