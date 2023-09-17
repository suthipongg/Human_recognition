import urllib.request
import cv2
import numpy as np
import time
url='http://172.20.10.2/cam.jpg'

while True:
    start = time.time()
    imgResp = urllib.request.urlopen(url)
    imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
    frame = cv2.imdecode(imgNp,-1)
    print("fps :", 1/(time.time()-start))
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) == 27:
        break