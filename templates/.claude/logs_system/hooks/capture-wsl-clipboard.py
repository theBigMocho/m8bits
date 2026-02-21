#!/usr/bin/env python3
"""
Hook para capturar imagenes del clipboard de Windows cuando Claude Code corre en WSL.

Se ejecuta en UserPromptSubmit. Solo actua si detecta entorno WSL.
En Windows las imagenes se capturan via save-images.py desde el transcript.

Si hay imagen en el clipboard al momento de enviar el prompt, la guarda en
.claude/logs_system/images/ y la registra en el indice con read_by_claude: false
para que Claude pueda leerla si el usuario hace referencia a ella.
"""
import json
import sys
import io
import os
import subprocess
from datetime import datetime


def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def get_logs_system_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_images_dir():
    images_dir = os.path.join(get_logs_system_dir(), "images")
    os.makedirs(images_dir, exist_ok=True)
    return images_dir


def get_images_index_file():
    data_dir = os.path.join(get_logs_system_dir(), "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, ".images_index.json")


def load_images_index():
    index_file = get_images_index_file()
    if os.path.exists(index_file):
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"images": []}
    return {"images": []}


def save_images_index(index_data):
    index_file = get_images_index_file()
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)


def linux_to_windows_path(linux_path):
    try:
        result = subprocess.run(
            ["wslpath", "-w", linux_path],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        # Fallback manual
        if linux_path.startswith("/mnt/c/"):
            return "C:\\" + linux_path[7:].replace("/", "\\")
        return None


def capture_clipboard_image():
    images_dir = get_images_dir()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"screenshot_{timestamp_str}.png"
    linux_path = os.path.join(images_dir, filename)
    win_path = linux_to_windows_path(linux_path)

    if not win_path:
        return None

    # Escapar backslashes para PowerShell
    win_path_ps = win_path.replace("\\", "\\\\")

    ps_command = f"""
Add-Type -AssemblyName System.Windows.Forms
$img = [System.Windows.Forms.Clipboard]::GetImage()
if ($img) {{
    $img.Save('{win_path_ps}')
    Write-Output 'OK'
}} else {{
    Write-Output 'NO_IMAGE'
}}
"""

    try:
        result = subprocess.run(
            ["powershell.exe", "-Command", ps_command],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip().replace("\r", "").replace("\n", "")

        if output == "OK" and os.path.exists(linux_path):
            return {
                "filename": filename,
                "path": linux_path,
                "relative_path": f".claude/logs_system/images/{filename}",
                "timestamp": datetime.now().isoformat(),
                "role": "user",
                "media_type": "image/png",
                "size_bytes": os.path.getsize(linux_path),
                "source": "wsl_clipboard",
                "read_by_claude": False,
                "read_timestamp": None
            }
    except Exception as e:
        print(f"Error capturing WSL clipboard: {e}", file=sys.stderr)

    return None


def is_recent_duplicate(index_data, seconds=3):
    now = datetime.now()
    for existing in index_data.get("images", []):
        try:
            existing_ts = datetime.fromisoformat(existing["timestamp"])
            if abs((now - existing_ts).total_seconds()) < seconds:
                return True
        except Exception:
            pass
    return False


try:
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
    input_data = json.load(sys.stdin)
    hook_type = input_data.get("hook_event_name", "")

    if hook_type == "UserPromptSubmit" and is_wsl():
        image_info = capture_clipboard_image()

        if image_info:
            index_data = load_images_index()

            if not is_recent_duplicate(index_data):
                index_data["images"].append(image_info)
                save_images_index(index_data)

    sys.exit(0)

except Exception as e:
    print(f"Error in capture-wsl-clipboard: {e}", file=sys.stderr)
    sys.exit(0)
