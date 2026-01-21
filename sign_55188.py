import os
import requests
import json
from datetime import datetime

SIGN_URL = "https://www.55188.com/plugin.php?id=sign&mod=add"
PUSHPLUS_URL = "https://www.pushplus.plus/send"

COOKIE = os.getenv("SIGN_COOKIE")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/144.0.0.0",
    "connection": "keep-alive",
    "cookie": COOKIE
}


def pushplus(title, content):
    if not PUSHPLUS_TOKEN:
        print("⚠️ 未配置 PUSHPLUS_TOKEN，跳过推送")
        return

    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "markdown"
    }

    try:
        r = requests.post(PUSHPLUS_URL, json=data, timeout=10)
        print("PushPlus 返回:", r.text)
    except Exception as e:
        print("❌ PushPlus 推送失败:", e)


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not COOKIE:
        msg = "❌ 未设置 SIGN_COOKIE"
        print(msg)
        pushplus("理想论坛 签到失败", msg)
        return

    try:
        r = requests.get(SIGN_URL, headers=HEADERS, timeout=15)
        print("HTTP:", r.status_code)
        print("响应:", r.text)

        if r.status_code == 200 and "success" in r.text:
            msg = f"""
### ✅ 理想论坛 签到成功

- 时间：{now}
- 返回：`{r.text}`
"""
            print("签到成功")
            pushplus("理想论坛 签到成功", msg)
        else:
            msg = f"""
### ❌ 理想论坛 签到失败

- 时间：{now}
- HTTP：{r.status_code}
- 返回：`{r.text}`
"""
            print("签到失败")
            pushplus("理想论坛 签到失败", msg)

    except Exception as e:
        msg = f"""
### ❌ 理想论坛 签到异常

- 时间：{now}
- 错误：`{str(e)}`
"""
        print(msg)
        pushplus("理想论坛 签到异常", msg)


if __name__ == "__main__":
    main()
