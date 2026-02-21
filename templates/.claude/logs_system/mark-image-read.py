#!/usr/bin/env python3
"""
Marca una imagen como leida por Claude en el indice de imagenes.

Uso:
  python .claude/logs_system/mark-image-read.py --latest
      Marca la imagen no leida mas reciente.

  python .claude/logs_system/mark-image-read.py screenshot_20260220_101530_123456.png
      Marca una imagen especifica por nombre de archivo.
"""
import json
import sys
import os
from datetime import datetime


def get_images_index_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    return os.path.join(data_dir, ".images_index.json")


def load_index():
    index_file = get_images_index_file()
    if os.path.exists(index_file):
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"images": []}
    return {"images": []}


def save_index(data):
    index_file = get_images_index_file()
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def mark_read(filename=None, latest=False):
    index_data = load_index()
    images = index_data.get("images", [])

    if latest:
        unread = [img for img in images if not img.get("read_by_claude", False)]
        if not unread:
            print("No hay imagenes sin leer en el indice")
            return False
        unread.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        target = unread[0]["filename"]
    else:
        target = filename

    updated = False
    for img in images:
        if img["filename"] == target:
            img["read_by_claude"] = True
            img["read_timestamp"] = datetime.now().isoformat()
            updated = True
            print(f"Marcada como leida: {target}")
            break

    if updated:
        save_index(index_data)
        return True
    else:
        print(f"Imagen no encontrada en el indice: {target}")
        return False


def list_unread():
    index_data = load_index()
    images = index_data.get("images", [])
    unread = [img for img in images if not img.get("read_by_claude", False)]
    if not unread:
        print("No hay imagenes sin leer")
        return
    unread.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    for img in unread:
        source = img.get("source", "transcript")
        print(f"  [{img['timestamp']}] {img['filename']} ({source})")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    if args[0] == "--latest":
        success = mark_read(latest=True)
        sys.exit(0 if success else 1)

    if args[0] == "--list":
        list_unread()
        sys.exit(0)

    mark_read(filename=args[0])
