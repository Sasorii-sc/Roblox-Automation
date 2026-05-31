import pyautogui
import PIL.Image
import pyscreeze
import asyncio
import warnings
import os
import sys
import subprocess
import re
import pyperclip
import random
import locale
import html
import gc
import threading
import builtins
import requests
import tempfile
import ctypes
import webbrowser
import logging
from datetime import datetime
from collections import deque
from functools import wraps
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from DrissionPage import Chromium, ChromiumOptions, errors
from tqdm import TqdmExperimentalWarning
from tqdm.rich import tqdm

from lib.lib import Main, getResourcePath

warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ACC_FILE = os.path.join(BASE_DIR, "accounts.txt")

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

def security_check():
    FORBIDDEN_PROCESSES = [
        "x64dbg.exe", "x32dbg.exe", "ida64.exe", "ida.exe", 
        "wireshark.exe", "fiddler.exe", "httpdebugger.exe", 
        "processhacker.exe", "dnspy.exe", "ollydbg.exe",
        "cheatengine-x86_64.exe", "cheatengine-i386.exe",
    ]
    
    try:
        cmd = 'tasklist /NH /FO CSV'
        output = subprocess.check_output(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode('cp1254', errors='ignore')
        
        for proc in FORBIDDEN_PROCESSES:
            if proc.lower() in output.lower():
                print(f"\n[SECURITY] CRITICAL THREAT DETECTED: {proc}")
                print("[SECURITY] SYSTEM SELF-DESTRUCT INITIATED.")
                os._exit(0) 
                
        if ctypes.windll.kernel32.IsDebuggerPresent():
            print("\n[SECURITY] DEBUGGER ATTACHED! EMERGENCY SHUTDOWN.")
            os._exit(0)
            
    except Exception:
        pass

def get_hwid():
    try:
        cmd = 'powershell -command "(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"'
        uuid = subprocess.check_output(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
        if uuid: return uuid
        return "ID_NOT_FOUND"
    except Exception:
        try: return os.popen('vol c:').read().strip().split(' ')[-1]
        except: return "CRITICAL_HWID_ERROR"

AUTHORIZED_HWIDS = {
    "0479FC80-E657-11ED-845E-079466F61700": "2010-05-04", 
}

LICENSE_VALID = False
LICENSE_INFO = "UNVERIFIED"
EASTER_EGG_ACTIVE = False

def get_network_date():
    try:
        res = requests.head('https://www.google.com', timeout=5)
        if res.headers.get('Date'):
            date_str = " ".join(res.headers.get('Date').split(" ")[1:4])
            return datetime.strptime(date_str, "%d %b %Y").date()
    except: pass

    try:
        res = requests.head('https://www.apple.com', timeout=5)
        if res.headers.get('Date'):
            date_str = " ".join(res.headers.get('Date').split(" ")[1:4])
            return datetime.strptime(date_str, "%d %b %Y").date()
    except: pass

    try:
        res = requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC', timeout=5)
        return datetime.strptime(res.json()['datetime'][:10], "%Y-%m-%d").date()
    except: pass

    print("\n" + "="*70)
    print(" 🌐 CRITICAL ERROR - TIME SYNC FAILED 🌐 ")
    print("="*70)
    print("\n[SECURITY] Could not verify global time from 3 different sources.")
    print("Please ensure your internet is connected to validate license.\n")
    return None

def verify_license():
    global LICENSE_VALID, LICENSE_INFO, EASTER_EGG_ACTIVE
    security_check()
    current_hwid = get_hwid()
    
    if current_hwid not in AUTHORIZED_HWIDS:
        LICENSE_VALID = False
        LICENSE_INFO = "UNAUTHORIZED"
        try: ctypes.windll.kernel32.SetConsoleTitleW("Firewall Security - Unauthorized Access")
        except: pass
        print("\n" + "="*70)
        print(" 🚨 ACCESS DENIED - VALID LICENSE NOT FOUND 🚨 ")
        print("="*70)
        print(f"\n🔑 Your Device ID: {current_hwid}\n")
        return
        
    expiry_str = AUTHORIZED_HWIDS[current_hwid]
    if expiry_str.upper() == "LIFETIME":
        LICENSE_VALID = True
        LICENSE_INFO = "LIFETIME"
    else:
        try:
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            today = get_network_date() 
            if today is None:
                LICENSE_VALID = False
                LICENSE_INFO = "NETWORK ERROR"
                return

            days_left = (expiry_date - today).days
            
            if days_left <= -365:
                EASTER_EGG_ACTIVE = True
                LICENSE_VALID = False
                LICENSE_INFO = "EASTER EGG EXPIRED"
                try: ctypes.windll.kernel32.SetConsoleTitleW("ZORT - BUSTED")
                except: pass
                print("\n[!] MEGA EXPIRED DETECTED. PREPARING SPECIAL SURPRISE...")
                
            elif days_left < 0:
                LICENSE_VALID = False
                LICENSE_INFO = "EXPIRED"
                try: ctypes.windll.kernel32.SetConsoleTitleW("System Security - License Expired")
                except: pass
                print("\n" + "!"*70)
                print(" ⏳ YOUR LICENSE HAS EXPIRED - SÜRENİZ DOLDU ⏳ ")
                print("!"*70)
                print(f"\n[WARNING] Your license for device {current_hwid} expired on {expiry_str}.")
                print(">>> Lütfen yeni bir lisans paketi almak için bizimle iletişime geçin.")
                print("\n" + "!"*70 + "\n")
            else:
                LICENSE_VALID = True
                LICENSE_INFO = f"{days_left} DAYS LEFT"
        except ValueError:
            LICENSE_VALID = False
            LICENSE_INFO = "INVALID CONFIG"

verify_license()

app = Flask(__name__)
app.secret_key = "AUTONOMOUS_ultimate_secret_key_2026_xyz"

VALID_USERS = {
    "Sasorii": "Sasorii",
    "froxyy": "froxyy"
}
SECURITY_WEBHOOK = "https://discord.com/api/webhooks/1482405364111642675/JW0Vf8WeGtWbT5mGjOh8_WYVjdi7wi3_74lbp33geATbBt0EUHJlH2axSzna0qg-2R73"

BOT_LOGS = deque(maxlen=300)
BOT_STATUS = "System Ready. Standing by..."
STOP_FLAG = False 
STATS = {"success": 0, "error": 0, "total": 0}

class OutputCapturer:
    def __init__(self):
        self.terminal = sys.__stdout__

    def write(self, message):
        msg_str = message.decode('utf-8', errors='ignore') if isinstance(message, bytes) else str(message)
        
        term_msg = re.sub(r'<[^>]+>', '', msg_str)
        term_msg = html.unescape(term_msg)
        self.terminal.write(term_msg)
        self.terminal.flush()

        clean_msg = msg_str.strip()
        if clean_msg and not clean_msg.startswith('\r'):
            time_str = datetime.now().strftime("%H:%M:%S")
            BOT_LOGS.append(f"<span class='time'>[{time_str}]</span> {clean_msg}")

    def flush(self):
        self.terminal.flush()

sys.stdout = OutputCapturer()

def find_browser():
    paths_to_check = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    for path in paths_to_check:
        if os.path.exists(path):
            return path
    return ""

def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"): return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'): return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'): return jsonify({"error": "Unauthorized access. Please login."}), 401
        return f(*args, **kwargs)
    return decorated_function

def send_discord_webhook(webhook_url, username, password, email, details):
    if not webhook_url: return
    data = {
        "username": "Roblox Autonomous System",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/6062/6062646.png",
        "content": "✅ **A new operation has been successfully completed!**",
        "embeds": [{
            "title": "🛡️ Autonomous Systems - Detailed Operation Report",
            "color": 3447003,
            "fields": [
                {"name": "👤 Account Information", "value": f"**Username:** `{username}`\n**Password:** `||{password}||`\n**Email:** `{email if email else 'Not Used'}`", "inline": False},
                {"name": "⚙️ Operation Details", "value": f"**Group Join:** {details.get('group', 'Not Requested')}\n**Game Like:** {details.get('game', 'Not Requested')}\n**Follow Action:** {details.get('follow', 'Not Requested')}\n**Camouflage (Bio):** {details.get('bio', 'Not Requested')}", "inline": False},
                {"name": "🌐 Network Info", "value": f"**Proxy Used:** `{details.get('proxy', 'Local IP (Not Used)')}`", "inline": False}
            ],
            "footer": {"text": f"Roblox Command Center | Operation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
        }]
    }
    headers = {"Content-Type": "application/json"}
    try: requests.post(webhook_url, json=data, headers=headers)
    except: pass

def safe_ele(page, selectors, timeout=10):
    for sel in selectors:
        try:
            el = page.ele(sel, timeout=timeout)
            if el: return el
        except errors.ElementNotFoundError: continue
    return None

async def set_random_bio(page):
    try:
        bios = ["Hello everyone!", "Roblox King", "Trading only, send offers.", "Just playing around with friends.", "New account, let's play!", "Hi, I love playing games.", "Gamer till the end.", "I love blox fruits!"]
        selected_bio = random.choice(bios)
        csrf_token = ""
        csrf_meta = page.ele('xpath://meta[@name="csrf-token"]', timeout=3)
        if csrf_meta: csrf_token = csrf_meta.attr('data-token')
        cookies_dict = {cookie['name']: cookie['value'] for cookie in page.cookies()}
        api_url = "https://users.roblox.com/v1/description"
        headers = {"X-CSRF-TOKEN": csrf_token, "Content-Type": "application/json", "Accept": "application/json"}
        response = requests.post(api_url, headers=headers, cookies=cookies_dict, json={"description": selected_bio})
        if response.status_code == 403 and 'x-csrf-token' in response.headers:
            headers['X-CSRF-TOKEN'] = response.headers['x-csrf-token']
            requests.post(api_url, headers=headers, cookies=cookies_dict, json={"description": selected_bio})
    except: pass

async def join_group(page, group_link):
    try:
        print(f"Navigating to target group: {group_link}")
        page.get(group_link)
        await asyncio.sleep(2)
        match = re.search(r'/(?:groups|communities)/(\d+)', group_link)
        if not match: return
        group_id = match.group(1)
        csrf_token = ""
        csrf_meta = page.ele('xpath://meta[@name="csrf-token"]', timeout=3)
        if csrf_meta: csrf_token = csrf_meta.attr('data-token')
        cookies_dict = {cookie['name']: cookie['value'] for cookie in page.cookies()}
        api_url = f"https://groups.roblox.com/v1/groups/{group_id}/users"
        headers = {"X-CSRF-TOKEN": csrf_token, "Content-Type": "application/json", "Accept": "application/json"}
        response = requests.post(api_url, headers=headers, cookies=cookies_dict)
        if response.status_code == 403 and 'x-csrf-token' in response.headers:
            headers['X-CSRF-TOKEN'] = response.headers['x-csrf-token']
            response = requests.post(api_url, headers=headers, cookies=cookies_dict)
        await asyncio.sleep(2)
        if page.ele('#arkose-iframe', timeout=2) or page.ele('.arkose-iframe', timeout=1):
            print("[WARNING] Captcha verification appeared while joining group! NopeCHA is solving it.")
            await asyncio.sleep(6)
    except: pass

async def like_game(page, game_link):
    try:
        print(f"Navigating to target game: {game_link}")
        page.get(game_link)
        await asyncio.sleep(3)
        like_btn = safe_ele(page, ['#voting-upvote', '.icon-like', '@@class=icon-like', 'xpath://div[@id="voting-upvote"]', 'xpath://span[contains(@class, "icon-like")]/..'], timeout=10)
        if like_btn:
            like_btn.click(by_js=True)
            print(f"[SUCCESS] Game successfully liked.")
            await asyncio.sleep(1)
    except: pass

async def follow_users_updated(page, usernames):
    for user in usernames:
        if STOP_FLAG: break
        try:
            print(f"Searching for user: {user}")
            page.get(f"https://www.roblox.com/search/users?keyword={user}")
            await asyncio.sleep(2)
            first_profile = safe_ele(page, ['.avatar-card-link', '@@class=avatar-card-link'])
            if first_profile:
                first_profile.click(by_js=True)
                await asyncio.sleep(4) 
                try:
                    pyautogui.moveTo(10, 10) 
                    human_delay = random.uniform(0.8, 1.8)
                    await asyncio.sleep(human_delay)
                    more_loc = pyautogui.locateCenterOnScreen('more_btn.png', confidence=0.8)
                    if more_loc:
                        offset_x = random.randint(-4, 4)
                        offset_y = random.randint(-4, 4)
                        pyautogui.moveTo(more_loc.x + offset_x, more_loc.y + offset_y, duration=random.uniform(0.3, 0.6))
                        pyautogui.moveTo(more_loc.x, more_loc.y, duration=0.2)
                        pyautogui.click()
                        await asyncio.sleep(1.5) 
                        follow_loc = pyautogui.locateCenterOnScreen('follow_btn.png', confidence=0.8)
                        if follow_loc:
                            pyautogui.moveTo(follow_loc.x + random.randint(-3,3), follow_loc.y + random.randint(-3,3), duration=random.uniform(0.2, 0.5))
                            pyautogui.click()
                            print(f"[SUCCESS] ✅ FOLLOWED {user} VIA IMAGE RECOGNITION! 💸")
                except Exception as img_err: pass
            await asyncio.sleep(1)
        except: pass

async def bot_runner(config):
    global BOT_STATUS, STOP_FLAG, STATS
    STOP_FLAG = False
    BOT_STATUS = "Bot is active, operation initiated."
    print("--- NEW TASK CHAIN INITIATED ---")
    
    security_check()

    original_input = builtins.input
    def auto_input(prompt=""):
        if "Ungoogled" in prompt or "install" in prompt: return "n"
        return "y"
    builtins.input = auto_input

    try:
        lib = Main()
        co = ChromiumOptions()
        co.set_argument("--lang", "en") 
        co.set_argument("--no-first-run") 
        co.set_argument("--no-default-browser-check") 
        co.set_argument("--no-sandbox")
        co.set_argument("--disable-gpu")
        co.set_argument("--disable-dev-shm-usage")
        co.set_argument("--disable-background-networking")
        co.set_argument("--disable-sync")
        co.set_argument("--password-store=basic")
        co.set_argument("--disable-blink-features=AutomationControlled")
        
        co.auto_port().mute(True)

        print("Checking updates and requirements...")
        await lib.checkUpdate()
        
        try:
            lib.promptAnalytics()
        except PermissionError:
            print("[INFO] Analytics file is locked by system, skipping safely...")
        except Exception:
            pass
        
        try: lib.downloadUngoogledChromium()
        except: pass

        browser_path = config.get("browser_path", "").strip()
        if not browser_path or not os.path.exists(browser_path):
            browser_path = find_browser()
            
        if os.path.exists(browser_path): co.set_browser_path(browser_path)
        else:
            print(f"[CRITICAL] Browser not found! Path: {browser_path}")
            BOT_STATUS = "Operation Failed: Browser Missing"
            return 

        if config.get("incognito") and not config.get("captcha_bypass"): co.incognito()

        if config.get("captcha_bypass"):
            print("NopeCHA extension is loading into the system...")
            co.add_extension(getResourcePath("lib/NopeCHA"))

        usableProxies = []
        proxyList = []
        
        if config.get("use_decodo"):
            print("--- [SYSTEM] Decodo Autonomous Logistics Network Initiating ---")
            d_user = 'sp468s50hj'
            d_pass = '=llEzqcemqR5z2VV49'
            d_host = 'gate.decodo.com'
            for port in range(10001, 10011):
                proxyList.append(f"http://{d_user}:{d_pass}@{d_host}:{port}")
        elif config.get("proxies"):
            proxy_raw = config.get("proxies", "")
            proxyList = [p.strip() for p in proxy_raw.replace(",", " ").split() if p.strip()]

        if proxyList:
            print(f"--- [SYSTEM] ANALYZING {len(proxyList)} PROXIES ---")
            for proxy in proxyList:
                is_working, status_code = lib.testProxy(proxy)
                display_proxy = f"Decodo Port: {proxy.split(':')[-1]}" if config.get("use_decodo") else proxy
                if is_working:
                    print(f"<span style='color:#10b981'>[ACTIVE] {display_proxy} connected. ✅</span>")
                    usableProxies.append(proxy)
                else:
                    print(f"<span style='color:#ef4444'>[DEAD] {display_proxy} rejected (Error: {status_code}). ❌</span>")

        executionCount = int(config.get("execution_count", 1))
        accounts = []
        mode = config.get("mode", "create") 
        webhook_url = config.get("discord_webhook", "").strip()

        STATS["total"] = executionCount

        if mode == "create":
            for x in range(executionCount):
                security_check()
                if STOP_FLAG: break
                BOT_STATUS = f"Creating account [{x+1}/{executionCount}]"
                print(f"\n[{x+1}/{executionCount}] New account creation process starting.")
                
                raw_prefix = config.get("name_prefix", "")
                if raw_prefix and "," in raw_prefix:
                    prefix_list = [p.strip() for p in raw_prefix.split(",") if p.strip()]
                    selected_prefix = random.choice(prefix_list)
                else:
                    selected_prefix = raw_prefix if raw_prefix else None

                username = lib.usernameCreator(selected_prefix)
                
                if not config.get("password") or config.get("password").strip() == "":
                    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$"
                    passw = "".join(random.choice(chars) for _ in range(random.randint(12, 16)))
                    print(f"<span style='color:#facc15'>[SECURITY] Unique password generated for this account: {passw}</span>")
                else:
                    passw = config.get("password")
                
                email, emailPassword = None, None
                page_ready = False
                active_proxy = None
                proxy_retry_limit = min(5, len(usableProxies)) if usableProxies else 1
                if proxy_retry_limit < 1: proxy_retry_limit = 1

                for attempt in range(proxy_retry_limit):
                    if STOP_FLAG: break
                    active_proxy = random.choice(usableProxies) if usableProxies else None
                    
                    if active_proxy:
                        clean_proxy = active_proxy.replace('http://', '').replace('https://', '')
                        co.set_proxy(clean_proxy)
                    else:
                        co.set_proxy('') 

                    try:
                        chrome = Chromium(addr_or_opts=co)
                        page = chrome.latest_tab
                        page.set.window.max()

                        page.get("https://www.roblox.com/CreateAccount")
                        await asyncio.sleep(4) 

                        if page.ele("#MonthDropdown", timeout=3):
                            page_ready = True
                            print(f"<span style='color:#10b981'>[SUCCESS] Roblox firewall bypassed!</span>")
                            break 
                        else:
                            if active_proxy and active_proxy in usableProxies: usableProxies.remove(active_proxy) 
                            try: chrome.quit()
                            except: pass
                    except Exception as e:
                        if active_proxy and active_proxy in usableProxies: usableProxies.remove(active_proxy)
                        try: chrome.quit()
                        except: pass

                if not page_ready:
                    print(f"<span style='color:#ef4444'>[ERROR] All proxy attempts failed!</span>")
                    STATS["error"] += 1
                    continue

                if config.get("verify_email"):
                    try:
                        email, emailPassword, token, emailID = await lib.generateEmail(passw)
                        print(f"Assigned Email: {email}")
                    except: pass
                
                try:
                    page.ele("#MonthDropdown", timeout=10).select.by_value(datetime.now().strftime("%b"))
                    page.ele("#DayDropdown", timeout=10).select.by_value(str(datetime.now().day))
                    page.ele("#YearDropdown", timeout=10).select.by_value(str(datetime.now().year - 19))
                    page.ele("#signup-username", timeout=10).input(username)
                    page.ele("#signup-password", timeout=10).input(passw)
                    await asyncio.sleep(1)
                    page.ele("@@id=signup-button@@name=signupSubmit", timeout=10).click(by_js=True)
                    
                    print("Registration form submitted, waiting for system to log in (15 sec)...")
                    await asyncio.sleep(15)
                    
                    if config.get("verify_email") and email:
                        print("Proceeding to email verification process...")
                        try:
                            try: page.ele(".btn-primary-md btn-primary-md btn-min-width", timeout=3).click(by_js=True)
                            except: pass

                            if page.ele("@@class=phone-verification-nonpublic-text text-description font-caption-body", timeout=3):
                                page.get("https://www.roblox.com/my/account#!/info")
                                await asyncio.sleep(2)
                                page.ele("@@class=account-field-edit-action@@text()=Add Email").click(by_js=True)
                                await asyncio.sleep(0.5)
                                page.ele("@@id=emailAddress@@name=userInfo.emailAddress@@type=email@@class=form-control input-field@@placeholder=Enter email@@autocomplete=off").input(email)
                                page.ele("@@class=modal-full-width-button btn-primary-md btn-min-width@@text()=Add Email").click(by_js=True)
                            elif page.ele(". form-control input-field verification-upsell-modal-input", timeout=3) or page.ele(".form-control input-field verification-upsell-modal-input", timeout=1):
                                modal_input = page.ele(". form-control input-field verification-upsell-modal-input") or page.ele(".form-control input-field verification-upsell-modal-input")
                                modal_input.input(email)
                                page.ele(".modal-button verification-upsell-btn btn-cta-md btn-min-width").click(by_js=True)
                            else:
                                page.get("https://www.roblox.com/my/account#!/info")
                                await asyncio.sleep(2)
                                add_email_btn = safe_ele(page, ['@@class=account-field-edit-action@@text()=Add Email', '.account-field-edit-action'])
                                if add_email_btn:
                                    add_email_btn.click(by_js=True)
                                    await asyncio.sleep(1)
                                    page.ele("@@id=emailAddress", timeout=5).input(email)
                                    page.ele("@@class=modal-full-width-button btn-primary-md btn-min-width@@text()=Add Email").click(by_js=True)

                            print("Scanning inbox...")
                            link = None
                            emailCheckAttempts = 0
                            
                            while emailCheckAttempts < 30:
                                try:
                                    messages = lib.fetchVerification(email, emailPassword, emailID)
                                    if len(messages) > 0: 
                                        msg = messages[0]
                                        body = getattr(msg, 'text', None)
                                        if not body and hasattr(msg, 'html') and msg.html: body = msg.html[0]
                                        if body:
                                            match = re.search(r'https://www\.roblox\.com/account/settings/verify-email\?ticket=[^\s)"]+', body)
                                            if match: link = match.group(0)
                                        break
                                    await asyncio.sleep(5)
                                    emailCheckAttempts += 1
                                except:
                                    emailCheckAttempts += 1
                                    await asyncio.sleep(5)

                            if link:
                                page.get(link)
                                await asyncio.sleep(3)
                                print("[SUCCESS] Email successfully verified.")
                        except: pass

                    await set_random_bio(page) 
                    if config.get("customize_avatar"): await lib.customization(page)
                    if not STOP_FLAG and config.get("group_link"): await join_group(page, config.get("group_link"))
                    if not STOP_FLAG and config.get("game_link"): await like_game(page, config.get("game_link"))
                    if not STOP_FLAG and config.get("follow_users"):
                        users_to_follow = [u.strip() for u in config.get("follow_users").split(",") if u.strip()]
                        await follow_users_updated(page, users_to_follow)

                    accountCookies = [{"name": c["name"], "value": c["value"]} for c in page.cookies()]
                    currentAccount = {"username": username, "password": passw, "email": email, "emailPassword": emailPassword, "cookies": accountCookies}
                    accounts.append(currentAccount)
                    await lib.saveAccount(currentAccount)
                    
                    print(f"[{x+1}/{executionCount}] Operation complete! Account: {username}")
                    STATS["success"] += 1
                    
                    proxy_display = "Local IP (Not Used)"
                    if active_proxy: proxy_display = f"🟢 Decodo Residential IP (Port: {active_proxy.split(':')[-1]})" if config.get("use_decodo") else active_proxy
                        
                    operation_details = {
                        "group": "✅ Applied" if config.get("group_link") else "➖ Not Requested",
                        "game": "✅ Applied" if config.get("game_link") else "➖ Not Requested",
                        "follow": "✅ Applied" if config.get("follow_users") else "➖ Not Requested",
                        "bio": "✅ Added (Camouflage)",
                        "proxy": proxy_display
                    }
                    send_discord_webhook(webhook_url, username, passw, email, operation_details)
                    
                except Exception as e:
                    print(f"[ERROR] Critical error: {e}")
                    STATS["error"] += 1
                finally:
                    try: chrome.quit()
                    except: pass

        elif mode == "login":
            try:
                with open(ACC_FILE, "r") as f:
                    lines = f.readlines()
                    valid_lines = [l for l in lines if "Username:" in l and "Password:" in l]
                    
                    if config.get("random_accounts"):
                        random.shuffle(valid_lines)
                        
                    target_count = min(executionCount, len(valid_lines))
                    valid_lines = valid_lines[:target_count]
                    STATS["total"] = len(valid_lines)
                    
                    for i, line in enumerate(valid_lines):
                        security_check()
                        if STOP_FLAG: break
                        parts = line.split(",")
                        user = parts[0].split(":")[1].strip()
                        pw = parts[1].split(":")[1].strip()
                        
                        registered_email = "None"
                        for p in parts:
                            if "Email:" in p and "Password" not in p:
                                registered_email = p.split(":")[1].strip()

                        print(f"\n[{i+1}/{len(valid_lines)}] Attempting login: {user}")
                        
                        page_ready = False
                        active_proxy = None
                        proxy_retry_limit = min(5, len(usableProxies)) if usableProxies else 1
                        if proxy_retry_limit < 1: proxy_retry_limit = 1

                        for attempt in range(proxy_retry_limit):
                            if STOP_FLAG: break
                            active_proxy = random.choice(usableProxies) if usableProxies else None
                            if active_proxy:
                                clean_proxy = active_proxy.replace('http://', '').replace('https://', '')
                                co.set_proxy(clean_proxy)
                            else:
                                co.set_proxy('')

                            try:
                                chrome = Chromium(addr_or_opts=co)
                                page = chrome.latest_tab

                                page.get("https://www.roblox.com/login")
                                await asyncio.sleep(4)

                                if page.ele('#login-username', timeout=3):
                                    page_ready = True
                                    break
                                else:
                                    if active_proxy and active_proxy in usableProxies: usableProxies.remove(active_proxy)
                                    try: chrome.quit()
                                    except: pass
                            except Exception as e:
                                if active_proxy and active_proxy in usableProxies: usableProxies.remove(active_proxy)
                                try: chrome.quit()
                                except: pass

                        if not page_ready:
                            print(f"<span style='color:#ef4444'>[ERROR] Login page could not be opened. Skipping.</span>")
                            STATS["error"] += 1
                            continue

                        try:
                            page.ele('#login-username').input(user)
                            page.ele('#login-password').input(pw)
                            page.ele('#login-button').click(by_js=True)
                            await asyncio.sleep(8)
                            
                            await set_random_bio(page) 
                            if not STOP_FLAG and config.get("group_link"): await join_group(page, config.get("group_link"))
                            if not STOP_FLAG and config.get("game_link"): await like_game(page, config.get("game_link"))
                            if not STOP_FLAG and config.get("follow_users"):
                                users_to_follow = [u.strip() for u in config.get("follow_users").split(",") if u.strip()]
                                await follow_users_updated(page, users_to_follow)
                            
                            STATS["success"] += 1
                            
                            proxy_display = "Local IP (Not Used)"
                            if active_proxy: proxy_display = f"🟢 Decodo Residential IP (Port: {active_proxy.split(':')[-1]})" if config.get("use_decodo") else active_proxy
                                
                            operation_details = {
                                "group": "✅ Applied" if config.get("group_link") else "➖ Not Requested",
                                "game": "✅ Applied" if config.get("game_link") else "➖ Not Requested",
                                "follow": "✅ Applied" if config.get("follow_users") else "➖ Not Requested",
                                "bio": "✅ Added (Camouflage)",
                                "proxy": proxy_display
                            }
                            send_discord_webhook(webhook_url, user, pw, registered_email, operation_details)
                        except Exception as e:
                            STATS["error"] += 1
                        finally:
                            try: chrome.quit()
                            except: pass

            except FileNotFoundError:
                print(f"<span style='color:#ef4444'>[CRITICAL] {ACC_FILE} file not found! Please create it.</span>")

        BOT_STATUS = "System Standby (Operation Completed)"
    finally:
        builtins.input = original_input


EASTER_EGG_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ZOOORT! - SİSTEM KİLİTLENDİ</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #050505; color: #ef4444; font-family: 'Impact', sans-serif; text-align: center; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; overflow: hidden; }
        h1 { font-size: 6rem; margin-bottom: 10px; text-shadow: 0 0 30px #ef4444; animation: shake 0.4s infinite; letter-spacing: 5px; }
        p { font-size: 1.8rem; color: #fca5a5; font-weight: bold; background: rgba(220,38,38,0.1); padding: 20px; border-radius: 10px; border: 2px dashed #ef4444; line-height: 1.4; }
        img { max-width: 500px; border-radius: 10px; border: 4px solid #ef4444; margin: 20px 0; box-shadow: 0 0 50px #ef4444; }
        .footer-meme { position: absolute; bottom: 30px; color: #64748b; font-family: monospace; font-size: 1.2rem; letter-spacing: 2px; text-shadow: 0 0 5px #64748b;}
        @keyframes shake { 0% { transform: translate(2px, 2px) rotate(0deg); } 10% { transform: translate(-2px, -3px) rotate(-1deg); } 20% { transform: translate(-4px, 0px) rotate(1deg); } 30% { transform: translate(4px, 3px) rotate(0deg); } 40% { transform: translate(2px, -2px) rotate(1deg); } 50% { transform: translate(-2px, 3px) rotate(-1deg); } 60% { transform: translate(-4px, 2px) rotate(0deg); } 70% { transform: translate(4px, 2px) rotate(-1deg); } 80% { transform: translate(-2px, -2px) rotate(1deg); } 90% { transform: translate(2px, 3px) rotate(0deg); } 100% { transform: translate(2px, -3px) rotate(-1deg); } }
    </style>
</head>
<body>
    <h1>OOPS! 🤡</h1>
    <p>IT'S BEEN A YEAR SINCE YOUR LICENSE EXPIRED—ARE YOU STILL TRYING TO SNEAK IN FOR FREE?! Renew your license</p>
    <img src="https://media1.tenor.com/m/b545m662T0QAAAAd/clown-clown-meme.gif" alt="Fakir">
    <div class="footer-meme">
        MADE BY FROXY & SASORİİ<br>
        <span style="font-size:0.9rem; color:#475569; display:block; margin-top:8px;">17.03.2026 - {{ today }} Anı</span>
    </div>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox Systems - Authorization</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #000000; color: #f8fafc; font-family: 'Courier New', Courier, monospace; height: 100vh; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .login-box { background: rgba(17, 24, 39, 0.92); border: 1px solid #dc2626; border-radius: 12px; box-shadow: 0 0 35px rgba(220, 38, 38, 0.5); padding: 40px; width: 100%; max-width: 420px; z-index: 10; position: relative; backdrop-filter: blur(8px); }
        .logo-icon { font-size: 2rem; color: #dc2626; text-align: center; margin-bottom: 10px; text-shadow: 0 0 15px #dc2626; }
        .login-title { text-align: center; color: #f8fafc; font-weight: bold; margin-bottom: 15px; letter-spacing: 2px; }
        .form-control { background: #1f2937; border: 1px solid #374151; color: #fff; border-radius: 5px; }
        .form-control:focus { background: #1f2937; border-color: #dc2626; color: #fff; box-shadow: 0 0 8px rgba(220, 38, 38, 0.5); }
        .btn-login { background: #dc2626; color: #fff; font-weight: bold; width: 100%; margin-top: 20px; transition: 0.3s; border: none; letter-spacing: 1px;}
        .btn-login:hover { background: #b91c1c; box-shadow: 0 0 15px #dc2626; color: #fff;}
        .error-msg { color: #ef4444; text-align: center; font-size: 0.9rem; margin-bottom: 15px; font-family: sans-serif; }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo-icon"><i class="fa-solid fa-robot"></i></div>
        <h4 class="login-title">AUTONOMOUS ROBLOX SYSTEM<br><span style="font-size: 1rem; color:#dc2626;">ACCESS PANEL</span></h4>
        
        {% if error %}
        <div class="error-msg"><i class="fa-solid fa-triangle-exclamation"></i> {{ error }}</div>
        {% endif %}
        
        <form method="POST" action="/login">
            <div class="mb-3">
                <div class="input-group">
                    <span class="input-group-text" style="background:#1f2937; border-color:#374151; color:#9ca3af;"><i class="fa-solid fa-user"></i></span>
                    <input type="text" class="form-control" name="username" placeholder="Authorized Personnel" required autocomplete="off">
                </div>
            </div>
            <div class="mb-3">
                <div class="input-group">
                    <span class="input-group-text" style="background:#1f2937; border-color:#374151; color:#9ca3af;"><i class="fa-solid fa-lock"></i></span>
                    <input type="password" class="form-control" name="password" placeholder="Password" required>
                </div>
            </div>
            <button type="submit" class="btn btn-login"><i class="fa-solid fa-right-to-bracket me-2"></i> LOGIN</button>
        </form>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROBLOX | Autonomous Control</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --bg-color: #0b0f19; --panel-bg: #111827; --text-main: #f3f4f6; --text-muted: #9ca3af; --accent-color: #0ea5e9; --danger-color: #ef4444; --border-color: #1f2937; --terminal-bg: #030712; --terminal-text: #10b981; }
        body { background-color: var(--bg-color); color: var(--text-main); font-family: 'Segoe UI', system-ui, sans-serif; margin-bottom: 40px; }
        .header-title { color: #fff; font-weight: 700; text-shadow: 0 0 10px rgba(14, 165, 233, 0.5); margin: 30px 0; display: flex; justify-content: space-between; align-items: center;}
        .control-panel { background-color: rgba(17, 24, 39, 0.94); border: 1px solid #334155; border-radius: 12px; box-shadow: 0 4px 30px rgba(0,0,0,0.8); padding: 25px; position: relative; overflow: hidden; backdrop-filter: blur(10px);}
        .control-panel::before { content: ""; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #dc2626; }
        label { color: var(--text-main); font-weight: 500; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
        .form-control, .form-select { background-color: #1e293b !important; border: 1px solid #475569 !important; color: #fff !important; border-radius: 8px; padding: 10px 15px; }
        .form-control:focus, .form-select:focus { border-color: #dc2626 !important; box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2) !important; }
        .nav-tabs { border-bottom: 1px solid #334155; margin-bottom: 25px; }
        .nav-tabs .nav-link { color: var(--text-muted); border: none; font-weight: 600; }
        .nav-tabs .nav-link.active { background-color: transparent; color: #dc2626; border-bottom: 2px solid #dc2626; }
        .btn-launch { background: linear-gradient(135deg, #dc2626, #991b1b); color: white; border: none; padding: 12px; font-weight: 600; border-radius: 8px; transition: 0.2s; letter-spacing: 1px;}
        .btn-launch:hover { box-shadow: 0 0 20px rgba(220,38,38,0.6); color: white;}
        .btn-kill { background: linear-gradient(135deg, #475569, #1e293b); color: white; border: none; padding: 12px; font-weight: 600; border-radius: 8px; }
        .btn-kill:hover { background: #0f172a; color: white;}
        .btn-logout { background: transparent; color: #cbd5e1; border: 1px solid #475569; padding: 8px 15px; border-radius: 8px; transition: 0.3s; font-size: 0.9rem; text-decoration: none; }
        .btn-logout:hover { background: rgba(220,38,38,0.15); border-color: #dc2626; color: #dc2626;}
        .terminal-container { margin-top: 30px; background-color: var(--terminal-bg); border: 1px solid var(--border-color); border-radius: 8px; }
        .terminal-header { background-color: #1f2937; padding: 8px 15px; border-radius: 8px 8px 0 0; font-size: 0.85rem; color: var(--text-muted); display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #374151; }
        .terminal-body { height: 350px; overflow-y: auto; padding: 15px; font-family: 'Consolas', monospace; font-size: 0.9rem; color: var(--terminal-text); line-height: 1.5; scroll-behavior: smooth; }
        .terminal-body .time { color: #6b7280; margin-right: 8px; }
        .terminal-input-wrapper { display: flex; border-top: 1px solid #374151; }
        .terminal-prompt { padding: 10px 15px; background: #030712; color: #10b981; font-family: monospace; border-radius: 0 0 0 8px;}
        .terminal-input { flex-grow: 1; background: #030712; border: none; color: #fff; font-family: monospace; padding: 10px 0; outline: none; border-radius: 0 0 8px 0;}
        .stat-card { background: rgba(30, 41, 59, 0.8); border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #334155; transition: 0.3s; backdrop-filter: blur(5px);}
        .stat-card h4 { margin: 0; font-size: 1.5rem; color: #fff; }
        .stat-card span { font-size: 0.8rem; color: var(--text-muted); }
        
        .blink-alert { animation: pulseRed 1s infinite; }
        @keyframes pulseRed { 0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); } 70% { box-shadow: 0 0 20px 10px rgba(239, 68, 68, 0); } 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); } }
        .blink-text { animation: textBlink 1s infinite; }
        @keyframes textBlink { 0%, 100% { opacity: 1; color: #ef4444; } 50% { opacity: 0; } }
    </style>
</head>
<body>
<div class="container">
    <div class="header-title">
        <div>
            ROBLOX AUTONOMOUS
            <span class="badge border ms-3 {% if not license_valid %}border-danger text-danger blink-text{% else %}border-warning text-warning{% endif %}" style="background: rgba(0,0,0, 0.4); font-size: 0.8rem; letter-spacing: 1px;">
                <i class="fa-solid fa-key me-1"></i> LICENSE: {{ license_info }}
            </span>
        </div>
        <a href="/logout" class="btn-logout"><i class="fa-solid fa-power-off me-2"></i>Logout</a>
    </div>
    
    {% if not license_valid %}
    <div class="blink-alert" style="background-color: rgba(220, 38, 38, 0.1); border: 2px solid #ef4444; border-radius: 8px; padding: 25px; text-align: center; margin-bottom: 25px; backdrop-filter: blur(5px);">
        <h2 style="color: #ef4444; margin: 0; font-weight: bold;"><i class="fa-solid fa-triangle-exclamation me-2"></i> LICENSE EXPIRED </h2>
        <p style="color: #fca5a5; margin-top: 10px; font-size: 1.1rem; margin-bottom: 0;">Your connection to the Autonomous System has been restricted. Please contact support for renewal.</p>
    </div>
    <style> .control-panel { pointer-events: none; opacity: 0.3; filter: grayscale(100%); } </style>
    {% endif %}

    <div class="row justify-content-center">
        <div class="col-lg-10 mb-4">
            <div class="row g-3">
                <div class="col-md-4"><div class="stat-card" style="border-bottom: 3px solid #64748b;"><h4 id="statTotal">0</h4><span>TOTAL</span></div></div>
                <div class="col-md-4"><div class="stat-card" style="border-bottom: 3px solid #10b981;"><h4 id="statSuccess">0</h4><span>SUCCESS</span></div></div>
                <div class="col-md-4"><div class="stat-card" style="border-bottom: 3px solid #dc2626;"><h4 id="statFail">0</h4><span>FAILED</span></div></div>
            </div>
        </div>

        <div class="col-lg-10">
            <div class="control-panel">
                <form id="botForm">
                    <ul class="nav nav-tabs" id="botTabs">
                        <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#general" type="button"><i class="fa-solid fa-crosshairs me-2"></i>General</button></li>
                        <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tasks" type="button"><i class="fa-solid fa-bolt me-2"></i>Actions</button></li>
                        <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#advanced" type="button"><i class="fa-solid fa-shield-halved me-2"></i>Proxy & Security</button></li>
                    </ul>

                    <div class="tab-content">
                        <div class="tab-pane fade show active" id="general">
                            <div class="mb-4">
                                <label><i class="fa-solid fa-microchip"></i> Operation Mode</label>
                                <select class="form-select" name="mode" id="modeSelect">
                                    <option value="create">⚡ CREATE FROM SCRATCH: Open New Units and Proceed</option>
                                    <option value="login">🔐 EXISTING ACCOUNTS: Enter accounts.txt and Process</option>
                                </select>
                            </div>
                            
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label>Target Account Count (To Create or Login)</label>
                                    <input type="number" class="form-control" name="execution_count" value="1" min="1">
                                </div>
                                <div class="col-md-6" id="randomizeBox" style="display:none;">
                                    <div class="form-check mt-4">
                                        <input class="form-check-input" type="checkbox" name="random_accounts">
                                        <label class="form-check-label text-white">Randomize List (Avoid sequential logins)</label>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="row" id="creationSettings">
                                <div class="col-md-6 mb-3">
                                    <label>Name Prefix (Optional)</label>
                                    <input type="text" class="form-control" name="name_prefix" placeholder="e.g.: comrade">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <div class="form-check mt-3">
                                        <input class="form-check-input" type="checkbox" name="verify_email" checked>
                                        <label class="form-check-label text-white">Email Verification</label>
                                    </div>
                                    <div class="form-check mt-2">
                                        <input class="form-check-input" type="checkbox" name="customize_avatar" checked>
                                        <label class="form-check-label text-white">Avatar Customization</label>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="tab-pane fade" id="tasks">
                            <div class="mb-3"><label>Group Link</label><input type="url" class="form-control" name="group_link" placeholder="Group URL"></div>
                            <div class="mb-3"><label>Game Link (Like)</label><input type="url" class="form-control" name="game_link" placeholder="Game URL"></div>
                            <div class="mb-3"><label>Follow Users</label><input type="text" class="form-control" name="follow_users" placeholder="User1, User2"></div>
                            <div class="mb-3"><label>Discord Webhook</label><input type="url" class="form-control" name="discord_webhook" value="https://discord.com/api/webhooks/1482405364111642675/JW0Vf8WeGtWbT5mGjOh8_WYVjdi7wi3_74lbp33geATbBt0EUHJlH2axSzna0qg-2R73" placeholder="e.g.: https://discord.com/api/webhooks/..."></div>
                        </div>

                        <div class="tab-pane fade" id="advanced">
                            <div class="mb-3">
                                <label>Browser Executable Path</label>
                                <input type="text" class="form-control" name="browser_path" placeholder="Leave blank for auto-detect">
                            </div>
                            <div class="mb-3"><label>NopeCHA Key</label><input type="text" class="form-control" name="captcha_bypass" placeholder="Captcha solver key"></div>
                            
                            <div class="control-panel mb-3" style="background: rgba(16, 185, 129, 0.1); border-color: #10b981; padding: 15px;">
                                <div class="form-check form-switch" style="display: flex; align-items: center; gap: 10px;">
                                    <input class="form-check-input" type="checkbox" name="use_decodo" id="useDecodoCheck" style="transform: scale(1.3); margin-top: 0;">
                                    <label class="form-check-label text-white fw-bold" for="useDecodoCheck" style="margin-bottom: 0;">
                                        <i class="fa-solid fa-satellite-dish text-success me-2"></i> Decodo Autonomous Logistics Network (Recommended)
                                    </label>
                                </div>
                            </div>

                            <div class="mb-3" id="manualProxyContainer" style="transition: 0.3s;"><label>Manual Proxy (If Decodo is Off)</label><textarea class="form-control" name="proxies" rows="2" placeholder="ip:port"></textarea></div>
                            <div class="form-check"><input class="form-check-input" type="checkbox" name="incognito" checked><label class="form-check-label text-white">Use Incognito Mode</label></div>
                        </div>
                    </div>

                    <div class="row mt-4">
                        <div class="col-md-8"><button type="submit" class="btn btn-launch w-100"><i class="fa-solid fa-jet-fighter-up me-2"></i>START</button></div>
                        <div class="col-md-4"><button type="button" id="killSwitchBtn" class="btn btn-kill w-100"><i class="fa-solid fa-hand me-2"></i>STOP</button></div>
                    </div>
                </form>
            </div>
            
            <div class="terminal-container shadow-lg">
                <div class="terminal-header"><span><i class="fa-solid fa-terminal me-2"></i>Console</span><span id="statusText" style="color:#10b981; font-weight:bold;">Ready</span></div>
                <div class="terminal-body" id="logTerminal"></div>
                <div class="terminal-input-wrapper">
                    <div class="terminal-prompt" id="termUserRoot">root@roblox:~#</div>
                    <input type="text" id="terminalCmdInput" class="terminal-input" placeholder="Type /help to see commands..." autocomplete="off">
                </div>
            </div>
        </div>
    </div>
    
    <div style="text-align: center; margin-top: 40px; margin-bottom: 20px; color: #475569; font-size: 0.85rem; font-family: 'Courier New', Courier, monospace; letter-spacing: 3px; font-weight: bold; text-shadow: 0 0 10px rgba(0,0,0,0.5);">
        MADE BY FROXY & SASORİİ
    </div>

</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
    document.getElementById('modeSelect').addEventListener('change', function() {
        document.getElementById('creationSettings').style.display = this.value === 'login' ? 'none' : 'flex';
        document.getElementById('randomizeBox').style.display = this.value === 'login' ? 'block' : 'none';
    });

    document.getElementById('useDecodoCheck').addEventListener('change', function() {
        const manualProxy = document.getElementById('manualProxyContainer');
        if (this.checked) {
            manualProxy.style.opacity = '0.4';
            manualProxy.style.pointerEvents = 'none';
        } else {
            manualProxy.style.opacity = '1';
            manualProxy.style.pointerEvents = 'auto';
        }
    });

    document.getElementById('botForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());
        data.incognito = formData.has('incognito');
        data.verify_email = formData.has('verify_email');
        data.customize_avatar = formData.has('customize_avatar');
        data.random_accounts = formData.has('random_accounts');
        data.use_decodo = formData.has('use_decodo');

        fetch('/start_bot', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    });

    document.getElementById('killSwitchBtn').addEventListener('click', function() {
        fetch('/kill', { method: 'POST' });
    });

    document.getElementById('terminalCmdInput').addEventListener('keypress', function(e) {
        if(e.key === 'Enter') {
            const cmd = this.value; this.value = '';
            fetch('/command', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ command: cmd }) });
        }
    });

    setInterval(() => {
        fetch('/logs')
            .then(res => {
                if(res.status === 401) window.location.href = '/login';
                return res.json();
            })
            .then(data => {
                document.getElementById('statusText').innerText = data.status;
                document.getElementById('statTotal').innerText = data.stats.total;
                document.getElementById('statSuccess').innerText = data.stats.success;
                document.getElementById('statFail').innerText = data.stats.error;
                if(data.user) document.getElementById('termUserRoot').innerText = data.user + "@roblox:~#";
                
                const terminal = document.getElementById('logTerminal');
                const isScrolledToBottom = terminal.scrollHeight - terminal.clientHeight <= terminal.scrollTop + 50;
                const newHtml = data.logs.join('<br>');
                if (terminal.innerHTML !== newHtml) {
                    terminal.innerHTML = newHtml;
                    if (isScrolledToBottom) terminal.scrollTop = terminal.scrollHeight;
                }
            }).catch(e => console.log("Log fetch error."));
    }, 1000);
</script>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in VALID_USERS and VALID_USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = "Authentication failed! Your IP address has been reported."
            error_ip = get_client_ip()
            try:
                data = {
                    "username": "Firewall",
                    "avatar_url": "https://cdn-icons-png.flaticon.com/512/6062/6062646.png",
                    "content": "🚨 **UNAUTHORIZED LOGIN ATTEMPT DETECTED!**",
                    "embeds": [{"title": "⚠️ ALERT", "color": 15158332, "fields": [{"name": "Attempted Username", "value": f"`{username}`", "inline": True}, {"name": "Attempted Password", "value": f"`{password}`", "inline": True}, {"name": "Attacker IP Address", "value": f"`{error_ip}`", "inline": False}]}]
                }
                requests.post(SECURITY_WEBHOOK, json=data)
            except: pass
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index(): 
    if EASTER_EGG_ACTIVE:
        today_str = datetime.now().strftime("%d.%m.%Y")
        return render_template_string(EASTER_EGG_TEMPLATE, today=today_str)
    
    return render_template_string(HTML_TEMPLATE, license_info=LICENSE_INFO, license_valid=LICENSE_VALID)

@app.route('/start_bot', methods=['POST'])
@api_login_required
def start_bot():
    global BOT_LOGS, STATS
    if not LICENSE_VALID:
        print("<span style='color:#ef4444'>[SECURITY] SYSTEM LOCKED. Operation rejected due to expired license!</span>")
        return jsonify({"message": "License Expired or Invalid"}), 403

    BOT_LOGS.clear()
    print(f"[SECURITY] Operation initiated by user '{session.get('username')}'.")
    STATS = {"success": 0, "error": 0, "total": 0}
    config = request.json
    threading.Thread(target=lambda: asyncio.run(bot_runner(config)), daemon=True).start()
    return jsonify({"message": "Triggered"})

@app.route('/kill', methods=['POST'])
@api_login_required
def kill_bot():
    global STOP_FLAG
    STOP_FLAG = True
    print(f"[SYSTEM] WARNING! User '{session.get('username')}' activated the Kill Switch (Emergency Stop).")
    return jsonify({"message": "Stopped"})

@app.route('/command', methods=['POST'])
@api_login_required
def handle_command():
    raw_cmd = request.json.get("command", "").strip()
    active_user = session.get('username', 'root')
    if not raw_cmd: return jsonify({})
    safe_cmd = html.escape(raw_cmd)
    print(f"<span style='color:#0ea5e9'>{active_user}@roblox:~# {safe_cmd}</span>")
    if raw_cmd == "/clear" or raw_cmd == "clear": BOT_LOGS.clear()
    elif raw_cmd == "/stop": 
        global STOP_FLAG
        STOP_FLAG = True
        print("<span style='color:#10b981'>[SUCCESS] System is shutting down.</span>")
    elif raw_cmd == "/help" or raw_cmd == "yardim": print("<span style='color:#f3f4f6'>--- ROBLOX TERMINAL COMMANDS ---</span><br>/clear : Clears the screen.<br>/stop  : Stops the operation.<br>/read acc : Reads accounts.txt file.<br>/clear acc : Resets accounts.txt.<br>/list acc : Shows total account count")
    elif raw_cmd == "/read acc":
        try:
            with open(ACC_FILE, "r") as f: print("<br>--- ACCOUNTS.TXT ---<br>" + f.read().replace('\n', '<br>') + "<br>-------------------")
        except FileNotFoundError: print(f"<span style='color:#ef4444'>[ERROR] accounts.txt not found!</span>")
    elif raw_cmd == "/clear acc":
        with open(ACC_FILE, "w") as f: f.write("")
        print("<span style='color:#10b981'>[SUCCESS] accounts.txt has been reset!</span>")
    elif raw_cmd == "/list acc":
        try:
            with open(ACC_FILE, "r") as f:
                account_count = sum(1 for line in f if "Username:" in line)
                print(f"<span style='color:#facc15'>[INVENTORY] Total accounts: {account_count}</span>")
        except FileNotFoundError: print(f"<span style='color:#ef4444'>[ERROR] File not found!</span>")
    else: print(f"<span style='color:#facc15'>[WARNING] Unknown command: '{safe_cmd}'.</span>")
    return jsonify({"status": "ok"})

@app.route('/logs', methods=['GET'])
@api_login_required
def get_logs(): 
    return jsonify({"status": BOT_STATUS, "logs": list(BOT_LOGS), "stats": STATS, "user": session.get('username')})

def security_watchdog():
    while True:
        security_check()
        gc.collect()
        threading.Event().wait(2)

if __name__ == "__main__":
    threading.Thread(target=security_watchdog, daemon=True).start()
    
    try:
        threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
        
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        gc.collect()
