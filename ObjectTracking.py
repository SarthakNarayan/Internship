import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import time
import sys
import allantools

# Important works only with Python 2.7 32 bit 

def Initialization(video="low" , tracker = "csrt"):
    '''
    We initialize the camera and the trackers

    Args:
    video: Select the type of video i.e. low or high density
        video = high for high density
        video = low for low density 
        default is low
    tracker: To select the type of tracker needed. 
        tracker = "csrt" , "kcf" ,"boosting" ,"mil","tld","medianflow","mosse"
        select any one. Default is csrt
    '''
    if video == "high":
        path_video = r"C:\Users\Lenovo\Desktop\IITB Internship\VIDEOS\1080P\ONLY CIRCULAR HIGH DENSITY7.mp4"
        Initialization.video_type = "high"
    elif video == "low":
        path_video = r"C:\Users\Lenovo\Desktop\IITB Internship\VIDEOS\1080P\ONLY CIRCULAR LOW DENSITY3.mp4"
        Initialization.video_type = "low"

    # Making all the variables global
    global cap,width,height,black_background,Tracker_used,trackers
    cap = cv2.VideoCapture(path_video)

    # Getting the width and height of the input frame
    width , height = cap.get(3) , cap.get(4)
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
    Tracker_used = OPENCV_OBJECT_TRACKERS[tracker]()
    # initialize OpenCV's special multi-object tracker
    trackers = cv2.MultiTracker_create()

def Video(waitkey = 0):
    '''
    This function is for processing the video

    Args:
    waitkey: for specifying the waitkey value
        0 for manual operation
        optimal choice is 60
        default is 0
    '''
    (x , y ,w , h) = (0,0,0,0)
    (fx , fy ,fw , fh) = (0,0,0,0)
    (ox , oy) = (0,0)
    Video.pos_x = []
    Video.pos_y = []    
    random_colours = (255*abs(np.random.randn(255,3))).astype(int)
    color_index = 0
    draw = False
    collection = False
    start_time = 0
    # Video.frame_collector = []

    while(cap.isOpened()):
        ret , frame = cap.read()
        if ret == True:
            color_index = 0
            (_, boxes) = trackers.update(frame)
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
                    # Video.frame_collector.append(frame)

                if collection == True:
                    Video.pos_x.append(((x+w/2)-ox))
                    Video.pos_y.append((oy-(y+h/2)))
                    cv2.circle(black_background , (x+w/2,y+h/2) , 2 , (255,255,255) , -1)

            cv2.imshow('frame',frame)
            cv2.imshow("Background" , black_background)
            key = cv2.waitKey(waitkey) & 0xFF
            if key == ord("p"):
                # There should be no pause once d has been pressed
                waitkey = 0
            if key == ord("c"):
                waitkey = 1
            if key == 2555904:
                ret, frame = cap.read()
            if key == ord("s"):
                box = cv2.selectROI("Selector", frame, fromCenter=False,
                            showCrosshair=True)
                tracker = Tracker_used
                trackers.add(tracker, frame, box)
                cv2.destroyWindow('Selector')
            if key == 27:
                break
            # if((((x+w/2)-ox)<-420) & ((oy-(y+h/2))>240)):
            #     Video.pos_x[:-1]
            #     Video.pos_y[:-1]
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
    Video.total_time = end_time-start_time
    cap.release()
    cv2.destroyWindow('frame')
    
def Plot(todo = "save",xaxischoice = "Frames",save="no",number = 0):
    '''
    For plotting the graphs

    Args:
    todo: To decide whether to plot new data or the one read
            default is save
    xaxischoice: To decide whether you want it in number of frames or
            time. default is Frames
    save: if you want to save the plot. Will be stored in the same folder where 
            data is being collected. By default it is no.
            save = "yes" to save the file
    number: Number reference for saving the plot
    '''
    
    if todo == "save":
        X = Video.pos_x
        Y = Video.pos_y
        timeforxaxis = Video.total_time
        if xaxischoice == "Frames":
            x_axis = np.arange(1,(len(X)+1),1)
        else:
            x_axis = np.linspace(1,(timeforxaxis+1),len(X))
    else:
        X = SavingAndReadingData.xAxis
        Y = SavingAndReadingData.yAxis
        timeforxaxis = SavingAndReadingData.timing
        if xaxischoice == "Frames":
            x_axis = np.arange(1,(len(X)+1),1)
        else:
            x_axis = np.linspace(1,(timeforxaxis+1),len(X))
    
    fig = plt.figure(figsize=(12,7))
    fig.subplots_adjust(hspace=0.5, wspace=0.2)
    
    plt.subplot(3, 2, 1)
    plt.plot( x_axis ,X, label='X coordinates vs time')
    plt.xlabel('frames')
    plt.ylabel('X coordinates')
    plt.title('X coordinates vs ' + xaxischoice)

    plt.subplot(3, 2, 3)
    plt.scatter( x_axis ,X, label='X coordinates vs time')
    plt.xlabel('frames')
    plt.ylabel('X coordinates')
    plt.title('X coordinates vs ' + xaxischoice +' scatter plot')

    plt.subplot(3, 2, 5)
    plt.hist(X, color = 'blue', edgecolor = 'black',bins = len(X))
    plt.xlabel('X coordinates')
    plt.ylabel('Count')
    plt.title('Histogram of X coordinates')

    plt.subplot(3, 2, 2)
    plt.plot( x_axis ,Y, label='Y coordinates vs time')
    plt.xlabel('frames')
    plt.ylabel('Y coordinates')
    plt.title('Y coordinates vs ' + xaxischoice)

    plt.subplot(3, 2, 4)
    plt.scatter( x_axis, Y, label='Y coordinates vs time')
    plt.xlabel('frames')
    plt.ylabel('Y coordinates')
    plt.title('Y coordinates vs ' + xaxischoice +' scatter plot')

    plt.subplot(3, 2, 6)
    plt.hist(Y, color = 'blue', edgecolor = 'black',bins = len(Y))
    plt.xlabel('Y coordinates')
    plt.ylabel('Count')
    plt.title('Histogram of Y coordinates')

    plt.show()

    if save == "yes":
        plot_path = SavingAndReadingData.path + "\\plot" + str(number) + ".png"
        fig.savefig(plot_path)

