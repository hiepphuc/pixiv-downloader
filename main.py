import requests, os

headers = {
    "Referer": "https://www.pixiv.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

artwork_id = 126624328
response = requests.get(f"https://www.pixiv.net/ajax/illust/{artwork_id}/pages", headers=headers)

for img in response.json()["body"]:
    original_img_url = img["urls"]["original"]

    img_original = requests.get(url=original_img_url, headers=headers).content
    file_name = original_img_url.split("/").pop()
    dir_path = "D:/Images/Pixiv Images/"
    full_path = f"{dir_path}{file_name}"
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    with open(full_path, mode="wb") as file_img:
        file_img.write(img_original)
        print(f"Downloaded image: {original_img_url}")