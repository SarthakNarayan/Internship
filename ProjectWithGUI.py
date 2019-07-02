import cv2
import tkinter
from tkinter import *
from PIL import Image , ImageTk
from tkinter.filedialog  import askopenfilename
from tkinter import filedialog
import numpy as np
import PIL
import time

#########################################################################################################
# Creating the main window with menu
main_window = Tk()
main_window.geometry("600x200")
main_window.title("Tracking Program")

#########################################################################################################
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
(fx,fy,fw,fh,x,y,w,h,ox,oy) = (0,0,0,0,0,0,0,0,0,0)
(start_time , end_time , total_time) = (0,0,0)
collection = False
draw = False
pos_x = []
pos_y = []   
#########################################################################################################

# setting values
camera.set(0)
spinbox1_main.set('0')
tracker.set('csrt')

# opening a file using a dialog box
def OpenFile():
    global load_path , enable_tracking
    load_path = askopenfilename(initialdir = "/",title = "Select file")
    print(load_path)
    enable_tracking = True
    button1_main.configure(state=NORMAL)

def SaveFile():
    global save_path
    save_path = filedialog.askdirectory()
    print(save_path)

def About():
    pass
def Use():
    pass
def Info():
    pass

def TrackerChooser():
    global tracker , Tracker_used
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


# Main Tracking Algorithm
def StartTracking():

    tracker_window = Toplevel()
    tracker_window.geometry("800x800") # width*height
    tracker_window.title("Tracking Window")

    trackers = cv2.MultiTracker_create()
    if camera.get() == 0:
        cap = cv2.VideoCapture(int(spinbox1_main.get()))
    elif camera.get() == 1:
        cap = cv2.VideoCapture(load_path)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

    width , height = cap.get(3) , cap.get(4)
    black_background = np.zeros((int(height),int(width),3),np.uint8)
    (x , y ,w , h) = (0,0,0,0)
    (fx , fy ,fw , fh) = (0,0,0,0)
    (ox , oy) = (0,0) 
    random_colours = (255*abs(np.random.randn(255,3))).astype(int)
    color_index = 0
    start_time = 0

    lmain = Label(tracker_window)
    lmain.grid(row = 0 , column = 0)

    def show_frame():
        global frame
        global fx,fy,fw,fh,x,y,w,h,ox,oy
        global collection , draw
        global pos_x , pos_y
        ret , frame = cap.read()
        if ret == True:
            color_index = 0
            if camera.get() == 0:
                frame = cv2.flip(frame, 1)
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

                if collection == True:
                    pos_x.append(((x+w/2)-ox))
                    pos_y.append((oy-(y+h/2)))
                    cv2.circle(black_background , (x+w/2,y+h/2) , 2 , (255,255,255) , -1)

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = PIL.Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
            if pause %2 == 0:
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
        box = cv2.selectROI("Selector", frame, fromCenter=False,
                            showCrosshair=True)
        tracker_trackingwindow = Tracker_used
        trackers.add(tracker_trackingwindow, frame, box)
        cv2.destroyWindow('Selector')

    def drawing():
        global fx,fy,fw,fh,x,y,w,h,ox,oy
        global start_time
        global collection , draw
        print("Drawing the reference coordinates")
        draw = True
        fx = x
        fy = y
        fw = w
        fh = h
        (ox , oy)  = (x+w/2 , y+h/2)
        collection = True
        start_time = time.time()

    def exitt():
        global end_time , total_time
        end_time = time.time()
        total_time = end_time-start_time
        print(pos_x)
        print(pos_y)
        cap.release()
        tracker_window.destroy()

    button1_tracking = Button(tracker_window , text="Pause" , bg="orange" , fg="black" ,
                      command = pausing , state=NORMAL)
    button1_tracking.place(x = 10 , y = 650)
    button2_tracking = Button(tracker_window , text="Select" , bg="orange" , fg="black" ,
                      command = select , state=NORMAL)
    button2_tracking.place(x = 60 , y = 650)
    button3_tracking = Button(tracker_window , text="Draw And Collect Data" , bg="orange" , fg="black" ,
                      command = drawing , state=NORMAL , width = 10)
    button3_tracking.place(x = 120 , y = 650)
    # Always use exit for exiting the program
    button4_tracking = Button(tracker_window , text="Exit" , bg="orange" , fg="black" ,
                      command = exitt , state=NORMAL)
    button4_tracking.place(x = 250 , y = 650)

    tracker_window.mainloop()

# Logic for enabling and disabling boxes
def switch():
    if camera.get() == 1:
        spinbox1_main.configure(state=DISABLED)
        if enable_tracking == True:
            button1_main.configure(state=NORMAL)
        else:
            button1_main.configure(state=DISABLED)
    else:
        spinbox1_main.configure(state=NORMAL)
        button1_main.configure(state=NORMAL)

def Plotter():
    pass

label1_main = Label(main_window , text = 'Please Read The Use Instructions in Help Menu' , 
                    fg='red',bg='yellow',font=("arial" , 16 , "bold"),relief='solid')
label1_main.pack()
button1_main = Button(main_window , text="Start Tracking" , bg="orange" , fg="black" ,
                      command = StartTracking , state=NORMAL)
button1_main.place(x = 250 , y = 40)  
button2_main = Button(main_window , text="Open Plotter" , bg="orange" , fg="black" ,
                      command = Plotter , state=NORMAL)
button2_main.place(x = 250 , y = 120)  
radiobutton1_main = Radiobutton(main_window , text = 'Use Webcam', variable=camera,
                                value=0 , command = switch)
radiobutton1_main.place(x=250,y=70)
radiobutton2_main = Radiobutton(main_window , text = 'Use video',variable=camera,
                                value=1 , command = switch)
radiobutton2_main.place(x=250,y=90)
spinbox1_main = Spinbox(main_window,from_=0,to=5,width=2)
spinbox1_main.place(x=400,y=70)





menu = Menu(main_window)
main_window.config(menu=menu)

file_menu = Menu(menu)
# Adding the menu option
menu.add_cascade(label='File',menu=file_menu)
# adding the submenus
file_menu.add_command(label="Open", command=OpenFile)
file_menu.add_command(label="Save", command=SaveFile)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=main_window.quit)

trackers_menu = Menu(menu)
menu.add_cascade(label="Trackers", menu=trackers_menu)
trackers_menu.add_radiobutton(label="CSRT" ,command=TrackerChooser,
                                variable=tracker,value="csrt")
trackers_menu.add_radiobutton(label="KCF", command=TrackerChooser,
                                variable=tracker,value="kcf")
trackers_menu.add_radiobutton(label="BOOSTING", command=TrackerChooser,
                                variable=tracker,value="boosting")
trackers_menu.add_radiobutton(label="MIL", command=TrackerChooser,
                                variable=tracker,value="mil")
trackers_menu.add_radiobutton(label="TLD", command=TrackerChooser,
                                variable=tracker,value="tld")
trackers_menu.add_radiobutton(label="MEDIANFLOW", command=TrackerChooser,
                                variable=tracker,value="medianflow")
trackers_menu.add_radiobutton(label="MOSSE", command=TrackerChooser,
                                variable=tracker,value="mosse")

trackers_menu.add_separator()
trackers_menu.add_radiobutton(label="HSV Tracking", command=TrackerChooser,
                                variable=tracker,value="Male")

help_menu = Menu(menu)
menu.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Use Instrcutions", command=Use)
help_menu.add_command(label="Tracker Info ", command=Info)
help_menu.add_command(label="About", command=About)

#########################################################################################################


main_window.mainloop()