def SavingAndReadingData(todo,dataType,number = 0):
    '''
    For saving the data to the disk

    Args:
    todo: To decide whether to save or read. Default todo = "save"
        todo = "read" for reading the data
    dataType: To decide whether the data being stored is of low density or high density data
    number: to distinguish it from other samples
    '''
    if dataType == "low":
        SavingAndReadingData.path = r"C:\Users\Lenovo\Desktop\Internship\Data\LessDense"
    else:
        SavingAndReadingData.path = r"C:\Users\Lenovo\Desktop\Internship\Data\MoreDense"

    path_x = SavingAndReadingData.path + "\X" + str(number) + ".npy"
    path_y = SavingAndReadingData.path + "\Y" + str(number) + ".npy"
    path_time =  SavingAndReadingData.path + "\\time" + str(number) + ".npy"
    path_background = SavingAndReadingData.path + "\\background" + str(number) + ".png"
    # path_video = SavingAndReadingData.path + "\\video" + str(number) + ".mp4"
    if todo == "save":
        np.save(path_x,Video.pos_x)
        np.save(path_y,Video.pos_y)
        np.save(path_time,Video.total_time)
        # saving the background plot
        cv2.imwrite(path_background,black_background)
        # out = cv2.VideoWriter(path_video, -1, 10.0, (int(width),int(height)))
        # for i in range(len(Video.frame_collector)):
        #     out.write(Video.frame_collector[i])
        # out.release()
    else:
        SavingAndReadingData.xAxis = np.load(path_x)
        SavingAndReadingData.yAxis = np.load(path_y)
        SavingAndReadingData.timing = np.load(path_time)

def Verbosity(verbose = 0):
    '''
    For deciding the verbosity

    Args:
    verbose: for deciding the verbosity 
                by default 0. Number in increasing order of verbosity
    '''
    if verbose == 0:
        print("Total time taken :{}".format( Video.total_time))
        print("Number of frames/values :{}".format(len(Video.pos_x)))
        print("values stored")
    if verbose == 1:
        print("Positions in x coordinate are",Video.pos_x)
        print("Positions in y coordinate are",Video.pos_y)
        print("Total time taken :{}".format( Video.total_time))
        print("Number of frames/values :{}".format(len(Video.pos_x)))
        print("values stored")

def allandeviation(wanted = "X" , number = 0):
    if wanted == "X":
        path_allan = SavingAndReadingData.path + "\X" + str(number) + ".npy" 
    if wanted == "Y":  
        path_allan = SavingAndReadingData.path + "\Y" + str(number) + ".npy"
    values = np.load(path_allan)
    tau = []
    for i in range(1,(len(values)+1)):
        tau.append(i)

    tau1 = np.logspace(0, 4, 1000)  # tau values from 1 to 1000

    # values = np.random.randn(10000)
    r = 20 # sampling rate
    (tau2, ad, ade, adn) = allantools.oadev(values, rate=20, data_type="freq", taus=tau1)
    (tau22, ad2, ade2, adn2) = allantools.oadev(values, rate=1, data_type="freq", taus=tau1)

    fig = plt.figure(figsize=(8,6))
    # fig.subplots_adjust(hspace=0.5, wspace=0.3)
    plt.subplot(1, 2, 1)
    plt.loglog(tau2, ad,'b')
    plt.plot([10000],[10000])
    plt.xlabel('tau')
    plt.ylabel('ADEV [V]')
    plt.grid()
    plt.subplot(1, 2, 2)
    plt.plot([10000],[10000])
    plt.loglog(tau22, ad2,'b')
    plt.xlabel('tau')
    plt.ylabel('ADEV [V]')
    plt.grid()
    plt.show()

def main():
    drawing = int(input("1 for collecting data and 0 for reading data 2 for drawing allan deviation:"))
    # Reference number 0 will always be for testing
    number_for_reference = int(input("Give the number you want to name or read from the file :"))
    if drawing == 1:
        Initialization("high")
        Video(waitkey = 0)
        SavingAndReadingData("save", Initialization.video_type , number_for_reference)
        Verbosity(verbose=1)
        Plot("save","Frames","yes",number_for_reference)
    if drawing == 0:
        Initialization("high")
        SavingAndReadingData("read", Initialization.video_type , number_for_reference)
        Plot("read","Frames","no",number_for_reference)
    if drawing == 2:
        Initialization("high")
        SavingAndReadingData("read", Initialization.video_type , number_for_reference)
        allandeviation("X" , number_for_reference)
        

if __name__ == '__main__':
    main()