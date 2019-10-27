# Name: TIAN Xiangan
# ITSC: xtianae
import copy
from getBullet import *
from getTrajectory import *    

cap = cv2.VideoCapture('17_43_50Uncompressed-0000.avi')
haveBul = False
angleThres = 0.95
trajCnt = 0
speed = 0
counter = 0
trajectories = []

while True:
    _, frame = cap.read()
    if frame is None:
        break
    img = processImg(frame)
    cv2.imwrite('debug/de%d.jpg'% counter, img)
    bullets = bulletInImage(img, counter)

    counter += 1

    if len(bullets) == 0 and haveBul == False:
        print("No.%-3d Condition 1 trajectories: %d" % (counter, len(trajectories)))
        continue
    elif len(bullets) == 1 and haveBul == False:
        print("No.%-3d Condition 2 trajectories: %d" % (counter, len(trajectories)))
        haveBul = True
        trajectories.append(Trajectory(img, copy.deepcopy(bullets[0])))
    elif len(bullets) > 1 and haveBul == False:
        print("No.%-3d Condition 3 trajectories: %d" % (counter, len(trajectories)))
        haveBul = True
        for bullet in bullets:
            trajectories.append(Trajectory(img, copy.deepcopy(bullets[0])))
    elif len(bullets) == 0 and haveBul == True:
        print("No.%-3d Condition 4 trajectories: %d" % (counter, len(trajectories)))
        haveBul = False
        for traj in trajectories:
            if len(traj.bulletBuffer) > 1:
                trajCnt += 1
                traj.drawTrajectory(trajCnt)
        trajectories = []   
    elif len(bullets) == 1 and haveBul == True:
        print("No.%-3d Condition 5 trajectories: %d" % (counter, len(trajectories)))
        if len(trajectories) == 0:
            trajectories.append(Trajectory(img, copy.deepcopy(bullets[0])))
            continue
        index = 0
        smallest = trajectories[0].bulletBuffer[-1].getDistance(bullets[0])
        for i in range(1, len(trajectories)):
            if trajectories[i].bulletBuffer[-1].getDistance(bullets[0]) < smallest and trajectories[i].checkDirection(bullets[0]) > angleThres:
                index = i
                smallest = trajectories[i].bulletBuffer[-1].getDistance(bullets[0])
        traj = copy.deepcopy(trajectories[index])
        del trajectories[index]
        for trajectory in trajectories:
            if len(trajectory.bulletBuffer) > 1:
                print(len(trajectory.bulletBuffer))
                print(len(trajectory.imgBuffer))
                trajCnt += 1
                trajectory.drawTrajectory(trajCnt)
        trajectories = []
        if traj.compareSpeed(bullets[0]):
            if traj.direction == [0, 0]:
                traj.setDirection(bullets[0])
                traj.addIB(img, copy.deepcopy(bullets[0]))
                trajectories.append(traj)
            else:
                if traj.checkDirection(bullets[0]) > angleThres:
                    traj.addIB(img, copy.deepcopy(bullets[0]))
                    trajectories.append(copy.deepcopy(traj))
                else:
                    if len(traj.bulletBuffer) > 1:
                        trajCnt += 1
                        traj.drawTrajectory(trajCnt)
                    trajectories.append(Trajectory(img, bullets[0]))
    elif len(bullets) > 1 and haveBul == True:
        print("No.%-3d Condition 6 trajectories: %d" % (counter, len(trajectories)))
        newTraj = []
        for traj in trajectories:
            if len(bullets) == 0:
                if len(traj.bulletBuffer) > 1:
                    trajCnt += 1
                    traj.drawTrajectory(trajCnt)
            continue
            index = 0
            smallest = traj.bulletBuffer[-1].getDistance(bullets[0])
            if len(bullets) > 1:
                for i in range(1, len(bullets)):
                    if traj.bulletBuffer[-1].getDistance(bullets[i]) < smallest and traj.checkDirection(bullets[i]) > angleThres:
                        smallest = traj.bulletBuffer[-1].getDistance(bullets[i]) < smallest
                        index = i
            if index == 0 and traj.checkDirection(bullets[0]) <= angleThres:
                if len(traj.bulletBuffer) > 1:
                    trajCnt += 1
                    traj.drawTrajectory(trajCnt)
                    continue
            if not traj.compareSpeed(bullets[index]):
                if len(traj.bulletBuffer) > 1:
                    trajCnt += 1
                    traj.drawTrajectory(trajCnt)
                    del bullets[index]
                    continue
            if traj.direction == [0, 0]:
                traj.setDirection(bullets[index])
            traj.addIB(img, copy.deepcopy(bullets[index]))
            newTraj.append(copy.deepcopy(traj))
            del bullets[index]
        trajectories = copy.deepcopy(newTraj)
        for bullet in bullets:
            trajectories.append(Trajectory(img, copy.deepcopy(bullet)))

cap.release()
print('Finished')