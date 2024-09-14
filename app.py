import os
import requests
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import torch
import yaml
import clip
import joblib
from sea import get_favorite_list, list_all
from move import move_video

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 图像加载函数
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

# 特征提取函数
def extract_features(img):
    img_tensor = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        img_features = clip_model.encode_image(img_tensor)
    return img_features.cpu().numpy()

# 图片处理并分类
def process_image(index, title, id_type, cover, callback):
    def task():
        def on_image_loaded(img):
            if img:
                features = extract_features(img)
                pred = svm_model.predict(features)[0]
                callback(index, title, id_type, img, pred)

        load_image_from_url(cover, on_image_loaded)
    threading.Thread(target=task).start()

# GUI更新函数
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
            if loaded_images == image_count:
                btn_move.pack(pady=10)  # 所有图像加载后显示Move按钮

        def on_image_saved(index, title, id_type, img, pred):
            img.thumbnail((200, 200))
            img_tk = ImageTk.PhotoImage(img)

            lbl_img = tk.Label(frame, image=img_tk, bd=0)  # 默认边框宽度为0
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

            # 根据预测结果默认选择
            if pred == 1:
                selected_items[index] = True
                lbl_img.config(bd=4, relief="flat", background="red")

            check_all_images_loaded()

        threads = []
        for index, ele in enumerate(data["data"]["medias"]):
            title = ele["title"]
            cover = ele["cover"]
            id_type = str(ele["id"]) + ":" + str(ele["type"])

            if title == "已失效视频":
                continue

            thread = threading.Thread(target=process_image, args=(index, title, id_type, cover, on_image_saved))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    load_images()

# 移动视频并加载下一页
def move_selection():
    for i, ele in enumerate(current_page_data["data"]["medias"]):
        id_type = str(ele["id"]) + ":" + str(ele["type"])
        if selected_items.get(i, False):
            # move_video(media_id, tar_media_id, id_type)
            threading.Thread(target=move_video, args=(media_id, tar_media_id, id_type, cookie)).start()
    load_next_page()

# 加载下一页
def load_next_page():
    global pn, current_page_data
    pn += 1
    current_page_data = get_favorite_list(media_id, pn, cookie=cookie)
    if current_page_data["data"]["medias"]:
        update_gui(current_page_data)
    else:
        messagebox.showinfo("结束", "所有页面已完成。")
        root.quit()

# 选择所有图像
def select_all_images():
    for index in selected_items.keys():
        selected_items[index] = True
        row, col = divmod(index, num_columns)
        try:
            lbl_img = frame.grid_slaves(row=row*2, column=col)[0]  # Access the label by its grid position
            lbl_img.config(bd=4, relief="flat", background="red")
        except IndexError:
            pass

# 取消选择所有图像
def unselect_all_images():
    for index in selected_items.keys():
        selected_items[index] = False
        row, col = divmod(index, num_columns)
        try:
            lbl_img = frame.grid_slaves(row=row*2, column=col)[0]  # Access the label by its grid position
            lbl_img.config(bd=0, relief="flat", highlightbackground="white", highlightcolor="white")
        except IndexError:
            pass

# 跳过当前页面
def skip_current_page():
    load_next_page()

# 主函数
if __name__ == "__main__":
    with open("config.yml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        cookie = config["cookie"]
        kernel = config["kernel"]

    print("Loading CLIP model and SVM model...")
    clip_model, transform = clip.load('ViT-B/16', device=device)
    model_path = f"./models/{kernel}.pkl"
    svm_model = joblib.load(model_path)

    try:
        lists = list_all(cookie)
    except Exception as e:
        os.environ["http_proxy"] = "http://127.0.0.1:7890"
        os.environ["https_proxy"] = "http://127.0.0.1:7890"
        lists = list_all(cookie)
        
    dic = {ele["id"]: ele["title"] for ele in lists}

    root = tk.Tk()
    root.title("RSQ视频分类器")
    root.geometry("1280x850")

    # 创建下拉框以选择源和目标收藏夹
    source_var = tk.StringVar()
    target_var = tk.StringVar()
    
    lbl_source = tk.Label(root, text="Source Collection:", font=("Arial", 12))
    lbl_source.pack(pady=5)

    source_combo = ttk.Combobox(root, textvariable=source_var,state='readonly')
    source_combo['values'] = list(dic.values())
    source_combo.pack(pady=5)

    lbl_target = tk.Label(root, text="Target Collection:", font=("Arial", 12))
    lbl_target.pack(pady=5)

    target_combo = ttk.Combobox(root, textvariable=target_var,state='readonly')
    target_combo['values'] = list(dic.values())
    target_combo.pack(pady=5)

    # 确认按钮
    def apply_selection():
        global media_id, tar_media_id, pn
        source_title = source_var.get()
        target_title = target_var.get()
        media_id = list(dic.keys())[list(dic.values()).index(source_title)]
        tar_media_id = list(dic.keys())[list(dic.values()).index(target_title)]
        pn = 0
        lbl_source.pack_forget()
        source_combo.pack_forget()
        lbl_target.pack_forget()
        target_combo.pack_forget()
        btn_apply.pack_forget()
        btn_select_all.pack(pady=10)
        btn_unselect_all.pack(pady=10)
        btn_skip.pack(pady=10)
        load_next_page()

    btn_apply = tk.Button(root, text="Apply", command=apply_selection)
    btn_apply.pack(pady=10)

    canvas = tk.Canvas(root)
    frame = tk.Frame(canvas)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    btn_move = tk.Button(root, text="Move", command=move_selection)
    btn_move.pack(pady=10)
    btn_move.pack_forget()

    btn_select_all = tk.Button(root, text="Select All", command=select_all_images)
    btn_unselect_all = tk.Button(root, text="Unselect All", command=unselect_all_images)
    btn_skip = tk.Button(root, text="Skip Page", command=skip_current_page)

    root.mainloop()
