import requests, os
import tkinter as tk
from tkinter import filedialog, messagebox

# Cấu hình headers của request
headers = {
    "Referer": "https://www.pixiv.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}


def select_dir_path():
    dir_path = filedialog.askdirectory()
    entry_dir_path.insert(0, dir_path)

def download():
    # 1. Lấy ID/URL từ ô nhập liệu
    artwork_id_or_url:str = entry_id_or_url.get()

    # 2. Lấy thư mục lưu
    dir_path:str = entry_dir_path.get()

    # 3. Kiểm tra (nếu người dùng có chọn thư mục và có nhập ID)
    if artwork_id_or_url and dir_path:
        # Nếu là URL thì tách lấy cái phần id ở cuối, không thì nó là chính nó
        artwork_id = artwork_id_or_url.split("/").pop()

        print(f"ID: {artwork_id}")
        print(f"Lưu tại: {dir_path}")

        # Tải ảnh
        # Gọi API
        api_url = f"https://www.pixiv.net/ajax/illust/{artwork_id}/pages"
        response = requests.get(api_url, headers=headers)

        # Kiểm tra xem request có thành công không, có thì tải
        if response.status_code == 200:
            # Nếu request thành công thì tạo thư mục để lưu ảnh
            os.makedirs(dir_path, exist_ok=True)

            for img in response.json()["body"]:
                original_img_url = img["urls"]["original"]
                file_name = original_img_url.split("/").pop()
                full_path = os.path.join(dir_path, file_name) # Dùng os.path.join để nối đường dẫn chuẩn theo hệ điều hành
                
                # Tải ảnh
                img_content = requests.get(original_img_url, headers=headers).content
                
                with open(full_path, mode="wb") as file_img:
                    file_img.write(img_content)
                    print(f"Đã tải xong: {file_name}")
        else:
            print(f"Lỗi không gọi được API: {response.status_code}")
        
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập ID và chọn thư mục!")

# Tạo cửa sổ chính
window = tk.Tk()
window.title("Pixiv Downloader 🎨")
window.geometry("1280x720")

# Tạo Label hướng dẫn nhập ID hoặc URL
label_id_or_url = tk.Label(window, text="Nhập Pixiv ID hoặc URL:")
label_id_or_url.pack(pady=(10, 0)) # pady là khoảng cách đệm trên/dưới

# Tạo ô input để nhập ID - URL
entry_id_or_url = tk.Entry(window, width=100)
entry_id_or_url.pack(pady=(0, 10))


# Tạo Button hướng dẫn nhập đường dẫn lưu file
download_btn = tk.Button(window, text="Chọn vị trí lưu ảnh:", command=select_dir_path)
download_btn.pack(pady=(10, 0))

# Tạo chổ nhập đường dẫn lưu file
entry_dir_path = tk.Entry(window, width=100)
entry_dir_path.pack(pady=(0, 10))

download_btn = tk.Button(window, text="Tải xuống", command=download)
download_btn.pack(pady=10)

# Chạy vòng lặp chính để hiện cửa sổ
window.mainloop()