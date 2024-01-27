import math
import time

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities
from pycaw.pycaw import IAudioEndpointVolume

import cv2
import numpy
import mediapipe as mp


mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils
hands = mpHands.Hands()

starTime = 0

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

minVol, maxVol = volume.GetVolumeRange()


while True:
    success, frame = cap.read()

    nowTime = time.time()
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    # print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for i in results.multi_hand_landmarks:
            for id, ln in enumerate(i.landmark):
                # print(id, ln)
                h, w, c = frame.shape
                if id == 4:
                    cX, cY = int(ln.x*w), int(ln.y*h)
                    cv2.circle(frame, (cX, cY), 20, (0, 255, 10), 3)

                if id == 8:
                    c_X, c_Y = int(ln.x*w), int(ln.y*h)

                    cv2.circle(frame, (c_X, c_Y), 20, (0, 255, 10), 3)
                    cv2.line(frame, (cX, cY), (c_X, c_Y), (0, 255, 20), 3)

                    VOL = math.hypot(c_X - cX, c_Y - cY)

                    normVol = numpy.interp(
                        VOL, [30, 275], [minVol, maxVol])
                    volume.SetMasterVolumeLevel(normVol, None)

            mpDraw.draw_landmarks(frame, i, mpHands.HAND_CONNECTIONS)

    fps = 1 / (nowTime - starTime)
    starTime = nowTime

    cv2.putText(frame, f"FPS: {int(fps)}", (20, 20*3),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 5, 100), 3)
    cv2.imshow("frame", frame)

    cv2.waitKey(1)
    if 0xFF == ord('q'):
        break
