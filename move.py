import requests

def get_cookie():
    with open("cookie.txt", "r") as f:
        return f.read()

def get_csrf(cookie=None):
    start = cookie.find('bili_jct=') + len('bili_jct=')
    end = cookie.find(';', start)
    csrf = cookie[start:end]
    return csrf

def get_uid(cookie=None):
    start = cookie.find('DedeUserID=') + len('DedeUserID=')
    end = cookie.find(';', start)
    uid = cookie[start:end]
    return uid

def move_video(media_id,tar_media_id=3329746580,id_type="112890715574044:2",cookie=None):
    if cookie is None:
        cookie = get_cookie()
        
    url = "https://api.bilibili.com/x/v3/fav/resource/move"
    uid=get_uid(cookie)
    headers = {
        "authority": "api.bilibili.com",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": cookie,
        "origin": "https://space.bilibili.com",
        "referer": f"https://space.bilibili.com/{uid}/favlist?fid={media_id}",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Microsoft Edge\";v=\"128\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    }
    
    # Define the payload
    payload = {
        "src_media_id": f"{media_id}",
        "tar_media_id": f"{tar_media_id}",
        "resources": id_type,
        "platform": "web",
        "csrf": get_csrf(cookie)
    }

    # Send the POST request
    response = requests.post(url, headers=headers, data=payload)

    # Print the response status code and content
    print(response.status_code)
    # print(response.json())

if __name__ == "__main__":
    move_video(51688080,3329746580,"112890715574044:2")
