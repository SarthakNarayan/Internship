#########################################################################################################
# IMPORTS SECTION
import cv2
import tkinter
from tkinter import *
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
import numpy as np
import PIL
import time
import tkinter.messagebox
import matplotlib.pyplot as plt
import allantools
import dlib
import tkinter.ttk as ttk
import textwrap
#########################################################################################################

#########################################################################################################
# MAIN WINDOW STARTS
main_window = Tk() # creating a new main window
main_window.geometry("500x150") # Width and height of the window
main_window.title("Tracking Program") #Title of the window

# Function for centering the main window
def center_window(width=300, height=200):
    # get screen width and height
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    main_window.geometry('%dx%d+%d+%d' % (width, height, x, y))

center_window(500, 150)

# global variables section 
####################################################
# main window global variables
tracker = StringVar()
Tracker_used = cv2.TrackerCSRT_create()
load_path = ''
save_path = ''
camera = IntVar()
spinbox1_main = StringVar()
enable_tracking = False

# tracker window global variables
pause = 0
frame = 0
(fx, fy, fw, fh, x, y, w, h, ox, oy) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
(start_time, end_time, total_time) = (0, 0, 0)
collection = False
draw = False
pos_x = []
pos_y = []
dlib_tracking = False
dlib_tracker = dlib.correlation_tracker()
cv2image = 0
(startX, startY, endX, endY) = (0, 0, 0, 0)
(h1w, s1w, v1w, h2w, s2w, v2w) = (0, 0, 0, 0, 0, 0)
var_c1_hsv = StringVar()
var_c2_hsv = StringVar()
(cx, cy, fcx, fcy) = (0, 0, 0, 0)
var_c3_hsv = StringVar()
var_c4_hsv = StringVar()
spin1_hsv_tracker = StringVar()

# value plotter global variables
load_path_x_plotter = ''
load_path_y_plotter = ''
load_path_time_plotter = ''
enable_plot = 0
var_c1 = StringVar()
loaded_X = ''
loaded_Y = ''
loaded_time = ''

# ad_plotter global variables
value_type = IntVar()
adplotter_path = ''
adplotter_values = ''
####################################################

# Setting predefined values to some of the widgets in GUI
####################################################
# setting values
camera.set(0)
spinbox1_main.set('0')
tracker.set('csrt')
var_c1.set(0)
value_type.set(0)
var_c1_hsv.set(1)
var_c2_hsv.set(0)
var_c3_hsv.set(0)
var_c4_hsv.set(0)
spin1_hsv_tracker.set('127')
####################################################

# Function for gamma transform
# Generally used with webcam when lighting conditions are bad or insufficient 
# To increase the brightness of the image
def gamma_transform(image , gamma = 2):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
    for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

# Function for finding the maximum contour area
# Returns the contour with maximum area and the maximum area 
# Used in HSV and thresholding tracking
def maximum_contour_area(contour):
    maximum_area = cv2.contourArea(contour[0])
    maximum = contour[0]
    for i in range(1, len(contour)):
        if(cv2.contourArea(contour[i]) > maximum_area):
            maximum_area = cv2.contourArea(contour[i])
            maximum = contour[i]
    return maximum, maximum_area


# Function for opening a file using a dialog box
# Used in file submenu of the main window
def OpenFile():
    global load_path, enable_tracking
    load_path = askopenfilename(initialdir="/", title="Select file")
    print(load_path)
    enable_tracking = True
    button1_main.configure(state=NORMAL)
    if load_path != '':
        other_algorithms.entryconfig(1, state=NORMAL)
    else:
        other_algorithms.entryconfig(1, state=DISABLED)

# Function for choosing the directory for saving using dialog box
# Used in file submenu of the main window
def SaveFile():
    global save_path
    save_path = filedialog.askdirectory()
    print(save_path)

# Function for opening a new window for about option in help submenu
# Contains information about the program
def About():
    about_window = Toplevel()
    about_window.geometry("250x300")
    about_window.title("About the Software")
    about_window.resizable(FALSE , FALSE)

    scrollbar = Scrollbar(about_window)
    editArea_about = Text(about_window, width=28, height=32, wrap="word",
                          yscrollcommand=scrollbar.set,
                          borderwidth=0, highlightthickness=0)

    text = ''' Created by : Sarthak Narayan \n Version : 2019.07 \n License : MIT License 
    \n Dependencies Python : 3.6.8 \n OpenCV : 3.4.2 \n Tkinter : 8.6 \n PIL : 5.4.1 
 numpy : 1.16.2 \n Matplotlib : 2.2.2 \n Allan Tools : 2018.03 \n Dlib : 19.7.0 
     \n \nIF THE PROGRAM DOESNT WORK AS INTENDED THEN TRY CHECKING AND MATCHING THE VERSIONS \
WITH THE ONES MENTIONED ABOVE'''

    textwrap.dedent(text)
    editArea_about.configure(state='normal')
    editArea_about.insert('end', text)
    editArea_about.configure(state='disabled')

    scrollbar.config(command=editArea_about.yview)
    scrollbar.pack(side="right", fill="y")
    editArea_about.pack(side="left", fill="both", expand=True)

    about_window.mainloop()

