#!/usr/bin/env python3
"""
Script para extraer y guardar imágenes del transcript de Claude Code.
Las imágenes se guardan en .claude/logs_system/images/ con timestamp y se mantiene
un registro en .claude/logs_system/data/.images_index.json para referencia.
"""
import json
import sys
import os
import io
import base64
from datetime import datetime

def get_log_dir():
    """Determina el directorio de logs"""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return os.path.join(os.environ["CLAUDE_PROJECT_DIR"], ".claude", "logs_system", "logs")
    else:
        # Este script está en .claude/logs_system/hooks/, necesitamos .claude/logs_system/logs/
        logs_system_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(logs_system_dir, "logs")

def get_images_dir():
    """Directorio donde se guardan las imágenes"""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        logs_system_dir = os.path.join(os.environ["CLAUDE_PROJECT_DIR"], ".claude", "logs_system")
    else:
        logs_system_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(logs_system_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    return images_dir

def get_images_index_file():
    """Archivo de índice de imágenes"""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        data_dir = os.path.join(os.environ["CLAUDE_PROJECT_DIR"], ".claude", "logs_system", "data")
    else:
        logs_system_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(logs_system_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, ".images_index.json")

def load_images_index():
    """Carga el índice de imágenes guardadas"""
    index_file = get_images_index_file()
    if os.path.exists(index_file):
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"images": []}
    return {"images": []}

def save_images_index(index_data):
    """Guarda el índice de imágenes"""
    index_file = get_images_index_file()
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

def extract_images_from_transcript(transcript_path):
    """
    Extrae imágenes del transcript y las guarda.
    Retorna lista de rutas de imágenes guardadas.
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return []

    images_dir = get_images_dir()
    index_data = load_images_index()
    saved_images = []

    try:
        # Leer todos los mensajes del transcript
        messages = []
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))

        # Procesar cada mensaje buscando imágenes
        for msg in messages:
            message_obj = msg.get("message", {})
            content = message_obj.get("content", [])
            role = message_obj.get("role", "")
            timestamp = msg.get("timestamp", datetime.now().isoformat())

            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "image":
                        source = item.get("source", {})

                        if source.get("type") == "base64":
                            media_type = source.get("media_type", "image/png")
                            ext = media_type.split("/")[-1]
                            image_data = source.get("data", "")

                            if image_data:
                                # Generar nombre único para la imagen
                                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                                filename = f"screenshot_{timestamp_str}.{ext}"
                                filepath = os.path.join(images_dir, filename)

                                # Decodificar y guardar imagen
                                try:
                                    with open(filepath, "wb") as img_file:
                                        img_file.write(base64.b64decode(image_data))

                                    # Agregar al índice
                                    image_info = {
                                        "filename": filename,
                                        "path": filepath,
                                        "relative_path": f".claude/logs_system/images/{filename}",
                                        "timestamp": timestamp,
                                        "role": role,
                                        "media_type": media_type,
                                        "size_bytes": os.path.getsize(filepath)
                                    }

                                    # Evitar duplicados (comparar por timestamp reciente)
                                    is_duplicate = False
                                    for existing in index_data["images"]:
                                        if abs(datetime.fromisoformat(existing["timestamp"]).timestamp() -
                                               datetime.fromisoformat(timestamp).timestamp()) < 1:
                                            is_duplicate = True
                                            break

                                    if not is_duplicate:
                                        index_data["images"].append(image_info)
                                        saved_images.append(image_info)

                                except Exception as e:
                                    print(f"Error saving image: {e}", file=sys.stderr)

        # Guardar índice actualizado
        if saved_images:
            save_images_index(index_data)

        return saved_images

    except Exception as e:
        print(f"Error extracting images: {e}", file=sys.stderr)
        return []

try:
    # Reconfigurar stdin para usar UTF-8
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    # Leer datos del hook
    input_data = json.load(sys.stdin)
    hook_type = input_data.get("hook_event_name", "")

    # Solo procesar en el hook Stop (cuando termina la respuesta)
    if hook_type == "Stop":
        transcript_path = input_data.get("transcript_path", "")

        if transcript_path:
            saved_images = extract_images_from_transcript(transcript_path)

            # Debug: registrar imágenes guardadas
            if saved_images:
                log_dir = get_log_dir()
                os.makedirs(log_dir, exist_ok=True)
                debug_file = os.path.join(log_dir, "debug-images.log")
                with open(debug_file, "a", encoding="utf-8") as df:
                    df.write(f"\n[{datetime.now().isoformat()}]\n")
                    df.write(f"Saved {len(saved_images)} image(s):\n")
                    for img in saved_images:
                        df.write(f"  - {img['relative_path']} ({img['size_bytes']} bytes)\n")

    sys.exit(0)

except Exception as e:
    print(f"Error in save-images: {e}", file=sys.stderr)
    sys.exit(0)  # No bloquear aunque haya error
