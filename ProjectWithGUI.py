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
#########################################################################################################

#########################################################################################################
# MAIN WINDOW STARTS
main_window = Tk()
main_window.geometry("500x150")
main_window.title("Tracking Program")


def center_window(width=300, height=200):
    # get screen width and height
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    main_window.geometry('%dx%d+%d+%d' % (width, height, x, y))


center_window(500, 150)

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
# save window global variables

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


def maximum_contour_area(contour):
    maximum_area = cv2.contourArea(contour[0])
    maximum = contour[0]
    for i in range(1, len(contour)):
        if(cv2.contourArea(contour[i]) > maximum_area):
            maximum_area = cv2.contourArea(contour[i])
            maximum = contour[i]
    return maximum, maximum_area

# opening a file using a dialog box


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


def SaveFile():
    global save_path
    save_path = filedialog.askdirectory()
    print(save_path)


def About():
    about_window = Toplevel()
    about_window.geometry("500x500")
    about_window.title("About the Software")

    scrollbar = Scrollbar(about_window)
    editArea_about = Text(about_window, width=50, height=50, wrap="word",
                          yscrollcommand=scrollbar.set,
                          borderwidth=0, highlightthickness=0)

    text = '1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n'

    editArea_about.configure(state='normal')
    editArea_about.insert('end', text)
    editArea_about.configure(state='disabled')

    scrollbar.config(command=editArea_about.yview)
    scrollbar.pack(side="right", fill="y")
    editArea_about.pack(side="left", fill="both", expand=True)

    about_window.mainloop()


