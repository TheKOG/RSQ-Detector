import requests

def get_cookie():
    with open("cookie.txt", "r") as f:
        return f.read()

def get_uid(cookie=None):
    start = cookie.find('DedeUserID=') + len('DedeUserID=')
    end = cookie.find(';', start)
    uid = cookie[start:end]
    return uid

def get_favorite_list(media_id, pn, save_path=None, cookie=None):
    if cookie is None:
        cookie= get_cookie()
    url = "https://api.bilibili.com/x/v3/fav/resource/list"
    headers = {
        "authority": "api.bilibili.com",
        "method": "GET",
        "path": f"/x/v3/fav/resource/list?media_id={media_id}&pn={pn}&ps=20&keyword=&order=mtime&type=0&tid=0&platform=web",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cookie": cookie,
        "origin": "https://space.bilibili.com",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    }
    params = {
        "media_id": str(media_id),
        "pn": str(pn),
        "ps": "20",
        "keyword": "",
        "order": "mtime",
        "type": "0",
        "tid": "0",
        "platform": "web",
    }
    # 发送请求
    response = requests.get(url, headers=headers, params=params)
    # print(response.status_code)
    # print(response.text)
    if save_path is not None:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(response.text)
    return response.json()

def list_all(cookie=None):
    if cookie is None:
        cookie = get_cookie()
    uid=get_uid(cookie)
    url=f"https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid={uid}"
    headers = {
        "authority": "api.bilibili.com",
        "method": "GET",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cookie": cookie,
        "origin": "https://space.bilibili.com",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    }    
    response = requests.get(url, headers=headers)
    # print(response.status_code)
    # print(response.text)
    return response.json()["data"]["list"]
        
if __name__ == "__main__":
    # get_favorite_list(50942780, 1)
    # get_favorite_list(1722876280, 1)
    # get_favorite_list(3329746580, 1)
    data=list_all()
    dic={ele["id"]:ele["title"] for ele in data}
    print(dic)
    print("done")