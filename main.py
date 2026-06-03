import requests, os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

class PixivDownloaderApp:
    def __init__(self, root:tk.Tk) -> None:
        self.window = root
        self.window.title("Pixiv Downloader 🎨 (Hỗ trợ tài khoản)")
        self.window.geometry("1280x800") # [MỚI] Tăng chiều cao cửa sổ lên một chút

        # Cấu hình headers của request
        self.headers = {
            "Referer": "https://www.pixiv.net/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        }

        # Tạo Label hướng dẫn nhập ID hoặc URL
        self.label_id_or_url = tk.Label(self.window, text="Nhập Pixiv ID hoặc URL:")
        self.label_id_or_url.pack(pady=(10, 0))

        # Tạo ô input để nhập ID - URL
        self.entry_id_or_url = tk.Entry(self.window, width=100)
        self.entry_id_or_url.pack(pady=(0, 10))

        # [MỚI] Tạo Label và ô nhập Cookie để tải ảnh giới hạn
        self.label_cookie = tk.Label(self.window, text="Nhập PHPSESSID (Bắt buộc với ảnh R-18/Private, bỏ trống nếu tải ảnh thường):")
        self.label_cookie.pack(pady=(10, 0))
        self.entry_cookie = tk.Entry(self.window, width=100)
        self.entry_cookie.pack(pady=(0, 10))

        # Tạo Button hướng dẫn nhập đường dẫn lưu file
        self.btn_select_dir_path = tk.Button(self.window, text="Chọn vị trí lưu ảnh:", command=self.select_dir_path)
        self.btn_select_dir_path.pack(pady=(10, 0))

        # Tạo ô nhập đường dẫn lưu file
        self.entry_dir_path = tk.Entry(self.window, width=100)
        self.entry_dir_path.pack(pady=(0, 10))

        # Nút tải xuống
        self.btn_download = tk.Button(self.window, text="Tải xuống", command=self.start_download_thread)
        self.btn_download.pack(pady=10)

        # Label ghi lại quá trình tải
        self.label_log = tk.Label(self.window, text="")
        self.label_log.pack(pady=(10, 0))

    def select_dir_path(self):
        dir_path = filedialog.askdirectory()
        self.entry_dir_path.delete(0, tk.END)
        self.entry_dir_path.insert(0, dir_path)

    def download(self):
        artwork_id_or_url:str = self.entry_id_or_url.get()
        dir_path:str = self.entry_dir_path.get()
        cookie_val:str = self.entry_cookie.get().strip() # [MỚI] Lấy giá trị cookie

        if not artwork_id_or_url or not dir_path:
            self.btn_download.config(state=tk.NORMAL, text="Tải xuống")
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập ID và chọn thư mục!")
            return 
        
        # [MỚI] Xử lý Cookie vào headers
        if cookie_val:
            # Nếu người dùng chưa gõ chữ PHPSESSID= ở đầu thì tự thêm vào
            if "PHPSESSID" not in cookie_val:
                cookie_val = f"PHPSESSID={cookie_val}"
            self.headers["Cookie"] = cookie_val
        else:
            # Xóa cookie nếu phiên tải trước có nhập nhưng phiên này bỏ trống
            if "Cookie" in self.headers:
                del self.headers["Cookie"]

        # Xử lý ID
        artwork_id = artwork_id_or_url.strip("/").split("/").pop().split("?")[0]
        print(f"ID: {artwork_id} - Lưu tại: {dir_path}")

        try:
            self.label_log.config(text="Đang kết nối...")
            api_url = f"https://www.pixiv.net/ajax/illust/{artwork_id}/pages"
            
            response = requests.get(api_url, headers=self.headers, timeout=10) 
            
            # [MỚI] Bắt lỗi 401/404 cụ thể cho Pixiv khi thiếu quyền
            if response.status_code == 404 or response.status_code == 401 or (response.json().get("error") == True):
                raise ValueError("Không tìm thấy ảnh hoặc ảnh yêu cầu đăng nhập. Vui lòng nhập đúng PHPSESSID!")

            response.raise_for_status() 
            
            os.makedirs(dir_path, exist_ok=True)

            imgs:list = response.json()["body"]
            for i, img in enumerate(imgs, 1):
                original_img_url = img["urls"]["original"]
                file_name = original_img_url.split("/").pop()
                full_path = os.path.join(dir_path, file_name) 
                
                img_content = requests.get(original_img_url, headers=self.headers, timeout=10).content
                
                with open(full_path, mode="wb") as file_img:
                    file_img.write(img_content)

                print(f"Đã tải xong: {file_name}")
                self.label_log.config(text=f"Đang tải ảnh {i}/{len(imgs)}...")

            self.label_log.config(text="Hoàn tất!")
            messagebox.showinfo("Thành công", f"Đã tải xong {len(imgs)} ảnh!")
            
        except requests.exceptions.RequestException as e:
            print(f"Lỗi mạng: {e}")
            messagebox.showerror("Lỗi kết nối", "Không thể tải dữ liệu. Vui lòng kiểm tra mạng hoặc ID ảnh.")
        except ValueError as e: # [MỚI] Xử lý lỗi báo thiếu quyền
            print(f"Lỗi quyền truy cập: {e}")
            messagebox.showerror("Lỗi Quyền/Đăng nhập", str(e))
        except OSError as e:
            print(f"Lỗi ghi file: {e}")
            messagebox.showerror("Lỗi File", f"Không thể lưu file.\nChi tiết: {e}")
        except Exception as e:
            print(f"Lỗi không xác định: {e}")
            messagebox.showerror("Lỗi Lạ", f"Đã xảy ra lỗi không mong muốn:\n{e}")
        finally:
            self.btn_download.config(state=tk.NORMAL, text="Tải xuống")

    def start_download_thread(self):
        self.btn_download.config(state=tk.DISABLED, text="Đang tải...")
        download_thread = threading.Thread(target=self.download)
        download_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = PixivDownloaderApp(root)
    app.window.mainloop()
