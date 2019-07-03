import cv2
import tkinter
from tkinter import *
from PIL import Image , ImageTk
from tkinter.filedialog  import askopenfilename
from tkinter import filedialog
import numpy as np
import PIL
import time
import tkinter.messagebox
import matplotlib.pyplot as plt

#########################################################################################################
# Creating the main window with menu
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
#########################################################################################################

# setting values
camera.set(0)
spinbox1_main.set('0')
tracker.set('csrt')
var_c1.set(0)

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
    tracker_window.geometry("800x700") # width*height
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
        frame = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_LINEAR)
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
        button3_tracking.configure(state = NORMAL)

    def drawing():
        global fx,fy,fw,fh,x,y,w,h,ox,oy
        global start_time
        global collection , draw
        global pos_x , pos_y
        print("Drawing the reference coordinates")
        draw = True
        fx = x
        fy = y
        fw = w
        fh = h
        (ox , oy)  = (x+w/2 , y+h/2)
        collection = True
        start_time = time.time()
        pos_x = []
        pos_y = []

    # Exit will also enable entry to save window
    def exitt():
        global end_time , total_time
        end_time = time.time()
        total_time = end_time-start_time
        print(pos_x)
        print(pos_y)
        cap.release()
        tracker_window.destroy()
        
        save_window = Toplevel()
        save_window.geometry("600x300") # width*height
        save_window.title("Tracking Window")
        save_window.resizable(width=FALSE, height=FALSE)

        def directory_select():
            global save_path 
            save_path = filedialog.askdirectory()
            if save_path == '':
                button2_saving.configure(state = DISABLED)
            else:
                button2_saving.configure(state = NORMAL)


        def saving_the_files():
            path_x = save_path + '//' + entry1_save_window.get()
            print(path_x)
            path_y = save_path + '//' + entry2_save_window.get()
            path_background = save_path + '//' + entry3_save_window.get()
            path_time = save_path + '//' + entry4_save_window.get()

            np.save(path_x , pos_x)
            np.save(path_y , pos_y)
            np.save(path_time , total_time)
            cv2.imwrite(path_background,black_background)
            tkinter.messagebox.showerror("Saving" , "Done Saving")
            

        label1_save_window = Label(save_window , text = 'If You Want to save the data then select the directory \n  Enter The Name of the files along with Extensions' , 
                                fg='red',bg='yellow',font=("arial" , 16 , "bold"),relief='solid')
        label1_save_window.pack()

        button1_saving = Button(save_window , text="Directory" , bg="orange" , fg="black" ,
                      command = directory_select , state=NORMAL , font=("arial" , 10 , "bold"),relief='solid' , 
                      width = 15)
        button1_saving.pack()

        label3_save_window = Label(save_window , text = 'X Values' , 
                                fg='red',bg='yellow',font=("arial" , 10 , "bold"),relief='solid')
        label3_save_window.place(x = 20 , y = 120)
        label4_save_window = Label(save_window , text = 'Y Values' , 
                                fg='red',bg='yellow',font=("arial" , 10 , "bold"),relief='solid')
        label4_save_window.place(x = 20 , y = 150)
        label5_save_window = Label(save_window , text = 'Background Image' , 
                                fg='red',bg='yellow',font=("arial" , 10 , "bold"),relief='solid')
        label5_save_window.place(x = 20 , y = 180)
        label6_save_window = Label(save_window , text = 'Time Taken' , 
                                fg='red',bg='yellow',font=("arial" , 10 , "bold"),relief='solid')
        label6_save_window.place(x = 20 , y = 210)

        entry1_save_window = Entry(save_window , width = 30)
        entry1_save_window.place(x = 180 , y = 120)
        entry1_save_window.insert(END, 'X.npy')
        entry2_save_window = Entry(save_window , width = 30)
        entry2_save_window.place(x = 180 , y = 150)
        entry2_save_window.insert(END, 'Y.npy')
        entry3_save_window = Entry(save_window , width = 30)
        entry3_save_window.place(x = 180 , y = 180)
        entry3_save_window.insert(END, 'Back.jpg')
        entry4_save_window = Entry(save_window , width = 30)
        entry4_save_window.place(x = 180 , y = 210)
        entry4_save_window.insert(END, 'T.npy')

        button2_saving = Button(save_window , text="Save" , bg="orange" , fg="black" ,
                      command = saving_the_files , state=DISABLED , font=("arial" , 10 , "bold"),relief='solid' , 
                      width = 15)
        button2_saving.place(x = 230 , y = 250)


    # disabling cross
    def disable_cross():
        tkinter.messagebox.showerror("EXIT" , "Please Exit Using Exit Button")

    button1_tracking = Button(tracker_window , text="Pause\ \n Continue" , bg="orange" , fg="black" ,
                      command = pausing , state=NORMAL , font=("arial" , 10 , "bold"),relief='solid' , 
                      width = 15)
    button1_tracking.place(x = 120 , y = 620)
    button2_tracking = Button(tracker_window , text="Select" , bg="orange" , fg="black" ,
                      command = select , state=NORMAL, font=("arial" , 10 , "bold"),relief='solid' , 
                      width = 15)
    button2_tracking.place(x = 270 , y = 620)
    button3_tracking = Button(tracker_window , text="Draw And \n Collect Data" , bg="orange" , fg="black" ,
                      command = drawing , state=DISABLED , font=("arial" , 10 , "bold"),relief='solid' , 
                      width = 15)
    button3_tracking.place(x = 420 , y = 620)
    # Always use exit for exiting the program
    button4_tracking = Button(tracker_window , text="Exit" , bg="orange" , fg="black" ,
                      command = exitt , state=NORMAL , font=("arial" , 10 , "bold"),relief='solid' , 
                      width = 15)
    button4_tracking.place(x = 570 , y = 620)

    # tracker_window.resizable(width=FALSE, height=FALSE)
    tracker_window.protocol("WM_DELETE_WINDOW", disable_cross)
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

