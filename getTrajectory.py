# Name: TIAN Xiangan
# ITSC: xtianae
import copy
import cv2
import numpy as np
from sklearn.linear_model import LinearRegression
from math import sqrt
from getBullet import *

bulletSmallestSize = 0
bulletLargestSize = 10
speedLowThres = 200
speedHighThres = 900
class Trajectory:
    imgBuffer = []
    bulletBuffer = []
    direction = [0, 0]
    speed = 0

    def __init__(self, img, bullet):
        self.imgBuffer = []
        self.bulletBuffer = []
        self.direction = [0, 0]
        self.speed = 0
        self.imgBuffer.append(img)
        self.bulletBuffer.append(bullet)

    def addIB(self, img, bullet):
        self.imgBuffer.append(img)
        self.bulletBuffer.append(bullet)
    
    def setDirection(self, bul):
        if len(self.bulletBuffer) == 0:
            print("Some error occurred setting direction.")
            return
        x_diff = bul.coorX - self.bulletBuffer[0].coorX
        y_diff = bul.coorY - self.bulletBuffer[0].coorY
        self.direction = (x_diff, y_diff)
        self.speed = sqrt(x_diff**2 + y_diff**2)

    def compareSpeed(self, bul):
        x_diff = self.bulletBuffer[-1].coorX - bul.coorX
        y_diff = self.bulletBuffer[-1].coorY - bul.coorY
        speed = int(sqrt(x_diff**2 + y_diff**2))
        return (speedLowThres < speed < speedHighThres)
    
    def checkDirection(self, bul):
        if self.direction == [0, 0]:
            return 1
        x_diff = bul.coorX - self.bulletBuffer[-1].coorX
        y_diff = bul.coorY - self.bulletBuffer[-1].coorY
        divisor = sqrt((x_diff**2 + y_diff**2)*(self.direction[0]**2 + self.direction[1]**2))
        if divisor == 0:
            angle = 1
        else:
            angle =  (x_diff*self.direction[0] + y_diff*self.direction[1]) / divisor
        return angle

    def drawTrajectory(self, index):
        if self.imgBuffer[0] is None:
            print("Fail to generate image: none")
            return
        elif len(self.imgBuffer) < 1 or len(self.bulletBuffer) < 1:
            print("Some error occurred generating image.")
            return
        resultImg = self.imgBuffer[0]
        for i in range(1, len(self.imgBuffer)):
            if self.imgBuffer[i] is None:
                print("Fail to generate image: none")
                return 
            resultImg += self.imgBuffer[i]
        x_set = np.array([], dtype = float)
        y_set = np.array([], dtype = float)
        for i in range(len(self.bulletBuffer)):
            imgg = self.imgBuffer[i]
            lowMost = self.bulletBuffer[i].lowerBound
            if lowMost > imgHeight:
                lowMost = imgHeight
            upMost = self.bulletBuffer[i].upperBound
            if upMost < 0:
                upMost = 0
            leftMost = self.bulletBuffer[i].leftBound
            if leftMost < 0:
                leftMost = 0
            rightMost = self.bulletBuffer[i].rightBound
            if rightMost > imgWidth:
                rightMost = imgWidth
            for row in range(upMost, lowMost):
                for col in range(leftMost, rightMost):
                    if imgg[row][col].all() > 0:
                        x_set = np.append(x_set, col)
                        y_set = np.append(y_set, row)
        x_set = x_set.reshape(-1, 1)
        y_set = y_set.reshape(-1, 1)
        if len(x_set) == 0:
            print("No thing to regression")
            return
        regressor = LinearRegression().fit(x_set, y_set)  
        x1 = 0
        y1 = int(regressor.intercept_)
        x2 = 1280
        y2 = int(1280*regressor.coef_ + regressor.intercept_)
        cv2.line(resultImg, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.imwrite('interpolation%d.jpg' % index, resultImg)
        print("finished generating image %d" % index)

    