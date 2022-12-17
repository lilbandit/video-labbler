from tkinter import *
import tkinter
from PIL import Image, ImageTk
from os import listdir
import pandas as pd
import os.path
import time

import skvideo.io
import skvideo.datasets

import argparse

parser = argparse.ArgumentParser(description='App for labeling video for object tracking.')

parser.add_argument("input", help="File name of video.")

parser.add_argument("output", help="Folder name to store labels.")

args = parser.parse_args()


video_file_name = args.input

video_name = video_file_name.split('/')[-1].split('.')[0]
save_to = '{0}/{1}.csv'.format(args.output, video_name)  

print('getting video: {}'.format(video_name))
print('output folder: {}'.format(save_to))

# exit()

video_data = skvideo.io.vread(video_file_name)

print('video data ', video_data.shape)
image_height, image_width = video_data.shape[1:3]
x,y = 0,0
image_index = 0
stop = True
speed = 500
xs = []
ys = []

class Application(Frame):

    def createWidgets(self):
        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()



def motion(event):
    global x, y
    x, y = event.x, event.y

def save_x_y(x, y):
    x_ratio = min(1., x / float(image_width))
    y_ratio = min(1., y / float(image_height))
    xs.append(x_ratio)
    ys.append(y_ratio)
    print(x_ratio, y_ratio)

def save_to_file():
    df = pd.DataFrame(list(zip(xs, ys)), columns=['x','y'])
    df.to_csv(save_to)
    print('labels saved to {}'.format(save_to))



def next_image():
    global image_index, x, y, stop, speed

    display_image(image_index)
    image_index+=1
    w.delete("all")
    w.create_image(0, 0, anchor=tkinter.NW, image=current_photo)
    w.create_line(x, 0, x, image_height, fill="red")
    w.create_line(0, y, image_width, y,fill="red")
    save_x_y(x, y)

    if image_index >= len(video_data):
        print("finished data")
        save_to_file()
        print("saved data")
    elif not stop:
        w.after(speed, next_image)


def play(event):
    global stop 
    if stop:
        stop = False
        next_image()


def pause(event):
    global stop 
    stop = True
    save_to_file()


def display_image(image_index):
    global current_photo
    current_photo = ImageTk.PhotoImage(Image.fromarray(video_data[image_index].astype('uint8'), 'RGB'))
 
def key(event):
    global speed 

    if event.char == '\uf703':
        print('right')
        speed = max(speed-70, 10)


    elif event.char == '\uf702':
        print('left')
        speed += 70

    elif event.char == '\uf701':
        print('down')

    else:
        print("pressed", repr(event.char))


root = Tk()

current_photo = None

w = Canvas(root, width=1000, height=1000, highlightthickness=0)
w.pack()

w.bind('<Motion>', motion)
w.bind("<Button-1>", play)
w.bind("<Button-2>", pause)
root.bind("<Key>", key)


app = Application(master=root)
app.mainloop()
root.destroy()