# Function for opening a new window for use option in help submenu
# Contains use instructions about the program
def Use():

    instructions_window = Toplevel()
    instructions_window.geometry("1000x600")
    instructions_window.title("Use Instructions")
    instructions_window.resizable(FALSE , FALSE)

    scrollbar = Scrollbar(instructions_window)
    editArea_use = Text(instructions_window, width=100, height=80, wrap="word",
                        yscrollcommand=scrollbar.set,
                        borderwidth=0, highlightthickness=0)

    text = ''' \t \t \t \t \t \t \t USE INSTRUCTIONS \n
1)FOR COLLECTING DATA : 
    i)Choose the tracker either from trackers or other algorithms submenu. By default csrt tracker is selected.
   ii)If webcam or usb camera has to be used click on the webcam radio button and specify the camera number.
      By default it is 0 for webcam and starts from 1 for usb cameras.
  iii)Now click on start tracking button to go to the tracking window.
   iv)If a video from the computer has to be used then first go to file menu and then select open,
      It will open a dialog box. Choose the video.
    v)Click on the Use video radio button and then click on start tracking button to start tracking.
    
      NOTE: If hsv tracking is selected from other algorithms option then a window will appear which will ask you 
            to set the HSV values for color filtering. Once done filtering use ESC key to quit that window. Now 
            click on start tracking button on the main window.
      NOTE: For quickly getting the hsv values set h2w , s2w , v2w to maximum the start increasing h1w , s1w , v1w
            and decreasing h2w , s2w , v2w to get the desired color values.
          
2)Tracking the Particles :
    i)Pause button in the tracking window can be used for pausing the window.
   ii)Use the select the button to select the region or object to be tracked. 
      When the select window is pressed the video will be paused and a new window will appear.
      On the new window drag and leave the left mouse key to make a bounding box around the object, press enter 
      to go back to the tracking window. If the selection is wrong then to cancel it press c.
  iii)Once the particle is selected the bounding box will appear on the main tracking window. Click on Draw and 
      and collect button to start collecting data of the position of the particle. This will also draw x and y 
      axes on the screen. If you want to start tracking again press the button again. It will reset the previously
      collected values and draw new x and y axes
   iv)Once done with tracking press the exit button and a save window will appear destroying the curent tracking 
      window.

      NOTE: Same process applies when hsv or thresholding tracking is used. Just there are more options to play with
            and there is no select button. To start tracking try to isolate a single particle or use maximum area mode.
            Once done click on the draw and collect button.
      NOTE: The axes drawn take the center of the particle as their origin and the all the coordinates stored for 
            processing are calculated with respect to the origin.     
             
3)Saving the data :
    i)Select the directory where the data is to be saved by clicking on the Directory button. It will open a dialog box
      for selecting the directory.
   ii)Write the name of the files to be saved. DONT CHANGE THE EXTENSIONS.
  iii)Click on the save button to save the files. A pop up will appear saying that files have been saved successfully.
     
4)Plotting the data :
    i)To plot the data click on value plotter button.
   ii)Select the X and Y values by clicking on respective buttons and choosing the files from the dialog box.
  iii)Time values can also be selected by the same process to use time values tick the checkbox.
   iv)Click on plot button to get the matplotlib plot.
   
5)Plotting allan deviation :
    i)To plot allan deviation click on ADEV plotter button in the main window.
   ii)Select the value for which you want to plot the allan deviation by using the select values button.
      It will open a dialog box to choose the file.
  iii)If you plotting for X values choose the Use X radio button or vice verse.
   iv)Select the rate and click on plot allan deviation button.
   
      Note: If you want to see allan deviation plots for multiple plots just change the rate and click on plot allan
            allan deviation button again.   '''
    
    editArea_use.configure(state='normal')
    editArea_use.insert('end', text)
    editArea_use.configure(state='disabled')

    scrollbar.config(command=editArea_use.yview)
    scrollbar.pack(side="right", fill="y")
    editArea_use.pack(side="left", fill="both", expand=True)

    instructions_window.mainloop()

# Function for opening a new window for info option in help submenu
# Contains information about various trackers in the program
def Info():
    info_window = Toplevel()
    info_window.geometry("500x500")
    info_window.title("Info About Trackers")

    scrollbar = Scrollbar(info_window)
    editArea_info = Text(info_window, width=50, height=50, wrap="word",
                         yscrollcommand=scrollbar.set,
                         borderwidth=0, highlightthickness=0)

    text = '1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n'

    editArea_info.configure(state='normal')
    editArea_info.insert('end', text)
    editArea_info.configure(state='disabled')

    scrollbar.config(command=editArea_info.yview)
    scrollbar.pack(side="right", fill="y")
    editArea_info.pack(side="left", fill="both", expand=True)

    info_window.mainloop()

# Function for choosing the tracker
# Chooses one of the trackers present in the tracker submenu
def TrackerChooser():
    global tracker, Tracker_used
    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "kcf": cv2.TrackerKCF_create,
        "boosting": cv2.TrackerBoosting_create,
        "mil": cv2.TrackerMIL_create,
        "tld": cv2.TrackerTLD_create,
        "medianflow": cv2.TrackerMedianFlow_create,
        "mosse": cv2.TrackerMOSSE_create
    }
    Tracker_used = OPENCV_OBJECT_TRACKERS[tracker.get()]()
    print(Tracker_used)

# Function for choosing other tracking algorithms 
# Chooses one of the algorithms present in the other algorithms submenu
def otherAlgorithmChooser():
    global h1w, s1w, v1w, h2w, s2w, v2w
    print(tracker.get())

    if tracker.get() == 'hsv':
        tkinter.messagebox.showinfo(
            'To Exit', 'Use "ESC" key to exit once done collecting the hsv values')
        if camera.get() == 0:
            capu = cv2.VideoCapture(int(spinbox1_main.get()))
        elif camera.get() == 1:
            capu = cv2.VideoCapture(load_path)
        # naming a window for object tracking
        cv2.namedWindow('SettingHSV')

        # defining the nothing function
        def nothing():
            pass

        # creating trackbars
        cv2.createTrackbar('h1w', 'SettingHSV', 0, 255, nothing)
        cv2.createTrackbar('s1w', 'SettingHSV', 0, 255, nothing)
        cv2.createTrackbar('v1w', 'SettingHSV', 0, 255, nothing)
        cv2.createTrackbar('h2w', 'SettingHSV', 0, 255, nothing)
        cv2.createTrackbar('s2w', 'SettingHSV', 0, 255, nothing)
        cv2.createTrackbar('v2w', 'SettingHSV', 0, 255, nothing)

        while(capu.isOpened()):
            ret, frames = capu.read()
            if ret == True:
                if camera.get() == 0:
                    frames = cv2.flip(frames, 1)

                # blurring the image
                blur = cv2.GaussianBlur(frames, (11, 11), 20)

                # converting brg to hsv
                hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

                # getting the input from the trackbars
                h1w = cv2.getTrackbarPos('h1w', 'SettingHSV')
                s1w = cv2.getTrackbarPos('s1w', 'SettingHSV')
                v1w = cv2.getTrackbarPos('v1w', 'SettingHSV')
                h2w = cv2.getTrackbarPos('h2w', 'SettingHSV')
                s2w = cv2.getTrackbarPos('s2w', 'SettingHSV')
                v2w = cv2.getTrackbarPos('v2w', 'SettingHSV')

                # define range of the color object
                lower_blue = np.array([h1w, s1w, v1w])
                upper_blue = np.array([h2w, s2w, v2w])

                # thresholding the image to get only white colors by creating a mask
                mask = cv2.inRange(hsv, lower_blue, upper_blue)

                # performing morphological operations on mask
                kernelforerosion = np.ones((5, 5), np.uint8)
                erodedmask = cv2.erode(mask, kernelforerosion, iterations=1)

                # using bitwiseand to do the mask
                result = cv2.bitwise_and(blur, blur, mask=erodedmask)

                # for finding and drawing contours
                _, contours, _ = cv2.findContours(
                    erodedmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                frameswithcontours = cv2.drawContours(
                    result, contours, -1, (0, 255, 0), 4)

                # getting the centoid of the image
                if(len(contours) != 0):
                    cnt = contours[0]
                    M = cv2.moments(cnt)
                    if (M['m00'] != 0):
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])

                        # drawing a circle at the centroid of the shape
                        cv2.circle(result, (cx, cy), 5, (0, 0, 255), -1)

                # displaying the video
                cv2.imshow('SettingHSV', mask)
                cv2.imshow('resultant', result)

                # setting esc key to end the process
                if camera.get() == 0:
                    k = cv2.waitKey(1) & 0xFF
                else:
                    k = cv2.waitKey(0) & 0xFF

                if k == 27:
                    break
                if k == 2555904:
                    ret, frames = capu.read()
            else:
                break

        # to release camera and destroy all windows
        capu.release()
        cv2.destroyAllWindows()


