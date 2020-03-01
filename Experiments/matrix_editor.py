import cv2
import numpy
import copy

radius = 15     # Радиус пикселя
dim_x = 16      # Количество пикселей по горизонтали
dim_y = 16      # Количество пикселей по вертикали
brightness = 0.65   # Яркость пикселей

window_x = dim_x * radius * 2 + 150
window_y = dim_y * radius * 2 + 150
distance = radius * 2 + 2
x_mouse = 0
y_mouse = 0
matrix = []
color = (int(81 * brightness), int(177 * brightness), int(183 * brightness))
frame = numpy.zeros((window_y, window_x, 3), numpy.uint8)

file = open("matrix.txt", 'a')


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
                    cv2.imshow("frame", frame)
                    cv2.waitKey(1)


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
cv2.imshow("frame", frame)

key = -1
matrix_old = None

while key != 27:
    key = cv2.waitKey(0)
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

        print(string, end='')
        file.write(string)

file.close()
