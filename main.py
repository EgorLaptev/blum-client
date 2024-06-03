import pyautogui
import cv2
import numpy as np
from PIL import Image
import time

left = 0 # x координата верхнего левого угла области
top = 100 # y координата верхнего левого угла области
width = 600  # ширина области
height = 850 # высота области

def is_far_enough(centers, new_center, min_distance=40):
    for center in centers:
        distance = np.sqrt((center[0] - new_center[0])**2 + (center[1] - new_center[1])**2)
        if distance < min_distance:
            return False
    return True

def draw_center(contours, image, color):
    for contour in contours:
        # Момент контура
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cX = int(M['m10'] / M['m00'])
            cY = int(M['m01'] / M['m00'])

            new_center = (cX, cY)

            # Проверка, находится ли новый центр на достаточном расстоянии от других центров
            if is_far_enough(centers, new_center):
                centers.append(new_center)
                # Рисование центра на изображении
                cv2.circle(image, new_center, 5, color, -1)

def blum_mask(image):
    lower_color = np.array([40, 100, 100])
    upper_color = np.array([80, 255, 255])

    mask = cv2.inRange(hsv, lower_color, upper_color)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    draw_center(contours, image, (0, 255, 0))

def bomb_mask(image):
    pass
    # lower_color = np.array([9,0,0])
    # upper_color = np.array([175,52,255])
    #
    # mask = cv2.inRange(hsv, lower_color, upper_color)
    # contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #
    # draw_center(contours, image, (0, 0, 255))

def froze_mask():
    pass

def mouse_click(center):
   screen_x = left + center[0]
   screen_y = top + center[1]
   pyautogui.click(screen_x, screen_y)

while True:
    # Захват области экрана
    screenshot = pyautogui.screenshot(region=(left, top, width, height))

    # Преобразование изображения из формата PIL в формат OpenCV
    open_cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Преобразование изображения в цветовое пространство HSV
    hsv = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2HSV)
    #
    image = np.zeros((height, width, 3), np.uint8)

    centers = []

    blum_mask(image)
    bomb_mask(image)

    # for center in centers:
    #     mouse_click(center)

    # time.sleep(1)

    # Отображение результата (для отладки)
    cv2.imshow('Musks', image)

    # Закрытие окна при нажатии на любую клавишу
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# cv2.destroyAllWindows()