#########################################################################################################
# TRACKER WINDOW STARTS

# Function for tracking purpose
# This is the function called when Start tracking button in the main window is pressed
def StartTracking():

    global cap

    # making a new window based on the type of tracker selected in the main window
    # one type of window for hsv and thresholding tracker and other type of window for other trackers
    if tracker.get() == 'hsv' or tracker.get() == 'thresh':
        hsv_tracker_window = Toplevel() # creating hsv tracking window
        hsv_tracker_window.geometry("800x800")  # width*height
        # simple logic for the title of the window
        if tracker.get() == 'hsv':
            hsv_tracker_window.title("HSV Tracking Window")
        else:
            hsv_tracker_window.title("Thresholding Tracking Window")

        # Several widgets present in the HSV Tracking Window/Thresholding Tracking Window
        entry1_hsv_tracker = Entry(hsv_tracker_window, width=5)
        entry1_hsv_tracker.place(x=300, y=500)
        entry1_hsv_tracker.insert(END, '100')

        combo1 = ttk.Combobox(hsv_tracker_window)
        combo1['values'] = ("None", "erosion", "dilation",
                            "opening", "closing")
        # Setting the seleted item
        combo1.current(0)
        combo1.place(x=400, y=600)

        combo2 = ttk.Combobox(hsv_tracker_window, state=DISABLED)
        combo2['values'] = ("THRESH_BINARY", "THRESH_BINARY_INV", "THRESH_TRUNC", "THRESH_TOZERO",
                            "THRESH_TOZERO_INV", "ADAPTIVE_MEAN", "ADAPTIVE_GAUSSIAN", "OTSU")
        # Setting the seleted item
        combo2.current(0)
        combo2.place(x=350, y=700)

        entry2_hsv_tracker = Entry(hsv_tracker_window, width=3)
        entry2_hsv_tracker.place(x=300, y=550)
        entry2_hsv_tracker.insert(END, '5')

        entry3_hsv_tracker = Entry(hsv_tracker_window, width=3, state=DISABLED)
        entry3_hsv_tracker.place(x=300, y=650)
        entry3_hsv_tracker.insert(END, '1')

        spin1_hsv_tracker = Spinbox(
            hsv_tracker_window, from_=1, to=255, width=4, state=DISABLED)
        spin1_hsv_tracker.place(x=600, y=700)
    else:
        tracker_window = Toplevel()
        tracker_window.geometry("800x700")  # width*height
        tracker_window.title("Tracking Window")

    # intializing trackers for using different types of tracker from the tracker sub menu
    trackers = cv2.MultiTracker_create()

    # selecting the input device based in the radio button
    # webcam or video
    if camera.get() == 0:
        cap = cv2.VideoCapture(int(spinbox1_main.get()))
        # cap = cv2.VideoCapture(int(spinbox1_main.get()) + cv2.CAP_DSHOW)
    elif camera.get() == 1:
        cap = cv2.VideoCapture(load_path)

    # Setting the height and width of the video
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

    # Storing height and width of the video
    width, height = cap.get(3), cap.get(4)
    # Creating a blackbackground for plotting purposes
    black_background = np.zeros((int(height), int(width), 3), np.uint8)

    (x, y, w, h) = (0, 0, 0, 0)
    (fx, fy, fw, fh) = (0, 0, 0, 0)
    (ox, oy) = (0, 0)
    random_colours = (255*abs(np.random.randn(255, 3))).astype(int)
    color_index = 0
    start_time = 0

    # Choosing the window for displaying depending upon tracker
    if tracker.get() == 'hsv' or tracker.get() == 'thresh':
        lmain = Label(hsv_tracker_window)
        lmain.grid(row=0, column=0)
    else:
        lmain = Label(tracker_window)
        lmain.grid(row=0, column=0)

    # Function for showing the frames of input continously
    # Like an infinite while loop collecting frames one by one and performing the required operation on each frame
    def show_frame():
        # making the variables global in the program so that they can be manipulated from any function
        global frame
        global fx, fy, fw, fh, x, y, w, h, ox, oy
        global collection, draw
        global pos_x, pos_y
        global dlib_tracking, dlib_tracker
        global cv2image
        global startX, startY, endX, endY
        global initialization_hsv
        global h1w, s1w, v1w, h2w, s2w, v2w
        global cx, cy, fcx, fcy

        # getting the frames from input device 
        ret, frame = cap.read()

        # Histogram equaliztion
        # Used when there is uneven distribution of light
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
        # # equalize the histogram of the Y channel
        # frame[:,:,0] = cv2.equalizeHist(frame[:,:,0])
        # # convert the YUV image back to RGB format
        # frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR)

        # gamma transformation
        # Can be used when the brightness is very less
        # frame = gamma_transform(frame,2)

        # Resizing the frame window
        # frame = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_LINEAR)


        if ret == True:
            color_index = 0

            # flip the frame if the input device is webcam
            if camera.get() == 0:
                frame = cv2.flip(frame, 1)

            # Execute the certain set of logic if the tracker selected is dlib from other algorithms
            if tracker.get() == 'dlib':
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if dlib_tracking:
                    dlib_tracker.update(cv2image)
                    pos = dlib_tracker.get_position()
                    x = int(pos.left())
                    y = int(pos.top())
                    endX = int(pos.right())
                    endY = int(pos.bottom())
                    w = endX-x
                    h = endY-y
                    cv2.rectangle(cv2image, (x, y),
                                  (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(cv2image, (int(x+w/2), int(y+h/2)),
                               4, (255, 255, 0), -1)

                    # draws the x and the y axis on the frame
                    if draw == True:
                        cv2.line(cv2image, (0, int(fy+fh/2)),
                                 (int(width), int(fy+fh/2)), (255, 0, 0), 3)
                        cv2.line(cv2image, (int(fx+fw/2), 0),
                                 (int(fx+fw/2), int(height)), (255, 0, 0), 3)
                        cv2.line(black_background, (0, int(fy+fh/2)),
                                 (int(width), int(fy+fh/2)), (255, 0, 0), 3)
                        cv2.line(black_background, (int(fx+fw/2), 0),
                                 (int(fx+fw/2), int(height)), (255, 0, 0), 3)
                    
                    # Collects the postion of center(x,y) of the particles 
                    if collection == True:
                        pos_x.append(((x+w/2)-ox))
                        pos_y.append((oy-(y+h/2)))
                        cv2.circle(black_background, (int(x+w/2),
                                                      int(y+h/2)), 2, (255, 255, 255), -1)

            # Execute the certain set of logic if the tracker selected is hsv or thresholding from other algorithms
            elif tracker.get() == 'hsv' or tracker.get() == 'thresh':
                if int(var_c1_hsv.get()) == 1:
                    # change the parameters of gaussian blurring
                    # 11 is the kernel size 11 and 20 can be changed
                    frame = cv2.GaussianBlur(frame, (11, 11), 20)

                frame_copy = frame.copy()

                # Logic if the tracker is hsv
                if tracker.get() == 'hsv':
                    spin1_hsv_tracker.configure(state=DISABLED)
                    combo2.configure(state=DISABLED)

                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    lower_range = np.array([h1w, s1w, v1w])
                    upper_range = np.array([h2w, s2w, v2w])
                    mask = cv2.inRange(hsv, lower_range, upper_range)
                
                # logic if the tracker is thresholding
                else:
                    spin1_hsv_tracker.configure(state=NORMAL)
                    combo2.configure(state=NORMAL)

                    try:
                        spin_value = int(spin1_hsv_tracker.get())
                    except:
                        spin_value = 127
                    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    if combo2.get() == 'THRESH_BINARY':
                        _, mask = cv2.threshold(
                            grayscale, spin_value, 255, cv2.THRESH_BINARY)
                    if combo2.get() == 'THRESH_BINARY_INV':
                        _, mask = cv2.threshold(
                            grayscale, spin_value, 255, cv2.THRESH_BINARY_INV)
                    if combo2.get() == 'THRESH_TRUNC':
                        _, mask = cv2.threshold(
                            grayscale, spin_value, 255, cv2.THRESH_TRUNC)
                    if combo2.get() == 'THRESH_TOZERO':
                        _, mask = cv2.threshold(
                            grayscale, spin_value, 255, cv2.THRESH_TOZERO)
                    if combo2.get() == 'THRESH_TOZERO_INV':
                        _, mask = cv2.threshold(
                            grayscale, spin_value, 255, cv2.THRESH_TOZERO_INV)

                    # play with block size and C
                    if combo2.get() == 'ADAPTIVE_MEAN':
                        mask = cv2.adaptiveThreshold(
                            grayscale, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
                    if combo2.get() == 'ADAPTIVE_GAUSSIAN':
                        mask = cv2.adaptiveThreshold(
                            grayscale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                    if combo2.get() == 'OTSU':
                        _, mask = cv2.threshold(
                            grayscale, spin_value, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

                try:
                    kernel = int(entry2_hsv_tracker.get())
                    kernelforerosion = np.ones((kernel, kernel), np.uint8)
                except:
                    kernelforerosion = np.ones((5, 5), np.uint8)
                
                # morphological transformations common for both hsv and thresholding tracker
                if combo1.get() == 'erosion':
                    try:
                        mask = cv2.erode(mask, kernelforerosion, iterations=int(
                            entry3_hsv_tracker.get()))
                    except:
                        mask = cv2.erode(mask, kernelforerosion, iterations=1)
                    entry3_hsv_tracker.configure(state=NORMAL)
                if combo1.get() == 'dilation':
                    try:
                        mask = cv2.dilate(mask, kernelforerosion, iterations=int(
                            entry3_hsv_tracker.get()))
                    except:
                        mask = cv2.dilate(mask, kernelforerosion, iterations=1)
                    entry3_hsv_tracker.configure(state=NORMAL)
                if combo1.get() == 'opening':
                    mask = cv2.morphologyEx(
                        mask, cv2.MORPH_OPEN, kernelforerosion)
                    entry3_hsv_tracker.configure(state=DISABLED)
                if combo1.get() == 'closing':
                    mask = cv2.morphologyEx(
                        mask, cv2.MORPH_CLOSE, kernelforerosion)
                    entry3_hsv_tracker.configure(state=DISABLED)

                result = cv2.bitwise_and(frame_copy, frame_copy, mask=mask)
                _, contours, _ = cv2.findContours(
                    mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                try:
                    comparision_area = int(entry1_hsv_tracker.get())
                except:
                    comparision_area = 0

                # Selecting contours above a certain area
                if int(var_c2_hsv.get()) == 0:
                    for i, contour in enumerate(contours):
                        area = cv2.contourArea(contour)
                        if (area > comparision_area):
                            frameswithcontours = cv2.drawContours(
                                frame_copy, contours, i, (0, 255, 0), 2)
                            result = cv2.drawContours(
                                result, contours, i, (0, 255, 0), 2)
                            cnt = contours[i]
                            M = cv2.moments(cnt)
                            cx = int(M['m10']/M['m00'])
                            cy = int(M['m01']/M['m00'])
                            cv2.circle(frameswithcontours,
                                       (cx, cy), 4, (255, 0, 0), -1)
                            cv2.circle(result, (cx, cy), 4, (255, 0, 0), -1)

                # Selecting cotour with the maximum area
                else:
                    if len(contours) > 0:
                        # c is the contour with the maximum area
                        c, max_area = maximum_contour_area(contours)
                        # draw only if above a certain threshold
                        if(max_area > comparision_area):
                            frameswithcontours = cv2.drawContours(
                                frame_copy, c, -1, (0, 255, 0), 4)
                            result = cv2.drawContours(
                                result, c, -1, (0, 255, 0), 4)
                            # (x, y), radius = cv2.minEnclosingCircle(c)
                            M = cv2.moments(c)
                            cx = int(M['m10']/M['m00'])
                            cy = int(M['m01']/M['m00'])
                            # cv2.circle(result, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                            cv2.circle(frameswithcontours,
                                       (cx, cy), 5, (0, 0, 255), -1)
                            cv2.circle(result, (cx, cy), 5, (0, 0, 255), -1)

                if int(var_c3_hsv.get()) == 0:
                    try:
                        cv2image = cv2.cvtColor(
                            frameswithcontours, cv2.COLOR_BGR2RGB)
                    except:
                        cv2image = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)

                else:
                    cv2image = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

                if draw == True:
                    cv2.line(cv2image, (0, int(fcy)),
                             (int(width), int(fcy)), (255, 0, 0), 3)
                    cv2.line(cv2image, (int(fcx), 0),
                             (int(fcx), int(height)), (255, 0, 0), 3)
                    cv2.line(black_background, (0, int(fcy)),
                             (int(width), int(fcy)), (255, 0, 0), 3)
                    cv2.line(black_background, (int(fcx), 0),
                             (int(fcx), int(height)), (255, 0, 0), 3)

                if collection == True:
                    pos_x.append((cx-ox))
                    pos_y.append((oy-cy))
                    cv2.circle(black_background, (int(cx), int(cy)),
                               2, (255, 255, 255), -1)

            # Execute the certain set of logic if the tracker selected is from the trackers submenu
            else:
                (_, boxes) = trackers.update(frame)
                for box in boxes:
                    color_index += 1
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (int(random_colours[color_index][0]), int(
                        random_colours[color_index][1]), int(random_colours[color_index][2])), 2)
                    cv2.circle(frame, (int(x+w/2), int(y+h/2)), 4, (int(random_colours[color_index][0]), int(
                        random_colours[color_index][1]), int(random_colours[color_index][2])), -1)

                    if draw == True:
                        cv2.line(frame, (0, int(fy+fh/2)),
                                 (int(width), int(fy+fh/2)), (255, 0, 0), 3)
                        cv2.line(frame, (int(fx+fw/2), 0),
                                 (int(fx+fw/2), int(height)), (255, 0, 0), 3)
                        cv2.line(black_background, (0, int(fy+fh/2)),
                                 (int(width), int(fy+fh/2)), (255, 0, 0), 3)
                        cv2.line(black_background, (int(fx+fw/2), 0),
                                 (int(fx+fw/2), int(height)), (255, 0, 0), 3)

                    if collection == True:
                        pos_x.append(((x+w/2)-ox))
                        pos_y.append((oy-(y+h/2)))
                        cv2.circle(black_background, (int(x+w/2),
                                                      int(y+h/2)), 2, (255, 255, 255), -1)

                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img = PIL.Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
            if pause % 2 == 0:
                lmain.after(10, show_frame)
            else:
                lmain.after(0, show_frame)

    show_frame()

    # Function for pausing the video
    # This function is called when pause button is pressed in tracker window
    def pausing():
        global pause
        pause = pause+1

    # Function for selecting the object for tracking by drawing the bounding box
    # This function is called when select button is pressed in the tracker window
    def select():
        global frame
        global dlib_tracking, dlib_tracker
        global cv2image
        global startX, startY, endX, endY

        if tracker.get() == 'dlib':
            dlib_tracking = True
            initBoundingBox = cv2.selectROI(
                "Selector", frame, fromCenter=False, showCrosshair=True)
            cv2.destroyWindow('Selector')
            (x1, y1, w1, h1) = initBoundingBox
            (startX, startY, endX, endY) = (x1, y1, x1+w1, y1+h1)
            rect = dlib.rectangle(startX, startY, endX, endY)
            dlib_tracker.start_track(cv2image, rect)
            cv2.rectangle(frame, (startX, startY),
                          (endX, endY), (0, 255, 0), 2)
            button3_tracking.configure(state=NORMAL)

        else:
            box = cv2.selectROI("Selector", frame, fromCenter=False,
                                showCrosshair=True)
            tracker_trackingwindow = Tracker_used
            trackers.add(tracker_trackingwindow, frame, box)
            cv2.destroyWindow('Selector')
            button3_tracking.configure(state=NORMAL)

    # Function enables drawing of axis and storing of coordinates
    # Marks the official beginning of tracking
    # This function is called when select Draw and collect button is pressed in the tracker window
    def drawing():
        global fx, fy, fw, fh, x, y, w, h, ox, oy
        global start_time
        global collection, draw
        global pos_x, pos_y
        global fcx, fcy, cx, cy
        print("Drawing the reference coordinates")

        if tracker.get() == 'hsv':
            fcx = cx
            fcy = cy
            (ox, oy) = (cx, cy)
        else:
            fx = x
            fy = y
            fw = w
            fh = h
            (ox, oy) = (x+w/2, y+h/2)

        draw = True
        collection = True
        start_time = time.time()
        pos_x = []
        pos_y = []

#########################################################################################################
# SAVE WINDOW STARTS
    # This function is called once exit button in the tracker window is pressed
    # This opens up a new window and asks for save location and name of files
    def exitt():
        global end_time, total_time
        end_time = time.time()
        total_time = end_time-start_time
        print(pos_x)
        print(pos_y)
        cap.release()

        # destroy the particular tracker window depending upon the tracker
        if tracker.get() == 'hsv':
            hsv_tracker_window.destroy()
        else:
            tracker_window.destroy()

        # creating the save window
        save_window = Toplevel()
        save_window.geometry("600x300")  # width*height
        save_window.title("Tracking Window")
        save_window.resizable(width=FALSE, height=FALSE)

        # This function is called when select button is pressed in the save window
        # This function is used for selecting the save directory
        def directory_select():
            global save_path
            save_path = filedialog.askdirectory()

            # Logic for enabling and disabling save button in save window
            if save_path == '':
                button2_saving.configure(state=DISABLED)
            else:
                button2_saving.configure(state=NORMAL)

        # This function is called when save button is clicked
        # This function is used to save the files in the required destination
        def saving_the_files():
            path_x = save_path + '//' + entry1_save_window.get()
            path_y = save_path + '//' + entry2_save_window.get()
            path_background = save_path + '//' + entry3_save_window.get()
            path_time = save_path + '//' + entry4_save_window.get()

            np.save(path_x, pos_x)
            np.save(path_y, pos_y)
            np.save(path_time, total_time)
            cv2.imwrite(path_background, black_background)
            tkinter.messagebox.showinfo("Saving", "Done Saving")

        # Save window widgets
        label1_save_window = Label(save_window, text='If You Want to save the data then select the directory \n  Enter The Name of the files along with Extensions',
                                   fg='red', bg='yellow', font=("arial", 16, "bold"), relief='solid')
        label1_save_window.pack()

        button1_saving = Button(save_window, text="Directory", bg="orange", fg="black",
                                command=directory_select, state=NORMAL, font=("arial", 10, "bold"), relief='solid',
                                width=15)
        button1_saving.pack()

        label3_save_window = Label(save_window, text='X Values',
                                   fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
        label3_save_window.place(x=20, y=120)
        label4_save_window = Label(save_window, text='Y Values',
                                   fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
        label4_save_window.place(x=20, y=150)
        label5_save_window = Label(save_window, text='Background Image',
                                   fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
        label5_save_window.place(x=20, y=180)
        label6_save_window = Label(save_window, text='Time Taken',
                                   fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
        label6_save_window.place(x=20, y=210)

        entry1_save_window = Entry(save_window, width=30)
        entry1_save_window.place(x=180, y=120)
        entry1_save_window.insert(END, 'X.npy')
        entry2_save_window = Entry(save_window, width=30)
        entry2_save_window.place(x=180, y=150)
        entry2_save_window.insert(END, 'Y.npy')
        entry3_save_window = Entry(save_window, width=30)
        entry3_save_window.place(x=180, y=180)
        entry3_save_window.insert(END, 'Back.jpg')
        entry4_save_window = Entry(save_window, width=30)
        entry4_save_window.place(x=180, y=210)
        entry4_save_window.insert(END, 'T.npy')

        button2_saving = Button(save_window, text="Save", bg="orange", fg="black",
                                command=saving_the_files, state=DISABLED, font=("arial", 10, "bold"), relief='solid',
                                width=15)
        button2_saving.place(x=230, y=250)

# SAVE WINDOW ENDS
#########################################################################################################

    # Disabling cross in the tracker window so that user uses exit button which leads to save window
    def disable_cross():
        tkinter.messagebox.showerror("EXIT", "Please Exit Using Exit Button")
    
    # tracker window widgets depending for hsv or thresholding tracking
    if tracker.get() == 'hsv' or tracker.get() == 'thresh':
        button1_tracking_hsv = Button(hsv_tracker_window, text="Pause\ \n Continue", bg="orange", fg="black",
                                      command=pausing, state=NORMAL, font=("arial", 10, "bold"), relief='solid',
                                      width=15)
        button1_tracking_hsv.place(x=30, y=500)

        button2_tracking_hsv = Button(hsv_tracker_window, text="Exit", bg="orange", fg="black",
                                      command=exitt, state=NORMAL, font=("arial", 10, "bold"), relief='solid',
                                      width=15)
        button2_tracking_hsv.place(x=30, y=600)

        button3_tracking_hsv = Button(hsv_tracker_window, text="Draw And \n Collect Data", bg="orange", fg="black",
                                      command=drawing, state=NORMAL, font=("arial", 10, "bold"), relief='solid',
                                      width=15)
        button3_tracking_hsv.place(x=30, y=550)

        c1_hsv = Checkbutton(hsv_tracker_window,
                             text='Gaussian Blur', variable=var_c1_hsv)
        c1_hsv.place(x=560, y=500)

        c2_hsv = Checkbutton(hsv_tracker_window,
                             text='Maximum Area Mode', variable=var_c2_hsv)
        c2_hsv.place(x=560, y=550)

        c3_hsv = Checkbutton(hsv_tracker_window,
                             text='Only Object', variable=var_c3_hsv)
        c3_hsv.place(x=560, y=600)

        label1_hsvwindow = Label(hsv_tracker_window, text='Area',
                                 fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
        label1_hsvwindow.place(x=200, y=500)
        label2_hsvwindow = Label(hsv_tracker_window, text='Kernel Value',
                                 fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
        label2_hsvwindow.place(x=200, y=550)
        label3_hsvwindow = Label(hsv_tracker_window, text='Morphological Transformation',
                                 fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
        label3_hsvwindow.place(x=200, y=600)

        label4_hsvwindow = Label(hsv_tracker_window, text='Iterations',
                                 fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
        label4_hsvwindow.place(x=200, y=650)

        label5_hsvwindow = Label(hsv_tracker_window, text='Thresholding Options',
                                 fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
        label5_hsvwindow.place(x=200, y=700)

        label6_hsvwindow = Label(hsv_tracker_window, text='Threshold',
                                 fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
        label6_hsvwindow.place(x=500, y=700)

        hsv_tracker_window.protocol("WM_DELETE_WINDOW", disable_cross)
        hsv_tracker_window.mainloop()
    # tracker window widgets for all the tracker in the trackers submenu
    else:
        button1_tracking = Button(tracker_window, text="Pause\ \n Continue", bg="orange", fg="black",
                                  command=pausing, state=NORMAL, font=("arial", 10, "bold"), relief='solid',
                                  width=15)
        button1_tracking.place(x=120, y=620)
        button2_tracking = Button(tracker_window, text="Select", bg="orange", fg="black",
                                  command=select, state=NORMAL, font=("arial", 10, "bold"), relief='solid',
                                  width=15)
        button2_tracking.place(x=270, y=620)
        button3_tracking = Button(tracker_window, text="Draw And \n Collect Data", bg="orange", fg="black",
                                  command=drawing, state=DISABLED, font=("arial", 10, "bold"), relief='solid',
                                  width=15)
        button3_tracking.place(x=420, y=620)
        # Always use exit for exiting the program
        button4_tracking = Button(tracker_window, text="Exit", bg="orange", fg="black",
                                  command=exitt, state=NORMAL, font=("arial", 10, "bold"), relief='solid',
                                  width=15)
        button4_tracking.place(x=570, y=620)

        tracker_window.protocol("WM_DELETE_WINDOW", disable_cross)
        tracker_window.mainloop()

# TRACKER WINDOW ENDS
#########################################################################################################

# This function is used for enabling and disabling widgets
# Some widgets or buttons remain disabled unless certain buttons are pressed
def switch():
    if camera.get() == 1:
        spinbox1_main.configure(state=DISABLED)
        if load_path == '':
            other_algorithms.entryconfig(1, state=DISABLED)
        else:
            other_algorithms.entryconfig(1, state=NORMAL)
        if enable_tracking == True:
            button1_main.configure(state=NORMAL)
        else:
            button1_main.configure(state=DISABLED)
    else:
        spinbox1_main.configure(state=NORMAL)
        button1_main.configure(state=NORMAL)
        other_algorithms.entryconfig(1, state=NORMAL)

#########################################################################################################
# VALUE PLOTTER WINDOW STARTS

# This function is used for plotting the values of postions of the tracked particles
# This function opens a new window
# This function is called when value plotter button is clicked in the main window
def Value_Plotter():

    # creation of new window
    value_plotter_window = Toplevel()
    value_plotter_window.geometry("400x250")  # width*height
    value_plotter_window.title("Plotting Window")
    value_plotter_window.resizable(width=FALSE, height=FALSE)

    # This function is called when select x values button is clicked
    # It is used select the x values saved in the computer
    # It opens a dialog box to choose the file
    def value_plotter_x_values():
        global load_path_x_plotter, enable_plot, loaded_X
        load_path_x_plotter = askopenfilename(
            initialdir="/", title="Select X values")
        if load_path_x_plotter != '':
            enable_plot += 1
        if enable_plot == 2:
            button4_value_plotter.configure(state=NORMAL)
        loaded_X = np.load(load_path_x_plotter)

    # This function is called when select y values button is clicked
    # It is used select the y values saved in the computer
    # It opens a dialog box to choose the file    
    def value_plotter_y_values():
        global load_path_y_plotter, enable_plot, loaded_Y
        load_path_y_plotter = askopenfilename(
            initialdir="/", title="Select Y values")
        if load_path_y_plotter != '':
            enable_plot += 1
        if enable_plot == 2:
            button4_value_plotter.configure(state=NORMAL)
        loaded_Y = np.load(load_path_y_plotter)

    # This function is called when select time values button is clicked
    # It is used select the time values saved in the computer
    # It opens a dialog box to choose the file    
    def value_plotter_time_values():
        global load_path_time_plotter, loaded_time
        load_path_time_plotter = askopenfilename(
            initialdir="/", title="Select time values")
        if load_path_time_plotter != '':
            checkbutton1_value_plotter.configure(state=NORMAL)
        loaded_time = np.load(load_path_time_plotter)

    # This function is used to display the matplotlib graph
    # This function is called when plot button is clicked
    def value_plot():
        X_values = loaded_X
        Y_values = loaded_Y
        timeforxaxis = loaded_time
        x_label = ''
        plot_title_x = ''
        plot_title_y = ''

        if var_c1.get() == '0':
            x_axis = np.arange(1, (len(X_values)+1), 1)
            x_label = 'frames'
            plot_title_x = 'X coordinates vs Frames'
            plot_title_y = 'Y coordinates vs Frames'
        else:
            x_axis = np.linspace(1, (timeforxaxis+1), len(X_values))
            x_label = 'time(s)'
            plot_title_x = 'X coordinates vs Time'
            plot_title_y = 'Y coordinates vs Time'

        fig1 = plt.figure(figsize=(12, 7))
        fig1.subplots_adjust(hspace=0.5, wspace=0.2)

        plt.subplot(3, 2, 1)
        plt.plot(x_axis, X_values)
        plt.xlabel(x_label)
        plt.ylabel('X coordinates')
        plt.title(plot_title_x)

        plt.subplot(3, 2, 3)
        plt.scatter(x_axis, X_values)
        plt.xlabel(x_label)
        plt.ylabel('X coordinates')
        plt.title(plot_title_x + ' scatter plot')

        plt.subplot(3, 2, 5)
        plt.hist(X_values, color='blue', edgecolor='black', bins=len(X_values))
        plt.xlabel('X coordinates')
        plt.ylabel('Count')
        plt.title('Histogram of X coordinates')

        plt.subplot(3, 2, 2)
        plt.plot(x_axis, Y_values)
        plt.xlabel(x_label)
        plt.ylabel('Y coordinates')
        plt.title(plot_title_y)

        plt.subplot(3, 2, 4)
        plt.scatter(x_axis, Y_values)
        plt.xlabel(x_label)
        plt.ylabel('Y coordinates')
        plt.title(plot_title_y + ' scatter plot')

        plt.subplot(3, 2, 6)
        plt.hist(Y_values, color='blue', edgecolor='black', bins=len(X_values))
        plt.xlabel('Y coordinates')
        plt.ylabel('Count')
        plt.title('Histogram of Y coordinates')

        plt.show()

    # plotter window widgets
    label1_value_plotter = Label(value_plotter_window, text='Select The X and Y values for Plotting',
                                 fg='red', bg='yellow', font=("arial", 16, "bold"), relief='solid')
    label1_value_plotter.pack()
    button1_value_plotter = Button(value_plotter_window, text="Select X values", bg="orange", fg="black",
                                   command=value_plotter_x_values, state=NORMAL, width=20,
                                   font=("arial", 10, "bold"))
    button1_value_plotter.place(x=120, y=50)
    button2_value_plotter = Button(value_plotter_window, text="Select Y Values", bg="orange", fg="black",
                                   command=value_plotter_y_values, state=NORMAL, width=20,
                                   font=("arial", 10, "bold"))
    button2_value_plotter.place(x=120, y=100)
    button3_value_plotter = Button(value_plotter_window, text="Select Time Values", bg="orange", fg="black",
                                   command=value_plotter_time_values, state=NORMAL, width=20,
                                   font=("arial", 10, "bold"))
    button3_value_plotter.place(x=120, y=150)
    button4_value_plotter = Button(value_plotter_window, text="Plot", bg="orange", fg="black",
                                   command=value_plot, state=DISABLED, width=20,
                                   font=("arial", 10, "bold"))
    button4_value_plotter.place(x=120, y=200)

    checkbutton1_value_plotter = Checkbutton(value_plotter_window, text='Vs Time', variable=var_c1,
                                             state=DISABLED)
    checkbutton1_value_plotter.place(x=300, y=150)

# PLOTTER WINDOW ENDS
#########################################################################################################


#########################################################################################################
# ALLAN DEVIATION PLOTTER WINDOW STARTS

# This function is used for plotting the allan deviation 
# This function is called when ADEV plotter button is clicked on the main window
def Allan_Deviation_Plotter():
    ad_plotter_window = Toplevel()
    ad_plotter_window.geometry("400x350")  # width*height
    ad_plotter_window.title("Plotting Window")
    ad_plotter_window.resizable(width=FALSE, height=FALSE)

    tau1 = np.logspace(0, 4, 1000)

    # This function is used for selecting the values whose allan deviation is to be plotted
    # This function is called when select values button is clicked in ad pltter window
    def value_adplotter():
        global adplotter_path, adplotter_values
        adplotter_path = askopenfilename(initialdir="/", title="Select Values")
        if adplotter_path != '':
            button2_adplotter.configure(state=NORMAL)
            adplotter_values = np.load(adplotter_path)
            plt.grid(color='red')

    # This function is used for plotting the allan deviation and displaying the matplotlib graph
    # This function is called when plot allan deviation button is clicked in the ad plotter window
    def plot_adplotter():
        try:
            rate = int(entry1_adplotter.get())
            if value_type.get() == 0:
                title = 'Allan Deviation for X values'
            elif value_type.get() == 1:
                title = 'Allan Deviation for Y values'
            (tau2, ad, _, _) = allantools.oadev(
                adplotter_values, rate=rate, data_type="freq", taus=tau1)

            idx_min = np.argmin(ad)
            idx_max = np.argmax(ad)
            allandeviation_minimum_value = ad[idx_min]
            allandeviation_maximum_value = ad[idx_max]
            tau_min = tau2[idx_min]
            tau_max = tau2[idx_max]

            # index of array t2 where the value is 1s.
            t21_ind1 = np.where(tau2 == 1.0)
            noise = ad[t21_ind1[0]]
            # noise density is value of ADEV curve at 1s averaging time.

            # Ad plotter window widgets for displaying some values
            label8_adplotter.configure(text=str(allandeviation_minimum_value))
            label9_adplotter.configure(text=str(allandeviation_maximum_value))
            label10_adplotter.configure(text=str(tau_min))
            label11_adplotter.configure(text=str(tau_max))
            label12_adplotter.configure(text=str(noise))

            plt.loglog(tau2, ad, c=np.random.rand(3,))
            plt.title(title)
            plt.xlabel('tau')
            plt.ylabel('ADEV [V]')
            plt.show()

        except:
            tkinter.messagebox.showerror(
                'Rate Error', 'Choose a larger or a smaller rate')

    # Allan deviation plotter window widgets
    label1_adplotter = Label(ad_plotter_window, text='Select X or Y for Allan Deviation',
                             fg='red', bg='yellow', font=("arial", 16, "bold"), relief='solid')
    label1_adplotter.pack()

    radiobutton1_adplotter = Radiobutton(ad_plotter_window, text='Use X', variable=value_type,
                                         value=0)
    radiobutton1_adplotter.place(x=100, y=30)
    radiobutton2_adplotter = Radiobutton(ad_plotter_window, text='Use Y', variable=value_type,
                                         value=1)
    radiobutton2_adplotter.place(x=240, y=30)

    button1_adplotter = Button(ad_plotter_window, text="Select Values", bg="orange", fg="black",
                               command=value_adplotter, state=NORMAL, width=20,
                               font=("arial", 10, "bold"))
    button1_adplotter.place(x=30, y=70)
    button2_adplotter = Button(ad_plotter_window, text="Plot Allan \n Deviation", bg="orange", fg="black",
                               command=plot_adplotter, state=DISABLED, width=20,
                               font=("arial", 10, "bold"))
    button2_adplotter.place(x=110, y=110)

    entry1_adplotter = Entry(ad_plotter_window, width=4)
    entry1_adplotter.place(x=280, y=70)
    entry1_adplotter.insert(END, '20')

    label2_adplotter = Label(ad_plotter_window, text='Rate : ',
                             fg='red', bg='yellow', font=("arial", 10, "bold"), relief='solid')
    label2_adplotter.place(x=220, y=70)

    label3_adplotter = Label(ad_plotter_window, text='The minimum value for allan deviation : ',
                             fg='red', bg='yellow', font=("arial", 8, "bold"), relief='solid')
    label3_adplotter.place(x=10, y=200)
    label4_adplotter = Label(ad_plotter_window, text='The maximum value for allan deviation : ',
                             fg='red', bg='yellow', font=("arial", 8, "bold"), relief='solid')
    label4_adplotter.place(x=10, y=230)
    label5_adplotter = Label(ad_plotter_window, text='The tau at which lowest value occurs : ',
                             fg='red', bg='yellow', font=("arial", 8, "bold"), relief='solid')
    label5_adplotter.place(x=10, y=260)
    label6_adplotter = Label(ad_plotter_window, text='The tau at which maximum value occurs : ',
                             fg='red', bg='yellow', font=("arial", 8, "bold"), relief='solid')
    label6_adplotter.place(x=10, y=290)
    label7_adplotter = Label(ad_plotter_window, text='Noise spectral density : ',
                             fg='red', bg='yellow', font=("arial", 8, "bold"), relief='solid')
    label7_adplotter.place(x=10, y=320)

    label8_adplotter = Label(ad_plotter_window, text='',
                             fg='red', bg='yellow', font=("arial", 8, "bold"), relief='solid')
    label8_adplotter.place(x=250, y=200)
    label9_adplotter = Label(ad_plotter_window, text='',
                             fg='red', bg='yellow', font=("arial", 8, "bold"), relief='solid')
    label9_adplotter.place(x=250, y=230)
    label10_adplotter = Label(ad_plotter_window, text='',
                              fg='red', bg='yellow', font=("arial", 8, "bold"), relief='solid')
    label10_adplotter.place(x=250, y=260)
    label11_adplotter = Label(ad_plotter_window, text='',
                              fg='red', bg='yellow', font=("arial", 8, "bold"), relief='solid')
    label11_adplotter.place(x=250, y=290)
    label12_adplotter = Label(ad_plotter_window, text='',
                              fg='red', bg='yellow', font=("arial", 8, "bold"), relief='solid')
    label12_adplotter.place(x=250, y=320)

    ad_plotter_window.mainloop()
# ALLAN DEVIATION PLOTTER WINDOW ENDS
#########################################################################################################

# main window widgets
label1_main = Label(main_window, text='Please Read The Use Instructions in Help Menu',
                    fg='red', bg='yellow', font=("arial", 16, "bold"), relief='solid')
label1_main.pack()
button1_main = Button(main_window, text="Start Tracking", bg="orange", fg="black",
                      command=StartTracking, state=NORMAL, width=20,
                      font=("arial", 10, "bold"))
button1_main.pack()
radiobutton1_main = Radiobutton(main_window, text='Use Webcam', variable=camera,
                                value=0, command=switch)
radiobutton1_main.pack()
radiobutton2_main = Radiobutton(main_window, text='Use video', variable=camera,
                                value=1, command=switch)
radiobutton2_main.pack()
spinbox1_main = Spinbox(main_window, from_=0, to=5, width=2)
spinbox1_main.place(x=300, y=60)
button2_main = Button(main_window, text="Value Plotter", bg="orange", fg="black",
                      command=Value_Plotter, state=NORMAL, width=20,
                      font=("arial", 10, "bold"))
button2_main.place(x=50, y=110)

button3_main = Button(main_window, text="ADEV Plotter", bg="orange", fg="black",
                      command=Allan_Deviation_Plotter, state=NORMAL, width=20,
                      font=("arial", 10, "bold"))
button3_main.place(x=280, y=110)

# Creating the menu in the main window
menu = Menu(main_window)
main_window.config(menu=menu)

file_menu = Menu(menu)
# Adding the menu option
menu.add_cascade(label='File', menu=file_menu)
# adding the file submenu
file_menu.add_command(label="Open", command=OpenFile)
file_menu.add_command(label="Save", command=SaveFile)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=main_window.quit)

# adding the tracker submenu
trackers_menu = Menu(menu)
menu.add_cascade(label="Trackers", menu=trackers_menu)
trackers_menu.add_radiobutton(label="CSRT", command=TrackerChooser,
                              variable=tracker, value="csrt")
trackers_menu.add_radiobutton(label="KCF", command=TrackerChooser,
                              variable=tracker, value="kcf")
trackers_menu.add_radiobutton(label="BOOSTING", command=TrackerChooser,
                              variable=tracker, value="boosting")
trackers_menu.add_radiobutton(label="MIL", command=TrackerChooser,
                              variable=tracker, value="mil")
trackers_menu.add_radiobutton(label="TLD", command=TrackerChooser,
                              variable=tracker, value="tld")
trackers_menu.add_radiobutton(label="MEDIANFLOW", command=TrackerChooser,
                              variable=tracker, value="medianflow")
trackers_menu.add_radiobutton(label="MOSSE", command=TrackerChooser,
                              variable=tracker, value="mosse")

# adding the other algorithms submenu
other_algorithms = Menu(menu)
menu.add_cascade(label="Other Algorithms", menu=other_algorithms)
other_algorithms.add_radiobutton(label="HSV Tracking", command=otherAlgorithmChooser,
                                 variable=tracker, value="hsv", state=NORMAL)
other_algorithms.add_radiobutton(label="Dlib Coorelation", command=otherAlgorithmChooser,
                                 variable=tracker, value="dlib")
# other_algorithms.add_radiobutton(label="Optical Flow", command=otherAlgorithmChooser,
#                                  variable=tracker, value="optical")
other_algorithms.add_radiobutton(label="Thresholding", command=otherAlgorithmChooser,
                                 variable=tracker, value="thresh")

# adding the help submenu
help_menu = Menu(menu)
menu.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Use Instrcutions", command=Use)
help_menu.add_command(label="Tracker Info ", command=Info)
help_menu.add_command(label="About", command=About)

main_window.resizable(width=FALSE, height=FALSE)
main_window.mainloop()

# MAIN WINDOW ENDS
#########################################################################################################
