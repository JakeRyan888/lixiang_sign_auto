import os
import requests
from datetime import datetime

SIGN_URL = "https://www.55188.com/plugin.php?id=sign&mod=add"
CHECK_URL = "https://www.55188.com/home.php"
PUSHPLUS_URL = "https://www.pushplus.plus/send"

COOKIE = os.getenv("SIGN_COOKIE")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.55188.com/",
    "Connection": "keep-alive",
}


def pushplus(title, content):
    if not PUSHPLUS_TOKEN:
        print("⚠️ 未配置 PUSHPLUS_TOKEN")
        return

    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "markdown"
    }

    try:
        requests.post(PUSHPLUS_URL, json=data, timeout=10)
    except Exception as e:
        print("PushPlus 推送失败:", e)


def build_session():
    session = requests.Session()
    session.headers.update(HEADERS)

    for kv in COOKIE.split(";"):
        if "=" in kv:
            k, v = kv.strip().split("=", 1)
            session.cookies.set(k, v)

    return session


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not COOKIE:
        pushplus("理想论坛 签到失败", "❌ 未设置 SIGN_COOKIE")
        return

    session = build_session()

    # ① 登录态检测
    r = session.get(CHECK_URL, timeout=10)
    if "退出" not in r.text:
        pushplus(
            "理想论坛 Cookie 失效",
            f"### ❌ 登录态失效\n\n- 时间：{now}\n- 请更新 Cookie"
        )
        return

    # ② 签到
    r = session.get(SIGN_URL, timeout=10)
    text = r.text

    if "已经签到" in text or "今日已签到" in text:
        pushplus(
            "理想论坛 已签到",
            f"### ℹ️ 今日已签到\n\n- 时间：{now}"
        )
    elif "签到成功" in text:
        pushplus(
            "理想论坛 签到成功",
            f"### ✅ 签到成功\n\n- 时间：{now}"
        )
    else:
        pushplus(
            "理想论坛 签到失败",
            f"### ❌ 签到异常\n\n- 时间：{now}\n- 返回片段：\n```{text[:300]}```"
        )


if __name__ == "__main__":
    main()
