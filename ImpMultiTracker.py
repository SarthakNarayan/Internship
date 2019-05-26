import cv2
import numpy as np

cap = cv2.VideoCapture(r"C:\Users\Lenovo\Desktop\IITB Internship\VIDEOS\1080P\ONLY CIRCULAR LOW DENSITY.mp4")


OPENCV_OBJECT_TRACKERS = {
	"csrt": cv2.TrackerCSRT_create,
	"kcf": cv2.TrackerKCF_create,
	"boosting": cv2.TrackerBoosting_create,
	"mil": cv2.TrackerMIL_create,
	"tld": cv2.TrackerTLD_create,
	"medianflow": cv2.TrackerMedianFlow_create,
	"mosse": cv2.TrackerMOSSE_create
}
 
# initialize OpenCV's special multi-object tracker
trackers = cv2.MultiTracker_create()

random_colours = (255*abs(np.random.randn(255,3))).astype(int)
color_index = 0
while(cap.isOpened()):
    ret , frame = cap.read()
    if ret == True:
            color_index = 0
            (success, boxes) = trackers.update(frame)
            for box in boxes:
                color_index+=1
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), random_colours[color_index], 2)
    
            cv2.imshow('frame',frame)
            key = cv2.waitKey(0) & 0xFF
            if key == 2555904:
                ret, frame = cap.read()
            if key == ord("s"):
                box = cv2.selectROI("Frame", frame, fromCenter=False,
                            showCrosshair=True)
                tracker = OPENCV_OBJECT_TRACKERS["csrt"]()
                trackers.add(tracker, frame, box)
            if key == 27:
                break
    else:
        break
    
cap.release()
cv2.destroyAllWindows()
