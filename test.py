import cv2
import os
from datetime import datetime
from PIL import ImageFont, ImageDraw, Image, ImageTk
import arabic_reshaper
from bidi.algorithm import get_display
import tkinter as tk
from tkinter import messagebox
import numpy as np

# Directory to save images
lab_directory = r"C:\Users\Nazeer\Desktop\projectBOb"
if not os.path.exists(lab_directory):
    os.makedirs(lab_directory)

# Path to the test image
test_image_path = r"C:\Users\Nazeer\Desktop\projectBOb\test2.png"
if not os.path.exists(test_image_path):
    messagebox.showerror("Error", f"Test image not found at {test_image_path}")
    exit()

# Read the test image
test_image = cv2.imread(test_image_path)
if test_image is None:
    messagebox.showerror("Error", "Failed to load the test image!")
    exit()

# Open the camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    messagebox.showerror("Error", "Camera not accessible!")
    exit()

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Font path for Arabic text
font_path = r"C:\Users\Nazeer\Desktop\projectBOb\Amiri.ttf"

# Function to overlay Arabic text on an image
def put_arabic_text(img, text, position, font_path=font_path, font_size=24):
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, bidi_text, font=font, fill=(0, 255, 0))
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

# Capture and save only the face region, then combine with test image
def capture_image():
    ret, frame = cap.read()
    if not ret:
        update_status("خطأ: لم يتم التقاط الصورة")
        return

    # Detect faces in the frame
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    if len(faces) == 0:
        update_status("لم يتم الكشف عن وجه!")
        return

    # Crop the first detected face
    for (x, y, w, h) in faces:
        # Add different margins for width and height
        margin_width = 20  # Adjust for width padding
        margin_height = 30  # Adjust for extra height padding

        x_start = max(x - margin_width, 0)
        y_start = max(y - margin_height, 0)
        x_end = min(x + w + margin_width, frame.shape[1])
        y_end = min(y + h + margin_height, frame.shape[0])

        # Crop the face with added margins
        face = frame[y_start:y_end, x_start:x_end]

        # Resize the face to fit into the test image
        face_resized = cv2.resize(face, (120, 160))  # Increased height relative to width
        test_image_copy = test_image.copy()

        # Add a margin to the left of the face image
        left_margin = 150  # Set your desired margin size
        overlay_x = left_margin
        overlay_y = 50  # Adjust position as needed

        # Overlay the resized face on the test image
        test_image_copy[overlay_y:overlay_y+160, overlay_x:overlay_x+120] = face_resized

        # Save the combined image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_image_filename = os.path.join(lab_directory, f"combined_with_face_{timestamp}.jpg")
        cv2.imwrite(combined_image_filename, test_image_copy)

        update_status("تم حفظ الصورة بنجاح")
        root.after(2000, lambda: update_status("جاهز"))
        return

# Quit the program
def quit_program():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

# Update status bar
def update_status(msg):
    status_label.config(text=msg)

# Update live camera feed
def update_feed():
    ret, frame = cap.read()
    if ret:
        frame_with_text = put_arabic_text(frame, "عرض مباشر للكاميرا", (10, 10))
        frame_rgb = cv2.cvtColor(frame_with_text, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
        live_feed_label.config(image=img)
        live_feed_label.image = img
    root.after(10, update_feed)

# GUI setup
root = tk.Tk()
root.title("أداة التقاط الصور")
root.geometry("800x600")

# Live feed label
live_feed_label = tk.Label(root, bg="black")
live_feed_label.pack(pady=20, expand=True)

# Buttons frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Capture button (Green)
capture_button = tk.Button(
    button_frame, 
    text="التقاط الصورة", 
    command=capture_image, 
    width=20, 
    height=2, 
    bg="green", 
    fg="white", 
    font=("Arial", 12)
)
capture_button.grid(row=0, column=0, padx=10)

# Quit button (Red)
quit_button = tk.Button(
    button_frame, 
    text="خروج", 
    command=quit_program, 
    width=20, 
    height=2, 
    bg="red", 
    fg="white", 
    font=("Arial", 12)
)
quit_button.grid(row=0, column=1, padx=10)

# Status bar
status_label = tk.Label(root, text="جاهز", bg="lightgray", anchor="w", font=("Arial", 14))
status_label.pack(side="bottom", fill="x")

# Start live feed
update_feed()
root.mainloop()
