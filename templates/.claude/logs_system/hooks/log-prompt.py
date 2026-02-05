#!/usr/bin/env python3
import json
import sys
import os
import io
from datetime import datetime

try:
    # Reconfigurar stdin para usar UTF-8 (importante en Windows)
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    # Leer los datos del hook desde stdin
    input_data = json.load(sys.stdin)

    # Obtener el prompt del usuario
    prompt = input_data.get("prompt", "")
    session_id = input_data.get("session_id", "unknown")

    # Determinar la ruta del archivo de log
    if "CLAUDE_PROJECT_DIR" in os.environ:
        log_dir = os.path.join(os.environ["CLAUDE_PROJECT_DIR"], ".claude", "logs_system", "logs")
    else:
        # Este script está en .claude/logs_system/hooks/, necesitamos .claude/logs_system/logs/
        logs_system_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(logs_system_dir, "logs")

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "prompt-history.log")

    # Formatear el timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Crear la entrada del log
    log_entry = f"[{timestamp}] [Session: {session_id}]\n{prompt}\n{'-' * 80}\n\n"

    # Agregar al archivo de log
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

    # Salir exitosamente (código 0)
    sys.exit(0)

except Exception as e:
    # En caso de error, escribir a stderr pero no bloquear
    print(f"Error al registrar prompt: {e}", file=sys.stderr)
    sys.exit(0)  # No bloquear aunque haya error