def Value_Plotter():
    value_plotter_window = Toplevel()
    value_plotter_window.geometry("400x250") # width*height
    value_plotter_window.title("Plotting Window")
    value_plotter_window.resizable(width=FALSE, height=FALSE)

    def value_plotter_x_values():
        global load_path_x_plotter , enable_plot , loaded_X
        load_path_x_plotter = askopenfilename(initialdir = "/",title = "Select X values")
        if load_path_x_plotter != '':
            enable_plot += 1
        if enable_plot == 2:
            button4_value_plotter.configure(state = NORMAL)
        loaded_X = np.load(load_path_x_plotter)

    def value_plotter_y_values():
        global load_path_y_plotter , enable_plot , loaded_Y
        load_path_y_plotter = askopenfilename(initialdir = "/",title = "Select Y values")
        if load_path_y_plotter != '':
            enable_plot += 1
        if enable_plot == 2:
            button4_value_plotter.configure(state = NORMAL)
        loaded_Y = np.load(load_path_y_plotter)

    def value_plotter_time_values():
        global load_path_time_plotter , loaded_time
        load_path_time_plotter = askopenfilename(initialdir = "/",title = "Select time values")
        if load_path_time_plotter != '':
            checkbutton1_value_plotter.configure(state = NORMAL)
        loaded_time = np.load(load_path_time_plotter)

    def value_plot():
        X_values = loaded_X
        Y_values = loaded_Y
        timeforxaxis = loaded_time
        x_label = ''
        plot_title_x = ''
        plot_title_y = ''

        if var_c1.get() == '0':
            x_axis = np.arange(1,(len(X_values)+1),1)
            x_label = 'frames'
            plot_title_x = 'X coordinates vs Frames'
            plot_title_y = 'Y coordinates vs Frames'
        else:
            x_axis = np.linspace(1,(timeforxaxis+1),len(X_values))
            x_label = 'time(s)'
            plot_title_x = 'X coordinates vs Time'
            plot_title_y = 'Y coordinates vs Time'
        
        fig = plt.figure(figsize=(12,7))
        fig.subplots_adjust(hspace=0.5, wspace=0.2)
        
        plt.subplot(3, 2, 1)
        plt.plot(x_axis ,X_values)
        plt.xlabel(x_label)
        plt.ylabel('X coordinates')
        plt.title(plot_title_x)

        plt.subplot(3, 2, 3)
        plt.scatter( x_axis ,X_values)
        plt.xlabel(x_label)
        plt.ylabel('X coordinates')
        plt.title(plot_title_x +' scatter plot')

        plt.subplot(3, 2, 5)
        plt.hist(X_values, color = 'blue', edgecolor = 'black',bins = len(X_values))
        plt.xlabel('X coordinates')
        plt.ylabel('Count')
        plt.title('Histogram of X coordinates')

        plt.subplot(3, 2, 2)
        plt.plot(x_axis ,Y_values)
        plt.xlabel(x_label)
        plt.ylabel('Y coordinates')
        plt.title(plot_title_y)

        plt.subplot(3, 2, 4)
        plt.scatter( x_axis, Y_values)
        plt.xlabel(x_label)
        plt.ylabel('Y coordinates')
        plt.title(plot_title_y +' scatter plot')

        plt.subplot(3, 2, 6)
        plt.hist(Y_values, color = 'blue', edgecolor = 'black',bins = len(X_values))
        plt.xlabel('Y coordinates')
        plt.ylabel('Count')
        plt.title('Histogram of Y coordinates')

        plt.show()

    label1_value_plotter = Label(value_plotter_window , text = 'Select The X and Y values for Plotting' , 
                                fg='red',bg='yellow',font=("arial" , 16 , "bold"),relief='solid')
    label1_value_plotter.pack()
    button1_value_plotter = Button(value_plotter_window , text="Select X values" , bg="orange" , fg="black" ,
                                    command = value_plotter_x_values , state=NORMAL , width = 20 , 
                                    font=("arial" , 10 , "bold"))
    button1_value_plotter.place(x = 120 , y = 50)
    button2_value_plotter = Button(value_plotter_window , text="Select Y Values" , bg="orange" , fg="black" ,
                      command = value_plotter_y_values , state=NORMAL , width = 20 , 
                      font=("arial" , 10 , "bold"))
    button2_value_plotter.place(x = 120 , y = 100)
    button3_value_plotter = Button(value_plotter_window , text="Select Time Values" , bg="orange" , fg="black" ,
                      command = value_plotter_time_values , state=NORMAL , width = 20 , 
                      font=("arial" , 10 , "bold"))
    button3_value_plotter.place(x = 120 , y = 150)
    button4_value_plotter = Button(value_plotter_window , text="Plot" , bg="orange" , fg="black" ,
                      command = value_plot , state=DISABLED , width = 20 , 
                      font=("arial" , 10 , "bold"))
    button4_value_plotter.place(x = 120 , y = 200)

    checkbutton1_value_plotter = Checkbutton(value_plotter_window , text='Vs Time' , variable=var_c1 , 
                                             state = DISABLED)
    checkbutton1_value_plotter.place(x=300,y=150)

