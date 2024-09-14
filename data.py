import json
import requests
from PIL import Image
from io import BytesIO
from torchvision import transforms
from sea import get_favorite_list
def load_image_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            return img
        else:
            print(f"无法加载图像，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"加载图像时出现错误: {e}")
        return None

if __name__ == "__main__":
    fav=1238492880
    pn=1
    while True:
        has_more=get_favorite_list(fav,pn,f"./jsons/page_{pn}.json")["data"]["has_more"]
        if has_more:
            pn+=1
        else:
            break