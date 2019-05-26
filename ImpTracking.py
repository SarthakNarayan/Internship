import argparse
import cv2
import time

ap = argparse.ArgumentParser()
choice = int(input("Enter your choice: 1 For Custom Video , 2 For Camera : "))
if choice == 1:
    ap.add_argument("-v", "--video", type=str, help="path to input video file",
                default = r"C:\Users\Lenovo\Desktop\IITB Internship\VIDEOS\1080P\ONLY CIRCULAR LOW DENSITY.mp4")
else:
    ap.add_argument("-v", "--video", type=str, help="path to input video file",
                default = 0)

ap.add_argument("-t", "--tracker", type=str, help="OpenCV object tracker type" ,
                default="csrt")
args = vars(ap.parse_args())


OPENCV_OBJECT_TRACKERS = {
		"csrt": cv2.TrackerCSRT_create,#1
		"kcf": cv2.TrackerKCF_create,
		"boosting": cv2.TrackerBoosting_create,
		"mil": cv2.TrackerMIL_create, #2
		"tld": cv2.TrackerTLD_create,
		"medianflow": cv2.TrackerMedianFlow_create,
		"mosse": cv2.TrackerMOSSE_create
	}

# grab the appropriate object tracker using our dictionary of
# OpenCV object tracker objects
tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

# initialize the bounding box coordinates of the object to track
initBoundingBox = None
    
cap = cv2.VideoCapture(args["video"])

# For camera
if (args["video"] == 0):
    while(cap.isOpened()):
        # grab the current frame, then handle if we are using a
        # VideoStream or VideoCapture object
        ret, frame = cap.read()
        if ret == True:
    
            frame = cv2.resize(frame, (600, 600), interpolation = cv2.INTER_LINEAR)
            frame = cv2.flip(frame , 1)
            (H, W) = frame.shape[:2]
    
            # check to see if we are currently tracking an object
            if initBoundingBox is not None:
                # grab the new bounding box coordinates of the object
                (success, box) = tracker.update(frame)
    
                # check to see if the tracking was a success
                if success:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h),(0, 255, 0), 2)
    
            # initialize the set of information we'll be displaying on
            # the frame
                info = [("Tracker", args["tracker"]), 
                        ("Success", "Yes" if success else "No")]
    
            # loop over the info tuples and draw them on our frame
                for (i, (k, v)) in enumerate(info):
                    text = "{}: {}".format(k, v)
                    cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
            # show the output frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("s"):
                initBoundingBox = cv2.selectROI("Frame", frame, fromCenter=False,
			showCrosshair=True)
                tracker.init(frame, initBoundingBox)            
    
    	# if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break
        else:
            break
    
    cap.release()
    cv2.destroyAllWindows()

# For Custom Video
else:
    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (600, 600), interpolation = cv2.INTER_LINEAR)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(0) & 0xFF
        # select the bounding box of the object we want to track (make
        # sure you press ENTER or SPACE after selecting the ROI)
        if key == 2555904:
                ret, frame = cap.read()
        if key == ord("s"):
                break
        
    initBoundingBox = cv2.selectROI("Frame", frame, fromCenter=False,
                                       showCrosshair=True)
    
    # start OpenCV object tracker using the supplied bounding box
    # coordinates, then start the FPS throughput estimator as well
    tracker.init(frame, initBoundingBox)
    
    while(cap.isOpened()):
        # grab the current frame, then handle if we are using a
        # VideoStream or VideoCapture object
        ret, frame = cap.read()
        if ret == True:
    
            frame = cv2.resize(frame, (600, 600), interpolation = cv2.INTER_LINEAR)
            (H, W) = frame.shape[:2]
    
            # check to see if we are currently tracking an object
            if initBoundingBox is not None:
                # grab the new bounding box coordinates of the object
                timer = cv2.getTickCount()
                (success, box) = tracker.update(frame)
                fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
    
                # check to see if the tracking was a success
                if success:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h),(0, 255, 0), 2)
    
            # initialize the set of information we'll be displaying on
            # the frame
                info = [("Tracker", args["tracker"]), 
                        ("Success", "Yes" if success else "No")]
    
            # loop over the info tuples and draw them on our frame
                for (i, (k, v)) in enumerate(info):
                    text = "{}: {}".format(k, v)
                    cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
            # show the output frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
    
    	# if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break
        else:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
