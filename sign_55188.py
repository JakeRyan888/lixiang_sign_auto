import os
import requests
import time  # 导入时间模块
from datetime import datetime

SIGN_URL = "https://www.55188.com/plugin.php?id=sign&mod=add"
CHECK_URL = "https://www.55188.com/home.php"
PUSHPLUS_URL = "https://www.pushplus.plus/send"

# 从环境变量获取配置
COOKIE = os.getenv("SIGN_COOKIE")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")
SIGN_IP = os.getenv("SIGN_IP")  # 新增：从 Secret 获取 IP (例如 171.213.250.189)

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

    # 1. 处理原始 Cookie
    if COOKIE:
        for kv in COOKIE.split(";"):
            if "=" in kv:
                k, v = kv.strip().split("=", 1)
                session.cookies.set(k, v)

    # 2. 动态生成 vOVx_56cc_lip 参数
    if SIGN_IP:
        # 生成当前 Unix 时间戳 (整数)
        timestamp = int(time.time())
        # 按照要求格式拼接：IP + URL编码后的逗号(%2C) + 时间戳
        lip_value = f"{SIGN_IP}%2C{timestamp}"
        session.cookies.set("vOVx_56cc_lip", lip_value)
        print(f"✅ 已注入动态 Cookie: vOVx_56cc_lip={lip_value}")
    else:
        print("⚠️ 未配置 SIGN_IP，跳过动态 Cookie 拼接")

    return session

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not COOKIE:
        pushplus("理想论坛 签到失败", "❌ 未设置 SIGN_COOKIE")
        return

    session = build_session()

    # ① 登录态检测
    try:
        r = session.get(CHECK_URL, timeout=15)
        if "退出" not in r.text:
            pushplus(
                "理想论坛 Cookie 失效",
                f"### ❌ 登录态失效\n\n- 时间：{now}\n- 请更新 Cookie"
            )
            return

        # ② 签到
        r = session.get(SIGN_URL, timeout=15)
        text = r.text

        if "已经签到" in text or "今日已签到" in text:
            pushplus("理想论坛 已签到", f"### ℹ️ 今日已签到\n\n- 时间：{now}")
        elif "签到成功" in text:
            pushplus("理想论坛 签到成功", f"### ✅ 签到成功\n\n- 时间：{now}")
        else:
            pushplus(
                "理想论坛 签到失败",
                f"### ❌ 签到异常\n\n- 时间：{now}\n- 返回片段：\n```{text[:300]}```"
            )
    except Exception as e:
        pushplus("理想论坛 运行出错", f"### ❌ 网络或脚本错误\n\n- 错误信息：{str(e)}")

if __name__ == "__main__":
    main()
