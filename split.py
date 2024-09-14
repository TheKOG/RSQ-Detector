import json
import requests
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
import threading

def load_image_from_url(url, callback):
    def task():
        try:
            response = requests.get(url)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                callback(img)
            else:
                print(f"无法加载图像，状态码: {response.status_code}")
                callback(None)
        except Exception as e:
            print(f"加载图像时出现错误: {e}")
            callback(None)
    threading.Thread(target=task).start()

def save_image(img, path):
    if img:
        img.save(path)

def process_image(index, title, bvid, cover, callback):
    def task():
        def on_image_loaded(img):
            if img:
                img.thumbnail((200, 200))
                file_type = cover.split(".")[-1]
                temp_path = f"./temp/{bvid}."+file_type
                save_image(img, temp_path)
                callback(index, title, temp_path)
        
        load_image_from_url(cover, on_image_loaded)
    threading.Thread(target=task).start()

def submit_selection():
    if not os.path.exists("./positive/"):
        os.makedirs("./positive/")
    if not os.path.exists("./negative/"):
        os.makedirs("./negative/")

    selected_indices = [i for i, selected in selected_items.items() if selected]

    for i, ele in enumerate(current_page_data["data"]["medias"]):
        bvid = ele["bvid"]
        temp_path = f"./temp/{bvid}.jpg"
        if os.path.exists(temp_path):
            if i in selected_indices:
                shutil.move(temp_path, f"./positive/{bvid}.jpg")
            else:
                shutil.move(temp_path, f"./negative/{bvid}.jpg")

    load_next_page()

def select_all_images():
    for index in selected_items.keys():
        selected_items[index] = True
        row, col = divmod(index, num_columns)
        try:
            lbl_img = frame.grid_slaves(row=row*2, column=col)[0]  # Access the label by its grid position
            lbl_img.config(bd=4, relief="flat", background="red")
        except IndexError:
            pass

def unselect_all_images():
    for index in selected_items.keys():
        selected_items[index] = False
        row, col = divmod(index, num_columns)
        try:
            lbl_img = frame.grid_slaves(row=row*2, column=col)[0]  # Access the label by its grid position
            lbl_img.config(bd=0, relief="flat", highlightbackground="white", highlightcolor="white")
        except IndexError:
            pass

def skip_current_page():
    load_next_page()

def clear_temp_folder():
    if not os.path.exists("./temp/"):
        os.makedirs("./temp/")
        return
    temp_folder = "./temp/"
    for filename in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

def load_next_page():
    global pn, current_page_data
    clear_temp_folder()  # Clear temp folder before loading new page
    pn += 1
    try:
        with open(f"./jsons/page_{pn}.json", "r", encoding="utf-8") as f:
            current_page_data = json.load(f)
            update_gui(current_page_data)
    except FileNotFoundError:
        messagebox.showinfo("结束", "所有页面已完成。")
        root.quit()

def update_gui(data):
    for widget in frame.winfo_children():
        widget.destroy()

    global selected_items
    selected_items = {i: False for i in range(len(data["data"]["medias"]))}
    image_count = len([ele for ele in data["data"]["medias"] if ele["title"] != "已失效视频"])
    loaded_images = 0

    global num_columns
    num_columns = 5

    def load_images():
        nonlocal loaded_images

        def check_all_images_loaded():
            nonlocal loaded_images
            loaded_images += 1
            # print(f"Loaded images: {loaded_images}/{image_count}")
            if loaded_images == image_count:
                btn_submit.pack(pady=10)  # Show submit button after all images are loaded

        def on_image_saved(index, title, temp_path):
            img = Image.open(temp_path)
            img_tk = ImageTk.PhotoImage(img)

            lbl_img = tk.Label(frame, image=img_tk, bd=0)  # Initial border width is 0
            lbl_img.image = img_tk
            row, col = divmod(index, num_columns)
            lbl_img.grid(row=row * 2, column=col, padx=8, pady=0)

            lbl_title = tk.Label(frame, text=title, wraplength=180)
            lbl_title.grid(row=row * 2 + 1, column=col, padx=8, pady=0)

            def on_click(event):
                if selected_items[index] == False:
                    selected_items[index] = True
                    lbl_img.config(bd=4, relief="flat", background="red")
                else:
                    selected_items[index] = False
                    lbl_img.config(bd=0, relief="flat", highlightbackground="white", highlightcolor="white")

            lbl_img.bind("<Button-1>", on_click)

            check_all_images_loaded()  # Check if all images are loaded

        threads = []
        for index, ele in enumerate(data["data"]["medias"]):
            title = ele["title"]
            cover = ele["cover"]
            bvid = ele["bvid"]

            if title == "已失效视频":
                continue

            thread = threading.Thread(target=process_image, args=(index, title, bvid, cover, on_image_saved))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    load_images()

if __name__ == "__main__":
    pn = 0
    current_page_data = {}

    root = tk.Tk()
    root.title("RSQ视频封面选择器")
    root.geometry("1250x850")

    canvas = tk.Canvas(root)
    frame = tk.Frame(canvas)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    btn_submit = tk.Button(root, text="Submit", command=submit_selection)
    btn_submit.pack(pady=10)
    btn_submit.pack_forget()

    btn_select_all = tk.Button(root, text="Select All", command=select_all_images)
    btn_select_all.pack(pady=10)

    btn_unselect_all = tk.Button(root, text="Unselect All", command=unselect_all_images)
    btn_unselect_all.pack(pady=10)

    btn_skip = tk.Button(root, text="Skip Page", command=skip_current_page)
    btn_skip.pack(pady=10)

    if not os.path.exists("./temp/"):
        os.makedirs("./temp/")

    load_next_page()

    root.mainloop()
