import os.path
import datetime
import pickle
from threading import Thread
import tkinter as tk
import customtkinter as ctk
from tkinter import Label, Canvas
import cv2
from PIL import Image, ImageTk, ImageDraw
import face_recognition

import util
from test import test


class App:
    def __init__(self):
        self.main_window = ctk.CTk()
        self.main_window.title("Anti-Spoofing Detection App")
        image_path = 'C:/Users/Home/Desktop/Raoha_Thesis/Project/THESIS PROJECT/Anti_Spoofing_System/Images/Background.png'
        self.original_image = Image.open(image_path)
        self.window_width = 1920
        self.window_height = 1080
        self.update_image(self.original_image) 

        self.main_window.geometry("1120x620")

        self.login_button_main_window = util.get_button(
            self.main_window, "Log In", "#18694C", self.start_login_thread
        )
        self.login_button_main_window.place(x=210, y=670)

        self.logout_button_main_window = util.get_button(
            self.main_window, "Log Out", "#FF5757", self.start_logout_thread
        )
        self.logout_button_main_window.place(x=210, y=770)

        self.register_new_user_button_main_window = util.get_button(
            self.main_window,
            "Register New User",
            "#FFBD59",
            self.register_new_user,
        )
        self.register_new_user_button_main_window.place(x=210, y=870)

        self.canvas = Canvas(self.main_window, width=600, height=500)
        self.canvas.place(x=100, y=140)  

        self.rounded_rect(self.canvas, 0, 0, 600, 500, 100, "#3F3E58")  
        self.webcam_label = util.get_img_label(self.canvas)
        self.webcam_label.place(x=10, y=10, width=580, height=480)  
        self.add_webcam(self.webcam_label)

        self.db_dir = "./db"
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = "./log.txt"

        self.main_window.bind("<Configure>", self.resize_image)

    def update_image(self, image):
        self.resized_image = image.resize((self.window_width, self.window_height), Image.ANTIALIAS)
        self.bck_end = ImageTk.PhotoImage(self.resized_image)
        if hasattr(self, 'lbl'):
            self.lbl.config(image=self.bck_end)
            self.lbl.image = self.bck_end
        else:
            self.lbl = Label(self.main_window, image=self.bck_end)
            self.lbl.image = self.bck_end
            self.lbl.place(x=0, y=0, relwidth=1, relheight=1)

    def resize_image(self, event):
        self.window_width = event.width
        self.window_height = event.height
        self.update_image(self.original_image)

    def add_webcam(self, label):
        if "cap" not in self.__dict__:
            self.cap = cv2.VideoCapture(1)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def start_login_thread(self):
        login_thread = Thread(target=self.login)
        login_thread.start()

    def start_logout_thread(self):
        logout_thread = Thread(target=self.logout)
        logout_thread.start()

    def login(self):
        label = test(
            image=self.most_recent_capture_arr,
            model_dir=r"resources\anti_spoof_models",
            device_id=0,
        )

        if label == 1:
            name = util.recognize(self.most_recent_capture_arr, self.db_dir)

            if name in ["unknown_person", "no_persons_found"]:
                util.msg_box(
                    "Ups!!", "Unknown user. Please register new user or try again."
                )
            else:
                util.msg_box("Welcome back!", "Welcome, {}.".format(name))
                with open(self.log_path, "a") as f:
                    f.write("{},{},in\n".format(name, datetime.datetime.now()))
        else:
            util.msg_box("Hey, spoofer!", "You are fake!")

    def logout(self):
        label = test(
            image=self.most_recent_capture_arr,
            model_dir=r"resources\anti_spoof_models",
            device_id=0,
        )

        if label == 1:
            name = util.recognize(self.most_recent_capture_arr, self.db_dir)

            if name in ["unknown_person", "no_persons_found"]:
                util.msg_box(
                    "Ups!!", "Unknown user. Please register new user or try again."
                )
            else:
                util.msg_box("Hasta la vista!", "Goodbye, {}.".format(name))
                with open(self.log_path, "a") as f:
                    f.write("{},{},out\n".format(name, datetime.datetime.now()))
        else:
            util.msg_box("Hey, spoofer!", "You are fake!")

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        self.accept_button_register_new_user_window = util.get_button(
            self.register_new_user_window,
            "Accept",
            "#18694C",
            self.accept_register_new_user,
        )
        self.accept_button_register_new_user_window.place(x=765, y=280)

        self.try_again_button_register_new_user_window = util.get_button(
            self.register_new_user_window,
            "Try Again",
            "#FF5757",
            self.try_again_register_new_user,
        )
        self.try_again_button_register_new_user_window.place(x=765, y=380)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = util.get_entry_text(
            self.register_new_user_window
        )
        self.entry_text_register_new_user.place(x=750, y=150)

        self.text_label_register_new_user = util.get_text_label(
            self.register_new_user_window, "Please, Input The Username:"
        )
        self.text_label_register_new_user.place(x=750, y=70)

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c")

        embeddings = face_recognition.face_encodings(self.register_new_user_capture)[0]

        file = open(os.path.join(self.db_dir, "{}.pickle".format(name)), "wb")
        pickle.dump(embeddings, file)

        util.msg_box("Success!", "User has registered successfully !")

        self.register_new_user_window.destroy()

    def rounded_rect(self, canvas, x1, y1, x2, y2, radius=25, color='black'):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]

        return canvas.create_polygon(points, fill=color, outline=color)


if __name__ == "__main__":
    app = App()
    app.start()