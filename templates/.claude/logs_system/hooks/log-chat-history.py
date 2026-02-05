#!/usr/bin/env python3
import json
import sys
import os
import io
from datetime import datetime

def get_log_dir():
    """Determina el directorio de logs"""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return os.path.join(os.environ["CLAUDE_PROJECT_DIR"], ".claude", "logs_system", "logs")
    else:
        # Este script está en .claude/logs_system/hooks/, necesitamos .claude/logs_system/logs/
        logs_system_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(logs_system_dir, "logs")

def get_temp_file():
    """Ruta del archivo temporal para acumular datos"""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        data_dir = os.path.join(os.environ["CLAUDE_PROJECT_DIR"], ".claude", "logs_system", "data")
    else:
        logs_system_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(logs_system_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, ".chat_temp.json")

def get_log_file():
    """Ruta del archivo de log final"""
    os.makedirs(get_log_dir(), exist_ok=True)
    return os.path.join(get_log_dir(), "prompt-chat-history.log")

def get_images_index_file():
    """Ruta del archivo de índice de imágenes"""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        data_dir = os.path.join(os.environ["CLAUDE_PROJECT_DIR"], ".claude", "logs_system", "data")
    else:
        logs_system_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(logs_system_dir, "data")
    return os.path.join(data_dir, ".images_index.json")

def get_recent_images(timestamp_str, window_seconds=5):
    """
    Obtiene imágenes guardadas recientemente (dentro de una ventana de tiempo).
    timestamp_str: ISO format timestamp
    window_seconds: ventana de tiempo en segundos para considerar imágenes como relacionadas
    """
    index_file = get_images_index_file()
    if not os.path.exists(index_file):
        return []

    try:
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = json.load(f)

        # Convertir timestamp de referencia
        ref_time = datetime.fromisoformat(timestamp_str)
        recent_images = []

        for img in index_data.get("images", []):
            img_time = datetime.fromisoformat(img["timestamp"])
            time_diff = abs((img_time - ref_time).total_seconds())

            if time_diff <= window_seconds:
                recent_images.append(img)

        return recent_images
    except Exception as e:
        return []

try:
    # Reconfigurar stdin para usar UTF-8 (importante en Windows)
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    # Leer los datos del hook desde stdin
    input_data = json.load(sys.stdin)
    hook_type = input_data.get("hook_event_name", "")

    if hook_type == "UserPromptSubmit":
        # INICIO: Guardar el prompt del usuario en archivo temporal
        temp_file = get_temp_file()
        prompt = input_data.get("prompt", "")
        session_id = input_data.get("session_id", "unknown")
        timestamp = datetime.now().isoformat()

        # Antes de guardar el nuevo prompt, verificar si hay datos previos que guardar
        if os.path.exists(temp_file):
            try:
                with open(temp_file, "r", encoding="utf-8") as f:
                    prev_data = json.load(f)

                # Si hay datos previos completos, guardarlos en el log
                if prev_data.get("prompt") and prev_data.get("completed"):
                    log_file = get_log_file()
                    log_timestamp = datetime.fromisoformat(prev_data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

                    # Buscar imágenes relacionadas con este mensaje
                    images = get_recent_images(prev_data["timestamp"], window_seconds=10)
                    images_section = ""
                    if images:
                        images_section = "\nIMAGES ATTACHED:\n"
                        for img in images:
                            images_section += f"  - {img['relative_path']} ({img['size_bytes']} bytes, {img['media_type']})\n"
                        images_section += "\n"

                    log_entry = f"""{'=' * 80}
[{log_timestamp}] [Session: {prev_data.get('session_id', 'unknown')}]
{'=' * 80}

USER:
{prev_data.get('prompt', '')}{images_section}
{'-' * 80}

ASSISTANT:
{prev_data.get('response_summary', '(Respuesta completada)')}

{'=' * 80}

"""
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(log_entry)
            except:
                pass  # Si hay error leyendo datos previos, continuar

        # Guardar nuevo prompt
        temp_data = {
            "prompt": prompt,
            "session_id": session_id,
            "timestamp": timestamp,
            "tool_count": 0,
            "completed": False
        }

        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(temp_data, f, ensure_ascii=False, indent=2)

    elif hook_type == "PostToolUse":
        # Contar herramientas usadas para saber cuándo termino
        temp_file = get_temp_file()

        if os.path.exists(temp_file):
            with open(temp_file, "r", encoding="utf-8") as f:
                temp_data = json.load(f)

            # Incrementar contador de herramientas
            temp_data["tool_count"] = temp_data.get("tool_count", 0) + 1
            temp_data["last_tool_time"] = datetime.now().isoformat()

            # Guardar herramientas relevantes para construir un resumen
            tool_name = input_data.get("tool_name", "")
            if "tools_used" not in temp_data:
                temp_data["tools_used"] = []
            temp_data["tools_used"].append(tool_name)

            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(temp_data, f, ensure_ascii=False, indent=2)

    elif hook_type == "Stop":
        # FINAL: Guardar el intercambio completo cuando el asistente termina de responder
        temp_file = get_temp_file()

        if os.path.exists(temp_file):
            with open(temp_file, "r", encoding="utf-8") as f:
                temp_data = json.load(f)

            # Leer el transcript para obtener la respuesta completa del asistente
            transcript_path = input_data.get("transcript_path", "")
            assistant_response = "(Respuesta no disponible)"

            # Debug: escribir info del transcript
            debug_file = os.path.join(get_log_dir(), "debug-transcript.log")
            with open(debug_file, "a", encoding="utf-8") as df:
                df.write(f"\n[{datetime.now().isoformat()}]\n")
                df.write(f"transcript_path: {transcript_path}\n")
                df.write(f"exists: {os.path.exists(transcript_path) if transcript_path else 'N/A'}\n")

            if transcript_path and os.path.exists(transcript_path):
                try:
                    # Leer el archivo JSONL (cada línea es un mensaje JSON)
                    messages = []
                    with open(transcript_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                messages.append(json.loads(line))

                    # Buscar la última respuesta del asistente
                    for msg in reversed(messages):
                        # La estructura es msg["message"]["role"] y msg["message"]["content"]
                        message_obj = msg.get("message", {})
                        if message_obj.get("role") == "assistant":
                            # Extraer el contenido de texto de la respuesta
                            content = message_obj.get("content", [])
                            text_parts = []

                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get("type") == "text":
                                        text_parts.append(item.get("text", ""))
                                    elif isinstance(item, str):
                                        text_parts.append(item)
                            elif isinstance(content, str):
                                text_parts.append(content)

                            assistant_response = "\n".join(text_parts).strip()
                            if assistant_response:
                                break
                except Exception as e:
                    assistant_response = f"(Error al leer transcript: {e})"

            temp_data["completed"] = True
            temp_data["response_summary"] = assistant_response

            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(temp_data, f, ensure_ascii=False, indent=2)

    # Salir exitosamente
    sys.exit(0)

except Exception as e:
    # En caso de error, escribir a stderr pero no bloquear
    print(f"Error en log-chat-history: {e}", file=sys.stderr)
    sys.exit(0)  # No bloquear aunque haya error
