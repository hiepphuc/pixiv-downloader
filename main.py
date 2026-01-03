import requests, os

# Cấu hình
headers = {
    "Referer": "https://www.pixiv.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}
artwork_id = 126624328
dir_path = "D:/Images/Pixiv Images/"

# Tạo thư mục: dùng makedirs để bao sân các trường hợp thư mục cha chưa có
os.makedirs(dir_path, exist_ok=True)

# Gọi API
api_url = f"https://www.pixiv.net/ajax/illust/{artwork_id}/pages"
response = requests.get(api_url, headers=headers)

# Kiểm tra xem request có thành công không, có thì tải
if response.status_code == 200:
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