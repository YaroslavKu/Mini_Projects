#########################################################################
#   Emotion | A program that guesses which emoticon is drawn using ML   #
#########################################################################

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import (Line, Color, Ellipse)
from kivy.core.window import Window

import numpy as np
from skimage.io import imread
from PIL import Image


matrix_of_img = np.zeros((20, 20))
synaptic_weight = np.load("synaptic_weight.npy")
input_vector = np.array([matrix_of_img.flatten('F')])
expected_output = np.array([1]).T
output = np.array([1])


class PainterWidget(Widget):
    def on_touch_down(self, touch):
        print(touch)
        with self.canvas:
            Color(1, 0, 0)
            Ellipse(pos=(touch.x - 20, touch.y - 20), size=(40, 40))
            touch.ud["line"] = Line(points=(touch.x, touch.y), width=20)

    def on_touch_move(self, touch):
        print(touch)
        touch.ud["line"].points += (touch.x, touch.y)


class DrawingApp(App):
    Window.clearcolor = (1, 1, 1, 1)

    def build(self):
        parent = Widget()
        parent.add_widget(self.painter)
        parent.add_widget(self.label)
        parent.add_widget(Button(text="=(", on_press=self.train_neg, size=(50, 50), pos=(250, 0)))
        parent.add_widget(Button(text="=)", on_press=self.train_pos, size=(50, 50), pos=(200, 0)))
        parent.add_widget(Button(text="Clear", on_press=self.clear_canvas, size=(70, 50), pos=(100, 0)))
        parent.add_widget(Button(text="OK", on_press=self.img_process, size=(100, 50)))
        return parent

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(text='', markup=True, font_size='20sp', pos=(Window.size[1], -20))
        self.painter = PainterWidget()

    def train_pos(self, instance):
        global expected_output
        expected_output = np.array([1]).T
        train()
        print("Weights after training: ")
        query()
        self.update_label()

    def train_neg(self, instance):
        global expected_output
        expected_output = np.array([0]).T
        train()
        print("Weights after training: ")
        query()
        self.update_label()

    def update_label(self):
        if output[0] > 0.5:
            emotion = "Positive"
        else:
            emotion = "Negative"
        self.label.text = "[color=000000]" + emotion + " (" + str(round(output[0][0], 4)) + ")[/color]"

    def clear_canvas(self, instance):
        self.painter.canvas.clear()
        reset_matrix_of_img()

    def img_process(self, instance):
        self.painter.size = (Window.size[0], Window.size[1])
        self.painter.export_to_png("emotion_img.png")

        img = Image.open('emotion_img.png')
        img = img.resize((20, 20), Image.ANTIALIAS)
        img.save('emotion_img.png')

        img_to_matrix()
        query()
        self.update_label()


# Image processing functions
def reset_matrix_of_img():
    global matrix_of_img
    matrix_of_img = np.zeros((20, 20))


def img_to_matrix():
    im = imread("emotion_img.png")
    global input_vector

    for i in range(20):
        for j in range(20):
            if im[i][j][0] > 5:
                matrix_of_img[i][j] = 1

    for r in matrix_of_img:
        for c in r:
            if c == 0:
                print(0, end="  ")
            else:
                print(" ", end="  ")
        print()

    input_vector = np.array([matrix_of_img.flatten('F')])


# Neural network
def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def train():
    global synaptic_weight
    err = expected_output - output
    adjustments = np.dot(input_vector.T, err * (output * (1 - output)))
    synaptic_weight += adjustments
    np.save("synaptic_weight.npy", synaptic_weight)


def query():
    global output
    output = sigmoid(np.dot(input_vector, synaptic_weight)).T
    print("Output: ", output)
    if output[0] > 0.5:
        print("Positive")
    else:
        print("Negative")


# MAIN
if __name__ == "__main__":
    DrawingApp().run()

