import json
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mss
import subprocess

import threading


with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

class ConfigEditor(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.title("JSON Config Editor")
        self.config = config
        self.process = None

        self.create_widgets()
        self.update_screenshot()
        self.update_screenshot_periodically()

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 16))
        self.style.configure("TButton", font=("Arial", 16))
        self.style.configure("TCheckbutton", font=("Arial", 16))
        self.style.configure("TEntry", font=("Arial", 16))
        self.style.configure("TNotebook", font=("Arial", 16))
        self.style.configure("TNotebook.Tab", font=("Arial", 16))
        self.style.configure("TLabelFrame.Label", font=("Arial", 16))

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(side='top', fill='both', expand=True)

        self.interact_frame = ttk.Frame(notebook)
        self.detect_frame = ttk.Frame(notebook)
        self.window_frame = ttk.Frame(notebook)
        self.render_frame = ttk.Frame(notebook)

        notebook.add(self.interact_frame, text='Interact')
        notebook.add(self.detect_frame, text='Detect')
        notebook.add(self.window_frame, text='Window')
        notebook.add(self.render_frame, text='Render')

        self.create_interact_widgets()
        self.create_detect_widgets()
        self.create_window_widgets()
        self.create_render_widgets()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', fill='x', pady=10)

        save_button = ttk.Button(button_frame, text="Save", command=self.save_config)
        save_button.pack(side='left', padx=10)

        run_button = ttk.Button(button_frame, text="Run", command=self.run_script)
        run_button.pack(side='left', padx=10)

        stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_script)
        stop_button.pack(side='left', padx=10)



    def create_interact_widgets(self):
        self.interact_var = tk.BooleanVar(value=self.config["interact"])
        ttk.Checkbutton(self.interact_frame, text="Interact", variable=self.interact_var).pack(pady=10)

    def create_detect_widgets(self):
        detect = self.config["detect"]

        ttk.Label(self.detect_frame, text="HSV Ranges:").pack()
        for key in detect["hsv"]:
            frame = ttk.LabelFrame(self.detect_frame, text=key.capitalize())
            frame.pack(fill='x', padx=10, pady=5)

            lower_var = [tk.IntVar(value=v) for v in detect["hsv"][key]["lower"]]
            upper_var = [tk.IntVar(value=v) for v in detect["hsv"][key]["upper"]]

            ttk.Label(frame, text="Lower:").grid(row=0, column=0, padx=5, pady=2)
            for i, var in enumerate(lower_var):
                ttk.Entry(frame, textvariable=var, width=5).grid(row=0, column=i+1, padx=5, pady=2)

            ttk.Label(frame, text="Upper:").grid(row=1, column=0, padx=5, pady=2)
            for i, var in enumerate(upper_var):
                ttk.Entry(frame, textvariable=var, width=5).grid(row=1, column=i+1, padx=5, pady=2)

            setattr(self, f"{key}_lower_var", lower_var)
            setattr(self, f"{key}_upper_var", upper_var)

        self.safe_distance_var = tk.IntVar(value=detect["safe_distance"])
        self.minimal_area_var = tk.IntVar(value=detect["minimal_area"])
        self.frame_frequency_var = tk.IntVar(value=detect["frame_frequency"])
        self.click_frequency_var = tk.IntVar(value=detect["click_frequency"])

        ttk.Label(self.detect_frame, text="Safe Distance:").pack()
        ttk.Entry(self.detect_frame, textvariable=self.safe_distance_var).pack(pady=2)

        ttk.Label(self.detect_frame, text="Minimal Area:").pack()
        ttk.Entry(self.detect_frame, textvariable=self.minimal_area_var).pack(pady=2)

        ttk.Label(self.detect_frame, text="Frame Frequency:").pack()
        ttk.Entry(self.detect_frame, textvariable=self.frame_frequency_var).pack(pady=2)

        ttk.Label(self.detect_frame, text="Click Frequency:").pack()
        ttk.Entry(self.detect_frame, textvariable=self.click_frequency_var).pack(pady=2)

    def create_window_widgets(self):
        window = self.config["window"]

        self.left_var = tk.IntVar(value=window["left"])
        self.top_var = tk.IntVar(value=window["top"])
        self.width_var = tk.IntVar(value=window["width"])
        self.height_var = tk.IntVar(value=window["height"])

        ttk.Label(self.window_frame, text="Left:").pack()
        ttk.Entry(self.window_frame, textvariable=self.left_var).pack(pady=2)

        ttk.Label(self.window_frame, text="Top:").pack()
        ttk.Entry(self.window_frame, textvariable=self.top_var).pack(pady=2)

        ttk.Label(self.window_frame, text="Width:").pack()
        ttk.Entry(self.window_frame, textvariable=self.width_var).pack(pady=2)

        ttk.Label(self.window_frame, text="Height:").pack()
        ttk.Entry(self.window_frame, textvariable=self.height_var).pack(pady=2)

        self.screenshot_label = ttk.Label(self.window_frame, text="Screenshot will appear here")
        self.screenshot_label.pack(fill='both', expand=True)

    def create_render_widgets(self):
        render = self.config["render"]

        ttk.Label(self.render_frame, text="Render Colors and Radius:").pack()

        for key in ["blum", "bomb", "ice"]:
            frame = ttk.LabelFrame(self.render_frame, text=key.capitalize())
            frame.pack(fill='x', padx=10, pady=5)

            color_var = [tk.IntVar(value=v) for v in render[key]["color"]]
            radius_var = tk.IntVar(value=render[key]["radius"])

            ttk.Label(frame, text="Color:").grid(row=0, column=0, padx=5, pady=2)
            for i, var in enumerate(color_var):
                ttk.Entry(frame, textvariable=var, width=5).grid(row=0, column=i+1, padx=5, pady=2)

            ttk.Label(frame, text="Radius:").grid(row=1, column=0, padx=5, pady=2)
            ttk.Entry(frame, textvariable=radius_var, width=5).grid(row=1, column=1, padx=5, pady=2)

            setattr(self, f"{key}_color_var", color_var)
            setattr(self, f"{key}_radius_var", radius_var)

        self.layers_listbox = tk.Listbox(self.render_frame, selectmode=tk.MULTIPLE, height=5)
        for layer in ["screenshot", "centers", "mask:blum", "mask:bomb", "mask:ice"]:
            self.layers_listbox.insert(tk.END, layer)
        self.layers_listbox.pack(pady=10)

        # Set initial selection based on the config
        for i, layer in enumerate(["screenshot", "centers", "mask:blum", "mask:bomb", "mask:ice"]):
            if layer in render["layers"]:
                self.layers_listbox.select_set(i)

    def update_screenshot(self):
        window = self.config["window"]
        with mss.mss() as sct:
            monitor = {
                "top": self.top_var.get(),
                "left": self.left_var.get(),
                "width": self.width_var.get(),
                "height": self.height_var.get()
            }
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img.thumbnail((img.width, 600))  # Resize to fit the height of the window (max 600px)
            self.photo = ImageTk.PhotoImage(img)
            self.screenshot_label.config(image=self.photo)
            self.screenshot_label.image = self.photo

        # Adjust the window size based on the screenshot
        # self.geometry(f"{img.width}x{img.height + 100}")  # Adding 100px for buttons

    def update_screenshot_periodically(self):
        self.update_screenshot()
        self.after(1000, self.update_screenshot_periodically)

    def save_config(self):
        self.config["interact"] = self.interact_var.get()

        detect = self.config["detect"]
        for key in detect["hsv"]:
            lower_var = getattr(self, f"{key}_lower_var")
            upper_var = getattr(self, f"{key}_upper_var")
            detect["hsv"][key]["lower"] = [var.get() for var in lower_var]
            detect["hsv"][key]["upper"] = [var.get() for var in upper_var]

        detect["safe_distance"] = self.safe_distance_var.get()
        detect["minimal_area"] = self.minimal_area_var.get()
        detect["frame_frequency"] = self.frame_frequency_var.get()
        detect["click_frequency"] = self.click_frequency_var.get()

        window = self.config["window"]
        window["left"] = self.left_var.get()
        window["top"] = self.top_var.get()
        window["width"] = self.width_var.get()
        window["height"] = self.height_var.get()

        render = self.config["render"]
        for key in ["blum", "bomb", "ice"]:
            color_var = getattr(self, f"{key}_color_var")
            radius_var = getattr(self, f"{key}_radius_var")
            render[key]["color"] = [var.get() for var in color_var]
            render[key]["radius"] = radius_var.get()

        render["layers"] = [self.layers_listbox.get(i) for i in self.layers_listbox.curselection()]

        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)


    def run_script(self):
        if self.process is None:
            self.process = subprocess.Popen(["python", "main.py"])

    def stop_script(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None


if __name__ == "__main__":
    app = ConfigEditor(config)
    app.mainloop()
