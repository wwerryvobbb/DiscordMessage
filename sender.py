import sys
import subprocess
import importlib
import os
import time
import threading

# ─────────────────────────────────────────────
#  AUTO-INSTALLER
# ─────────────────────────────────────────────

REQUIRED = {
    "requests": "requests",
    "colorama": "colorama",
}

def install_missing():
    for import_name, pip_name in REQUIRED.items():
        try:
            importlib.import_module(import_name)
            print(f"  [\033[92m✓\033[0m] {pip_name} already installed")
        except ImportError:
            print(f"  [\033[93m↓\033[0m] Installing {pip_name}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pip_name, "--quiet"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"  [\033[92m✓\033[0m] {pip_name} installed")

# ─────────────────────────────────────────────
#  BANNER
# ─────────────────────────────────────────────

def banner():
    print("\033[35m")
    print("  ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗  ██████╗ ████████╗")
    print("  ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔═══██╗╚══██╔══╝")
    print("  ██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║   ██║   ██║   ")
    print("  ██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║   ██║   ██║   ")
    print("  ██████╔╝██║███████║╚██████╗╚██████╔╝██████╔╝╚██████╔╝   ██║   ")
    print("  ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝  ╚═════╝   ╚═╝   ")
    print("\033[0m")
    print("  \033[90mDiscord Message Sender — Actions & Selfbot Edition\033[0m")
    print("  \033[90m─────────────────────────────────────────────────\033[0m\n")

# ─────────────────────────────────────────────
#  FETCH GUILD CHANNELS
#  Returns list of text channel IDs in guild
# ─────────────────────────────────────────────

def fetch_guild_channels(guild_id, headers):
    import requests
    url = f"https://discord.com/api/v9/guilds/{guild_id}/channels"
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code == 200:
        channels = resp.json()
        # type 0 = GUILD_TEXT, type 5 = GUILD_ANNOUNCEMENT
        text_channels = [str(ch["id"]) for ch in channels if ch.get("type") in (0, 5)]
        return text_channels
    elif resp.status_code == 401:
        print("  \033[91m[!!] 401 Unauthorized — bad token.\033[0m")
        sys.exit(1)
    elif resp.status_code == 403:
        print("  \033[91m[!!] 403 Forbidden — no access to guild.\033[0m")
        sys.exit(1)
    else:
        print(f"  \033[91m[!] Failed to fetch guild channels: HTTP {resp.status_code}\033[0m")
        sys.exit(1)

# ─────────────────────────────────────────────
#  CHANNEL SENDER THREAD
#  Each thread loops one channel independently
# ─────────────────────────────────────────────

def channel_sender(channel_id, message, headers, delay, max_duration, start_time, label):
    import requests
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    sent = 0
    while True:
        elapsed = time.time() - start_time
        if elapsed >= max_duration:
            print(f"  \033[93m[{label}] Runtime cutoff reached. Thread exiting.\033[0m")
            break

        try:
            resp = requests.post(url, json={"content": message}, headers=headers, timeout=15)
            if resp.status_code == 200:
                sent += 1
                preview = message.replace('\n', ' ')[:40]
                print(f"  \033[92m[{label}][{sent}]\033[0m {preview}...")
            elif resp.status_code == 429:
                retry_after = resp.json().get("retry_after", 5)
                print(f"  \033[93m[{label}] Rate limited — sleeping {retry_after}s\033[0m")
                time.sleep(float(retry_after))
                continue
            elif resp.status_code == 401:
                print(f"  \033[91m[{label}] 401 — bad token. Thread stopping.\033[0m")
                break
            elif resp.status_code == 403:
                # No permission in this channel — skip silently
                print(f"  \033[90m[{label}] 403 — no permission, skipping channel.\033[0m")
                break
            else:
                print(f"  \033[91m[{label}] HTTP {resp.status_code}\033[0m")
        except Exception as e:
            print(f"  \033[91m[{label}] Error: {e}\033[0m")

        time.sleep(delay)

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    import requests

    # 1. TOKEN
    TOKEN = os.getenv("USER_TOKEN", "").strip()
    if not TOKEN:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            TOKEN = os.getenv("USER_TOKEN", "").strip()
        except ImportError:
            pass

    if not TOKEN or TOKEN == "paste_your_token_here":
        print("\n  \033[91m[!] No USER_TOKEN found.\033[0m\n")
        sys.exit(1)

    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    }

    # 2. MESSAGE
    msg_file = os.path.join(os.path.dirname(__file__), "message.txt")
    if not os.path.exists(msg_file):
        print("\n  \033[91m[!] message.txt not found.\033[0m\n")
        sys.exit(1)
    with open(msg_file, "r", encoding="utf-8") as f:
        message = f.read().strip()
    if not message:
        print("\n  \033[91m[!] message.txt is empty.\033[0m\n")
        sys.exit(1)
    print("  \033[90m[i] message.txt loaded\033[0m\n")

    # 3. CHANNEL_ID SECRET — parse C= or G= prefix
    raw_target = os.getenv("CHANNEL_ID", "").strip()
    if not raw_target:
        raw_target = input("  \033[96mTarget\033[0m (C=<channel_id>  or  G=<guild_id>): ").strip()

    if raw_target.upper().startswith("G="):
        guild_id = raw_target[2:].strip()
        print(f"  \033[90m[i] Guild mode — fetching all text channels in guild {guild_id}...\033[0m")
        channel_ids = fetch_guild_channels(guild_id, headers)
        print(f"  \033[92m[✓] Found {len(channel_ids)} text channels. Spamming all simultaneously.\033[0m\n")
    elif raw_target.upper().startswith("C="):
        channel_id = raw_target[2:].strip()
        channel_ids = [channel_id]
        print(f"  \033[92m[✓] Single channel mode — target: {channel_id}\033[0m\n")
    else:
        print("  \033[91m[!] Invalid format. Use C=<id> for a channel or G=<id> for a guild.\033[0m")
        sys.exit(1)

    if not channel_ids:
        print("  \033[91m[!] No valid channels found.\033[0m")
        sys.exit(1)

    # 4. MESSAGES PER SECOND
    mps_env = os.getenv("MESSAGES_PER_SECOND", "").strip()
    if mps_env:
        try:
            mps = float(mps_env)
        except ValueError:
            mps = 0.2
    else:
        print("  \033[90mMessages per second:\033[0m")
        print("  \033[92m  0.2\033[0m  → 1 msg every 5s (recommended)")
        print("  \033[93m  0.5\033[0m  → 1 msg every 2s (medium)")
        print("  \033[91m  1  \033[0m  → 1 msg every 1s (high risk)")
        print("  \033[91m  2+ \033[0m  → sub-0.5s (nuke tier)")
        print()
        mps_input = input("  \033[96mMessages per second\033[0m [default: 0.2]: ").strip()
        try:
            mps = float(mps_input) if mps_input else 0.2
            if mps <= 0:
                mps = 0.2
        except ValueError:
            mps = 0.2

    delay = 1.0 / mps
    print(f"  \033[92m[✓] {mps} msg/s per channel — {delay:.2f}s delay\033[0m")

    # 5. RUNTIME LIMIT
    max_duration_env = os.getenv("MAX_RUN_SECONDS", "").strip()
    max_duration = float(max_duration_env) if max_duration_env else (5.5 * 3600)
    start_time = time.time()
    print(f"  \033[90m[i] Runtime limit: {max_duration/3600:.1f} hours\033[0m\n")

    is_ci = os.getenv("CI") or os.getenv("GITHUB_ACTIONS")
    if not is_ci and not os.getenv("CHANNEL_ID"):
        input("  Press \033[92mENTER\033[0m to start... (Ctrl+C to stop)\n  ")

    # 6. LAUNCH THREADS — one per channel, all run simultaneously
    print(f"  \033[92m[✓] Launching {len(channel_ids)} sender thread(s)...\033[0m\n")
    threads = []
    for i, ch_id in enumerate(channel_ids):
        label = f"CH-{i+1}"
        t = threading.Thread(
            target=channel_sender,
            args=(ch_id, message, headers, delay, max_duration, start_time, label),
            daemon=True
        )
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n\n  \033[90m[✓] Stopped by user.\033[0m\n")

if __name__ == "__main__":
    banner()
    install_missing()
    main()
