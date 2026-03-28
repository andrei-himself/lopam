# clipboard.py
import subprocess, time, threading

def wl_copy(text: str):
    subprocess.run(["wl-copy"], input=text.encode(), check=True)

def wl_clear():
    # overwrite then clear
    subprocess.run(["wl-copy"], input=b"cleared", check=True)
    time.sleep(0.1)
    subprocess.run(["wl-copy", "--clear"], check=True)

def copy_with_timeout(text: str, seconds: int = 30):
    wl_copy(text)
    def _clear():
        time.sleep(seconds)
        wl_clear()
    threading.Thread(target=_clear, daemon=True).start()