import math

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities
from pycaw.pycaw import IAudioEndpointVolume

import cv2
import numpy
import mediapipe as mp

# Loading Hand Model
mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils
hands = mpHands.Hands()

# Loading Speaker Maximum and Minimum Volume Range
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

Volume = volume.GetVolumeRange()[:2]

cap = cv2.VideoCapture(0)

while True:
    frame = cap.read()[1]

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for i in results.multi_hand_landmarks:
            for id, ln in enumerate(i.landmark):
                h, w, c = frame.shape

                if id == 4:
                    cX, cY = int(ln.x*w), int(ln.y*h)
                    cv2.circle(frame, (cX, cY), 20, (0, 255, 10), 3)

                if id == 8:
                    c_X, c_Y = int(ln.x*w), int(ln.y*h)

                    cv2.circle(frame, (c_X, c_Y), 20, (0, 255, 10), 3)
                    cv2.line(frame, (cX, cY), (c_X, c_Y), (0, 255, 20), 3)

                    VOL = math.hypot(c_X - cX, c_Y - cY)

                    normVol = numpy.interp(VOL, [50, 150], Volume)

                    volume.SetMasterVolumeLevel(normVol, None)

                    cv2.putText(frame, f"Volume: {100 * ((Volume[0] - int(normVol)) / Volume[0]):.1f}%", (20, 20*3),
                                cv2.FONT_HERSHEY_PLAIN, 3, (255, 5, 100), 3)

            mpDraw.draw_landmarks(frame, i, mpHands.HAND_CONNECTIONS)

    cv2.imshow("Volume Control", frame)

    if cv2.waitKey(1) == ord('q'):
        break