def Allan_Deviation_Plotter():
    pass

label1_main = Label(main_window , text = 'Please Read The Use Instructions in Help Menu' , 
                    fg='red',bg='yellow',font=("arial" , 16 , "bold"),relief='solid')
label1_main.pack()
button1_main = Button(main_window , text="Start Tracking" , bg="orange" , fg="black" ,
                      command = StartTracking , state=NORMAL , width = 20 , 
                      font=("arial" , 10 , "bold"))
button1_main.pack()  
radiobutton1_main = Radiobutton(main_window , text = 'Use Webcam', variable=camera,
                                value=0 , command = switch)
radiobutton1_main.pack()
radiobutton2_main = Radiobutton(main_window , text = 'Use video',variable=camera,
                                value=1 , command = switch)
radiobutton2_main.pack()
spinbox1_main = Spinbox(main_window,from_=0,to=5,width=2)
spinbox1_main.place(x = 300 , y = 60)
button2_main = Button(main_window , text="Value Plotter" , bg="orange" , fg="black" ,
                      command = Value_Plotter , state=NORMAL , width = 20 ,
                      font=("arial" , 10 , "bold"))
button2_main.place(x = 50 , y = 110) 

button3_main = Button(main_window , text="ADEV Plotter" , bg="orange" , fg="black" ,
                      command = Allan_Deviation_Plotter , state=NORMAL , width = 20 ,
                      font=("arial" , 10 , "bold"))
button3_main.place(x = 280 , y = 110) 


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

main_window.resizable(width=FALSE, height=FALSE)
main_window.mainloop()