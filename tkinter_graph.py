import tkinter as tk
import random
import math

class SineGraph(tk.Canvas):
    def __init__(self, master=None, seconds=10, width=400, height=300, *args, **kwargs):
        super().__init__(master, width=width, height=height, *args, **kwargs)
        self.seconds = seconds
        self.width = width
        self.height = height
        self.amplitude = height / 2
        self.period = 50
        self.phase_shift = 0
        self.x_increment = 1
        self.max_x = width
        self.line_color = 'blue'
        self.background_color = 'white'
        self.x = 0
        self.start()

    def start(self):
        self.delete("all")
        self.create_rectangle(0, 0, self.width, self.height, fill=self.background_color, outline=self.background_color)
        self.create_line(0, self.height / 2, self.width, self.height / 2, fill=self.line_color)
        self.x = 0
        self.draw_wave()
        if self.seconds > 0:
            self.after(1000, self.start)
            self.seconds -= 1

    def draw_wave(self):
        y = self.amplitude * math.sin((2 * math.pi / self.period) * self.x + self.phase_shift) + self.height / 2
        self.create_line(self.x, y, self.x + self.x_increment, self.amplitude * math.sin((2 * math.pi / self.period) * (self.x + self.x_increment) + self.phase_shift) + self.height / 2, fill=self.line_color)
        self.x += self.x_increment
        if self.x < self.max_x:
            self.after(10, self.draw_wave)

root = tk.Tk()
graph = SineGraph(root, seconds=10)
graph.pack()
root.mainloop()
