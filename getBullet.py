# Name: TIAN Xiangan
# ITSC: xtianae
import cv2
import numpy as np
from math import sqrt

lowerThres = np.array([65, 50, 120])
upperThres = np.array([95, 210, 255])
thres = 5
imgWidth = 1280   # Width is len(img[0])
imgHeight = 1024  # Height is len(img)
windowWidth = int(imgWidth / 20)
windowHeight = int(imgHeight / 64)
bulletSmallestSize = 0
bulletLargestSize = 10

class Bullet:
    coorX = 0
    coorY = 0
    upperBound = 0
    lowerBound = 0
    leftBound = 0
    rightBound = 0
    blocks = []

    def __init__(self, blocks):
        self.blocks = []
        self.changeBound(blocks[0][0], blocks[0][1], 0, blocks)

    def changeBound(self, x, y, dir, blocks):
        if [x, y] in blocks:
            blocks.remove([x, y])
            self.blocks.append([x, y])
            if dir == 0:
                self.upperBound = y - windowHeight
                self.lowerBound = y + windowHeight
                self.leftBound = x - windowWidth
                self.rightBound = x + windowWidth
                self.changeBound(x, y - windowHeight, 1, blocks)
                self.changeBound(x, y + windowHeight, 2, blocks)
                self.changeBound(x - windowWidth, y, 3, blocks)
                self.changeBound(x + windowWidth, y, 4, blocks)
            elif dir == 1:
                if y - windowHeight < self.upperBound:
                    self.upperBound = y - windowHeight
                if y + windowHeight > self.lowerBound:
                    self.lowerBound = y + windowHeight
                if x - windowWidth < self.leftBound:
                    self.leftBound = x - windowWidth
                if x + windowWidth > self.rightBound:
                    self.rightBound = x + windowWidth
                self.changeBound(x, y - windowHeight, 1, blocks)
                self.changeBound(x - windowWidth, y, 3, blocks)
                self.changeBound(x + windowWidth, y, 4, blocks)
            elif dir == 2:
                if y - windowHeight < self.upperBound:
                    self.upperBound = y - windowHeight
                if y + windowHeight > self.lowerBound:
                    self.lowerBound = y + windowHeight
                if x - windowWidth < self.leftBound:
                    self.leftBound = x - windowWidth
                if x + windowWidth > self.rightBound:
                    self.rightBound = x + windowWidth
                self.changeBound(x, y + windowHeight, 2, blocks)
                self.changeBound(x - windowWidth, y, 3, blocks)
                self.changeBound(x + windowWidth, y, 4, blocks)
            elif dir == 3:
                if y - windowHeight < self.upperBound:
                    self.upperBound = y - windowHeight
                if y + windowHeight > self.lowerBound:
                    self.lowerBound = y + windowHeight
                if x - windowWidth < self.leftBound:
                    self.leftBound = x - windowWidth
                if x + windowWidth > self.rightBound:
                    self.rightBound = x + windowWidth
                self.changeBound(x, y - windowHeight, 1, blocks)
                self.changeBound(x, y + windowHeight, 2, blocks)
                self.changeBound(x - windowWidth, y, 3, blocks)
            elif dir == 4:
                if y - windowHeight < self.upperBound:
                    self.upperBound = y - windowHeight
                if y + windowHeight > self.lowerBound:
                    self.lowerBound = y + windowHeight
                if x - windowWidth < self.leftBound:
                    self.leftBound = x - windowWidth
                if x + windowWidth > self.rightBound:
                    self.rightBound = x + windowWidth
                self.changeBound(x, y - windowHeight, 1, blocks)
                self.changeBound(x, y + windowHeight, 2, blocks)
                self.changeBound(x + windowWidth, y, 4, blocks)
        else:
            if [x, y - windowHeight] in blocks:
                self.changeBound(x, y - windowHeight, 1, blocks)
            elif [x, y + windowHeight] in blocks:
                self.changeBound(x, y + windowHeight, 2, blocks)
            elif [x - windowWidth, y] in blocks:
                self.changeBound(x - windowWidth, y, 3, blocks)
            elif [x + windowWidth, y] in blocks:
                self.changeBound(x + windowWidth, y, 4, blocks)
    
    def distanceToCenter(self):
        x_diff = self.coorX - imgWidth / 2
        y_diff = self.coorY - imgHeight / 2
        return int(sqrt(x_diff*x_diff + y_diff*y_diff))

    def getDistance(self, bul):
        x_diff = self.coorX - bul.coorX
        y_diff = self.coorY - bul.coorY
        return int(sqrt(x_diff*x_diff + y_diff*y_diff))

def generateImg(loewrBound, upperBound, imgNum):
    cap = cv2.VideoCapture('17_43_50Uncompressed-0000.avi')
    counter = 0
    global combination

    while counter < loewrBound:
        _, frame = cap.read()
        if frame is None:
            break
        counter += 1
    
    while counter <= upperBound:
        _, frame = cap.read()
        if frame is None:
            break
        counter += 1
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lowerThres, upperThres)
        mask = cv2.medianBlur(mask, 5)
        res = cv2.bitwise_or(frame, frame, mask = mask)
        kernel = np.ones((7, 7), np.float32) / 49
        smoothed = cv2.filter2D(res, -1, kernel)
        if counter == loewrBound  + 1:
            combination = smoothed
        else:
            combination += smoothed

        print("Processed No." + str(counter - 1) + " Image.")
        
    cv2.imwrite('trajectory' + str(imgNum) + '.jpg', combination)
    print('Finished Generation Trajectory Image(%d)' % imgNum)
    cap.release()

def processImg(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowerThres, upperThres)
    mask = cv2.medianBlur(mask, 5)
    return cv2.bitwise_or(img, img, mask = mask)

def checkPattern(img, row, col):
    global windowHeight, windowWidth
    pixelCnt = 0
    for i in range(row, row + windowHeight):
        for j in range(col, col + windowWidth): 
            pixelCnt += img[i][j]
    pixelCnt /= (windowHeight*windowWidth)
    return pixelCnt

def bulletInImage(img, index):
    img = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_HSV2BGR_FULL), cv2.COLOR_BGR2GRAY)
    blocks = []
    bullets = []
    for i in range(0, imgHeight, windowHeight):
        for j in range(0, imgWidth, windowWidth):
            imgCheck = 0
            for m in range (i, i + windowHeight, windowHeight // 4):
                for n in range(j, j + windowWidth, windowWidth // 4):
                    imgCheck += img[m][n]
            imgCheck
            if imgCheck < 3:
                continue
            if checkPattern(img, i, j) > thres:
                coor = [j + windowWidth // 2, i + windowHeight // 2]
                blocks.append(coor)
    while len(blocks) > 0:
        bullets.append(Bullet(blocks))
    i = 0  
    while i < len(bullets):
        if len(bullets[i].blocks) > bulletLargestSize:
            bullets.remove(bullets[i])
        else:
            i += 1
    for bullet in bullets:
        coorX = 0
        coorY = 0
        for block in bullet.blocks:
            coorX += block[0]
            coorY += block[1]
        coorX //= len(bullet.blocks)
        coorY //= len(bullet.blocks)
        bullet.coorX = coorX
        bullet.coorY = coorY
    return bullets