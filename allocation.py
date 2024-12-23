import cv2
import numpy as np
import random
import matplotlib.pyplot as plt


def image_to_points(image, uav_total_num, dx, w=512, h=512):

    # to gray
    image = cv2.resize(image, (w, h))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # gaussian filter
    kernel_size = (11, 11)
    sigma_x = 0
    gray = cv2.GaussianBlur(gray, kernel_size, sigma_x)

    # normalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(3, 3))
    gray = clahe.apply(gray)

    # binary
    _, binary = cv2.threshold(gray, min([int(np.mean(gray) * 1.5), 150]), 255, cv2.THRESH_BINARY)

    # remove tiny lines
    kernel = np.ones((5, 5), np.uint8)
    binary = cv2.erode(binary, kernel, iterations=1)
    binary = cv2.dilate(binary, kernel, iterations=1)

    # concave convex
    ori = binary
    uav_num = np.sum((ori == 0).astype(int))
    # if 2 * uav_num > w * h:
    #     ori = 255 - ori
    #     uav_num = np.sum((ori == 0).astype(int))

    # reshape to fit uav_total_num
    rate = (uav_total_num / uav_num) ** 0.5
    binary = cv2.resize(ori, (int(rate * w + 0.5), int(rate * h + 0.5)))
    uav_num = np.sum((binary == 0).astype(int))
    while uav_num < uav_total_num:
        h, w = binary.shape
        rate = (uav_total_num / uav_num) ** 0.5
        binary = cv2.resize(ori, (int(rate * w + 3), int(rate * h + 3)))
        uav_num = np.sum((binary == 0).astype(int))

    # randomly drop UAVs
    h, w = binary.shape
    binary = binary.reshape([-1])
    lst = np.nonzero(binary == 0)[0].tolist()
    idxs = random.sample(lst, uav_num - uav_total_num)
    binary[idxs] = 255
    binary = binary.reshape([h, w])

    # get uav positions
    points = []
    for i in range(h):
        for j in range(w):
            if binary[i, j] == 0:
                points.append([j, h - i])
    points = np.array(points).astype(float)[:uav_total_num]
    points *= dx
    points -= np.min(points, axis=0, keepdims=True)

    return points[:uav_total_num]


if __name__ == '__main__':

    image_path = r"C:\Users\Dell\Desktop\dt\cpp\pkq.png"
    image = cv2.imread(image_path)
    image = np.array(image)        # h, w, 3

    uav_total_num = 450
    dx = 2.

    points = image_to_points(image, uav_total_num, dx)

    plt.scatter(points[:, 0], points[:, 1], s=1.)
    plt.show()


