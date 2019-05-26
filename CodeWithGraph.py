import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import time

# If u want to manually move through frames set waitKey(0) mostly for videos
# for web cam make it 1

# When inside the execution you press 's' a new window named selector will appear
# select the roi in that window and press enter you will see a green bounding box in the main frame
# if u want to select another object press s again in the main window
# Select the roi by going in the selector window
cap = cv2.VideoCapture(r"C:\Users\Lenovo\Desktop\IITB Internship\VIDEOS\1080P\ONLY CIRCULAR LOW DENSITY.mp4")
width = cap.get(3)
height = cap.get(4)
print(height , width)

draw = False
collection = False
black_background = np.zeros((int(height),int(width),3),np.uint8)
OPENCV_OBJECT_TRACKERS = {
	"csrt": cv2.TrackerCSRT_create,
	"kcf": cv2.TrackerKCF_create,
	"boosting": cv2.TrackerBoosting_create,
	"mil": cv2.TrackerMIL_create,
	"tld": cv2.TrackerTLD_create,
	"medianflow": cv2.TrackerMedianFlow_create,
	"mosse": cv2.TrackerMOSSE_create
}

(x , y ,w , h) = (0,0,0,0)
(fx , fy ,fw , fh) = (0,0,0,0)
(ox , oy) = (0,0)
pos_x = []
pos_y = []
angle_holder = []
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
                cv2.circle(frame , (x+w/2,y+h/2) , 4 , random_colours[color_index] , -1)

                if draw == True:
                    cv2.line(frame , (0,fy+fh/2) , (int(width),fy+fh/2) , (255,0,0) , 3)
                    cv2.line(frame , (fx+fw/2,0) , (fx+fw/2,int(height)) , (255,0,0) , 3)
                    cv2.line(black_background , (0,fy+fh/2) , (int(width),fy+fh/2) , (255,0,0) , 3)
                    cv2.line(black_background , (fx+fw/2,0) , (fx+fw/2,int(height)) , (255,0,0) , 3)

                if collection == True:
                    pos_x.append(((x+w/2)-ox))
                    pos_y.append((oy-(y+h/2)))
                    cv2.circle(black_background , (x+w/2,y+h/2) , 2 , (255,255,255) , -1)
#                if(x+w/2>fx+fw/2 & y+h/2<fy+fh/2):
#                    text = "1st quadrant"
#                    cv2.putText(frame, text, (10, 30 ),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
#                if(x+w/2<fx+fw/2 & y+h/2<fy+fh/2):
#                    text = "2nd quadrant"
#                    cv2.putText(frame, text, (10, 30 ),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
#                if(x+w/2<fx+fw/2 & y+h/2>fy+fh/2):
#                    text = "3rd quadrant"
#                    cv2.putText(frame, text, (10, 30 ),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
#                if(x+w/2>fx+fw/2 & y+h/2>fy+fh/2):
#                    text = "4th quadrant"
#                    cv2.putText(frame, text, (10, 30 ),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
    
                
            cv2.imshow('frame',frame)
            cv2.imshow("Background" , black_background)
            key = cv2.waitKey(60) & 0xFF
            if key == 2555904:
                ret, frame = cap.read()
            if key == ord("s"):
                box = cv2.selectROI("Frame", frame, fromCenter=False,
                            showCrosshair=True)
                tracker = OPENCV_OBJECT_TRACKERS["csrt"]()
                trackers.add(tracker, frame, box)
            if key == 27:
                break
            if key == ord("d"):
                print("Drawing the reference coordinates")
                draw = True
                fx = x
                fy = y
                fw = w
                fh = h
                (ox , oy)  = (x+w/2 , y+h/2)
                collection = True
                start_time = time.time()
                
                
    else:
        break

end_time = time.time()
total_time = end_time-start_time
cap.release()
cv2.destroyAllWindows()

print("Positions in x coordinate are",pos_x)
print("Positions in y coordinate are",pos_y)

for i in range(0,len(pos_x)):
    if pos_x[i]!=0:
        value = math.atan(pos_y[i]/pos_x[i])
        angle_holder.append(value)

print(angle_holder)

x_axis = np.linspace(0,total_time,len(angle_holder))
plt.plot( x_axis ,angle_holder, label='Angle vs time')
plt.xlabel('Time')
plt.ylabel('Angle in Radians')
plt.title('Angle vs Time Graph after Motion Analysis')
plt.legend()
plt.show()