def Use():

    instructions_window = Toplevel()
    instructions_window.geometry("500x500")
    instructions_window.title("Use Instructions")

    scrollbar = Scrollbar(instructions_window)
    editArea_use = Text(instructions_window, width=50, height=50, wrap="word",
                        yscrollcommand=scrollbar.set,
                        borderwidth=0, highlightthickness=0)

    text = '1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n 1 \n'

    editArea_use.configure(state='normal')
    editArea_use.insert('end', text)
    editArea_use.configure(state='disabled')

    scrollbar.config(command=editArea_use.yview)
    scrollbar.pack(side="right", fill="y")
    editArea_use.pack(side="left", fill="both", expand=True)

    instructions_window.mainloop()


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
def StartTracking():

    global cap
    if tracker.get() == 'hsv' or tracker.get() == 'thresh':
        hsv_tracker_window = Toplevel()
        hsv_tracker_window.geometry("800x800")  # width*height
        if tracker.get() == 'hsv':
            hsv_tracker_window.title("HSV Tracking Window")
        else:
            hsv_tracker_window.title("Thresholding Tracking Window")

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

    trackers = cv2.MultiTracker_create()
    if camera.get() == 0:
        cap = cv2.VideoCapture(int(spinbox1_main.get()))
    elif camera.get() == 1:
        cap = cv2.VideoCapture(load_path)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

    width, height = cap.get(3), cap.get(4)
    black_background = np.zeros((int(height), int(width), 3), np.uint8)
    (x, y, w, h) = (0, 0, 0, 0)
    (fx, fy, fw, fh) = (0, 0, 0, 0)
    (ox, oy) = (0, 0)
    random_colours = (255*abs(np.random.randn(255, 3))).astype(int)
    color_index = 0
    start_time = 0

    if tracker.get() == 'hsv' or tracker.get() == 'thresh':
        lmain = Label(hsv_tracker_window)
        lmain.grid(row=0, column=0)
    else:
        lmain = Label(tracker_window)
        lmain.grid(row=0, column=0)

    def show_frame():
        global frame
        global fx, fy, fw, fh, x, y, w, h, ox, oy
        global collection, draw
        global pos_x, pos_y
        global dlib_tracking, dlib_tracker
        global cv2image
        global startX, startY, endX, endY
        # global cap
        global initialization_hsv
        global h1w, s1w, v1w, h2w, s2w, v2w
        global cx, cy, fcx, fcy

        ret, frame = cap.read()
        # frame = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_LINEAR)
        if ret == True:
            color_index = 0
            if camera.get() == 0:
                frame = cv2.flip(frame, 1)
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

                    if draw == True:
                        cv2.line(cv2image, (0, int(fy+fh/2)),
                                 (int(width), int(fy+fh/2)), (255, 0, 0), 3)
                        cv2.line(cv2image, (int(fx+fw/2), 0),
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

            elif tracker.get() == 'hsv' or tracker.get() == 'thresh':
                if int(var_c1_hsv.get()) == 1:
                    # change the parameters of gaussian blurring
                    frame = cv2.GaussianBlur(frame, (11, 11), 20)

                frame_copy = frame.copy()

                if tracker.get() == 'hsv':
                    spin1_hsv_tracker.configure(state=DISABLED)
                    combo2.configure(state=DISABLED)

                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    lower_range = np.array([h1w, s1w, v1w])
                    upper_range = np.array([h2w, s2w, v2w])
                    mask = cv2.inRange(hsv, lower_range, upper_range)
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

    # functions for buttons
    def pausing():
        global pause
        pause = pause+1

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
    def exitt():
        global end_time, total_time
        end_time = time.time()
        total_time = end_time-start_time
        print(pos_x)
        print(pos_y)
        cap.release()
        if tracker.get() == 'hsv':
            hsv_tracker_window.destroy()
        else:
            tracker_window.destroy()

        save_window = Toplevel()
        save_window.geometry("600x300")  # width*height
        save_window.title("Tracking Window")
        save_window.resizable(width=FALSE, height=FALSE)

        def directory_select():
            global save_path
            save_path = filedialog.askdirectory()
            if save_path == '':
                button2_saving.configure(state=DISABLED)
            else:
                button2_saving.configure(state=NORMAL)

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

    # disabling cross
    def disable_cross():
        tkinter.messagebox.showerror("EXIT", "Please Exit Using Exit Button")

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

# Logic for enabling and disabling boxes


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
def Value_Plotter():
    value_plotter_window = Toplevel()
    value_plotter_window.geometry("400x250")  # width*height
    value_plotter_window.title("Plotting Window")
    value_plotter_window.resizable(width=FALSE, height=FALSE)

    def value_plotter_x_values():
        global load_path_x_plotter, enable_plot, loaded_X
        load_path_x_plotter = askopenfilename(
            initialdir="/", title="Select X values")
        if load_path_x_plotter != '':
            enable_plot += 1
        if enable_plot == 2:
            button4_value_plotter.configure(state=NORMAL)
        loaded_X = np.load(load_path_x_plotter)

    def value_plotter_y_values():
        global load_path_y_plotter, enable_plot, loaded_Y
        load_path_y_plotter = askopenfilename(
            initialdir="/", title="Select Y values")
        if load_path_y_plotter != '':
            enable_plot += 1
        if enable_plot == 2:
            button4_value_plotter.configure(state=NORMAL)
        loaded_Y = np.load(load_path_y_plotter)

    def value_plotter_time_values():
        global load_path_time_plotter, loaded_time
        load_path_time_plotter = askopenfilename(
            initialdir="/", title="Select time values")
        if load_path_time_plotter != '':
            checkbutton1_value_plotter.configure(state=NORMAL)
        loaded_time = np.load(load_path_time_plotter)

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

def Allan_Deviation_Plotter():
    ad_plotter_window = Toplevel()
    ad_plotter_window.geometry("400x350")  # width*height
    ad_plotter_window.title("Plotting Window")
    ad_plotter_window.resizable(width=FALSE, height=FALSE)

    tau1 = np.logspace(0, 4, 1000)

    def value_adplotter():
        global adplotter_path, adplotter_values
        adplotter_path = askopenfilename(initialdir="/", title="Select Values")
        if adplotter_path != '':
            button2_adplotter.configure(state=NORMAL)
            adplotter_values = np.load(adplotter_path)
            plt.grid(color='red')

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

menu = Menu(main_window)
main_window.config(menu=menu)

file_menu = Menu(menu)
# Adding the menu option
menu.add_cascade(label='File', menu=file_menu)
# adding the submenus
file_menu.add_command(label="Open", command=OpenFile)
file_menu.add_command(label="Save", command=SaveFile)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=main_window.quit)

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

other_algorithms = Menu(menu)
menu.add_cascade(label="Other Algorithms", menu=other_algorithms)
other_algorithms.add_radiobutton(label="HSV Tracking", command=otherAlgorithmChooser,
                                 variable=tracker, value="hsv", state=NORMAL)
other_algorithms.add_radiobutton(label="Dlib Coorelation", command=otherAlgorithmChooser,
                                 variable=tracker, value="dlib")
other_algorithms.add_radiobutton(label="Optical Flow", command=otherAlgorithmChooser,
                                 variable=tracker, value="optical")
other_algorithms.add_radiobutton(label="Thresholding", command=otherAlgorithmChooser,
                                 variable=tracker, value="thresh")

help_menu = Menu(menu)
menu.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Use Instrcutions", command=Use)
help_menu.add_command(label="Tracker Info ", command=Info)
help_menu.add_command(label="About", command=About)

main_window.resizable(width=FALSE, height=FALSE)
main_window.mainloop()

# MAIN WINDOW ENDS
#########################################################################################################
