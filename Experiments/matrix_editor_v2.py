import cv2
import numpy
import copy
from termcolor import colored
import time
import random

radius = 15  # Радиус пикселя
dim_x = 16  # Количество пикселей по горизонтали
dim_y = 16  # Количество пикселей по вертикали
brightness = 0.65  # Яркость пикселей
delay = 300

window_x = dim_x * radius * 2 + 150
window_y = dim_y * radius * 2 + 150
distance = radius * 2 + 2
x_mouse = 0
y_mouse = 0
matrix = []
color = (int(81 * brightness), int(177 * brightness), int(183 * brightness))
frame = numpy.zeros((window_y, window_x, 3), numpy.uint8)
black = numpy.zeros((window_y, 100, 3), numpy.uint8)
cv2.rectangle(black, (0, 0), (99, window_y - 1), (0, 0, 0), max(window_x, window_y))

file = open("matrix.txt", 'a')

key = -1
matrix_old = None
animation = []


def select_point(event, x, y, flags, param):
    global frame, radius, distance
    if event == cv2.EVENT_LBUTTONDOWN:
        for i in range(dim_y):
            for j in range(dim_x):
                if (x - (j * distance + int((window_x - distance * dim_x) / 2) + radius)) ** 2 + (
                        y - (i * distance + int((window_y - distance * dim_y) / 2) + radius)) ** 2 <= radius ** 2:
                    matrix[i][j] = 1 - matrix[i][j]
                    if matrix[i][j] == 1:
                        cv2.circle(frame, ((j * distance + int((window_x - distance * dim_x) / 2) + radius),
                                           (i * distance + int((window_y - distance * dim_y) / 2) + radius)),
                                   int(radius / 2),
                                   (255, 255, 255), radius)
                    else:
                        cv2.circle(frame, ((j * distance + int((window_x - distance * dim_x) / 2) + radius),
                                           (i * distance + int((window_y - distance * dim_y) / 2) + radius)),
                                   int(radius / 2),
                                   color, radius)
                    cv2.imshow("frame", numpy.hstack([frame, black, frame]))
                    cv2.waitKey(1)


def save():
    global matrix, matrix_old, file
    if matrix != matrix_old:
        matrix_old = copy.deepcopy(matrix)
        string = "{"
        for i in range(len(matrix) - 1):
            string += "{"
            for j in range(len(matrix[i]) - 1):
                string += str(matrix[i][j]) + " ,"
            string += str(matrix[i][len(matrix[i]) - 1])
            string += '}, '
        i = len(matrix) - 1
        string += '{'
        for j in range(len(matrix[i]) - 1):
            string += str(matrix[i][j]) + " ,"
        string += str(matrix[i][len(matrix[i]) - 1])
        string += '}}\n'

        # print(string, end='')
        file.write(string)
        print(colored("SAVED", "green"))
    else:
        print(colored("ALREADY SAVED", "red"))


def draw():
    global animation, delay, dim_x, dim_y, distance, window_x, window_y, radius, frame, color, black
    while True:
        if len(animation) > 0:
            for an in animation:
                for i in range(dim_y):
                    for j in range(dim_x):
                        if an[i][j] == 0:
                            cv2.circle(frame,
                                       ((j * distance + int((window_x - distance * dim_x) / 2) + radius),
                                        (i * distance + int((window_y - distance * dim_y) / 2) + radius)),
                                       int(radius / 2), color, radius)
                        else:
                            cv2.circle(frame,
                                       ((j * distance + int((window_x - distance * dim_x) / 2) + radius),
                                        (i * distance + int((window_y - distance * dim_y) / 2) + radius)),
                                       int(radius / 2), (255, 255, 255), radius)
                cv2.imshow("frame", numpy.hstack([frame, black, frame]))
                ttt = time.time()
                while (time.time() - ttt) < delay / 1000:
                    if cv2.waitKey(1) == 112:
                        return 0


def animation_save():
    global animation, delay
    name = "animation" + str(int(random.random() * 1000)) + ".txt"
    out = open(name, 'w')
    for a in animation:
        string = "{"
        for i in range(len(a) - 1):
            string += "{"
            for j in range(len(a[i]) - 1):
                string += str(a[i][j]) + " ,"
            string += str(a[i][len(a[i]) - 1])
            string += '}, '
        i = len(a) - 1
        string += '{'
        for j in range(len(a[i]) - 1):
            string += str(a[i][j]) + " ,"
        string += str(a[i][len(a[i]) - 1])
        string += '}}\n'
        out.write(string)
    out.write(str(delay))
    out.close()
    print(colored("SAVED", "green"))


cv2.rectangle(frame, (0, 0), (window_x - 1, window_y - 1), (0, 0, 0), max(window_x, window_y))

for i in range(dim_y):
    matrix.append([])
    for j in range(dim_x):
        cv2.circle(frame,
                   ((j * distance + int((window_x - distance * dim_x) / 2) + radius),
                    (i * distance + int((window_y - distance * dim_y) / 2) + radius)),
                   int(radius / 2), color, radius)
        matrix[i].append(0)

cv2.namedWindow("frame")

cv2.setMouseCallback('frame', select_point)
cv2.imshow("frame", numpy.hstack([frame, black, frame]))
mode = 0

while key != 27:
    key = cv2.waitKey(0)
    if key == 115:
        save()
    elif key == 32:
        if mode == 0:
            print(colored("Animation mode ON", "green"))
            mode = 1
        else:
            print(colored("SAVE? (y/n/cancel)", "green"))
            ch = input()
            if ch == "y":
                animation_save()
                animation = []
                print(colored("SAVED. Animation mode OFF", "green"))
                mode = 0
            elif ch == "n":
                print(colored("Animation mode OFF", "red"))
                animation = []
                mode = 0
            else:
                print(colored("SAVING ABORTED. Animation mode ON", "red"))
    if mode == 1:
        if key == 97:
            animation.append(copy.deepcopy(matrix))
            print(colored("IMAGE ADDED", "green"))
        elif key == 112:
            print(colored("START ANIMATION", "green"))
            draw()
            print(colored("STOP ANIMATION", "red"))
        elif key == 116:
            print(colored("ENTER NEW TIME DELAY:", "red"))
            try:
                delay = int(input())
                print(colored("OK", "green"))
            except:
                print(colored("ERROR", "red"))
    # print(key)
    # s 115     save
    # space  32  animation mode on/off
    # p 112     play
    # a 97      add
    # t 116     time


    # S - Сохранить текущую картинку в общий файл (независимо от режима)
    # Пробел - войти в режим создания анимации. Выход этой же клавишей. При выходе требуется ввести
    # "y" если нужно сохранить анимацию в отдельный файл, "n" если нужно выйти из режима анимации без сохранения,
    # любой другой символ - прожолжить редактирование
    # A - Добавить текущую картинку в конец анимации. Удаление или редактирование не предусмотрено
    # P - проиграть анимацию. Остановка только по нажатию этой же клавиши
    # T - Изменить скорость анимации. Ввод в консоль задержки между кадрами в миллисекундах

file.close()
