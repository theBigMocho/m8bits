# Sistema de Logging de Claude Code

## Descripción General

Este sistema implementa un mecanismo automático de logging para registrar todas las interacciones con Claude Code CLI, incluyendo:
- Prompts enviados por el usuario
- Respuestas completas del asistente
- Imágenes adjuntadas durante las conversaciones
- Uso de herramientas (tools)

**Nota sobre la estructura**: Este sistema está organizado en su propia carpeta `.claude/logs_system/` dentro del directorio `.claude/`. La configuración de hooks permanece en `.claude/settings.local.json`, y todos los scripts, logs, imágenes y datos están contenidos en `.claude/logs_system/`. Esto mantiene el sistema de logging modular e independiente de los comandos/skills de Claude.

## Arquitectura del Sistema

### 1. Configuración de Hooks (`settings.local.json`)

El sistema se basa en hooks que se ejecutan en diferentes momentos del ciclo de vida de una conversación:

#### **UserPromptSubmit** - Cuando el usuario envía un mensaje
```json
{
  "type": "command",
  "command": "python .claude/logs_system/hooks/log-prompt.py"
}
{
  "type": "command",
  "command": "python .claude/logs_system/hooks/log-chat-history.py"
}
```
- Captura el prompt del usuario
- Inicia el tracking de una nueva interacción

#### **PostToolUse** - Después de cada uso de herramienta
```json
{
  "type": "command",
  "command": "python .claude/logs_system/hooks/log-chat-history.py"
}
```
- Registra qué herramientas está usando Claude
- Cuenta el número de operaciones realizadas

#### **Stop** - Cuando el asistente termina de responder
```json
{
  "type": "command",
  "command": "python .claude/logs_system/hooks/save-images.py"
}
{
  "type": "command",
  "command": "python .claude/logs_system/hooks/log-chat-history.py"
}
```
- Extrae y guarda imágenes del transcript
- Guarda la conversación completa (usuario + asistente)

---

## Componentes del Sistema

### Script 1: `log-prompt.py`
**Propósito**: Registro simple de prompts del usuario

**Funcionamiento**:
1. Lee el prompt desde stdin (formato JSON)
2. Obtiene session_id y timestamp
3. Guarda en `.claude/logs_system/logs/prompt-history.log`

**Formato de salida**:
```
[2026-01-08 18:15:36] [Session: abc123]
¿Qué es este animalito?
--------------------------------------------------------------------------------
```

**Características**:
- Encoding UTF-8 para Windows
- Manejo de errores que no bloquea el CLI
- Determina automáticamente el directorio de logs

---

### Script 2: `log-chat-history.py`
**Propósito**: Registro completo de conversaciones con contexto

**Funcionamiento Complejo**:

#### Fase 1: UserPromptSubmit
1. Si existe conversación previa completa en `.chat_temp.json`, la guarda en el log
2. Busca imágenes relacionadas con la conversación anterior (ventana de 10 segundos)
3. Inicia nueva sesión temporal con:
   - prompt del usuario
   - session_id
   - timestamp
   - contador de herramientas en 0
   - estado: no completado

#### Fase 2: PostToolUse
1. Lee datos temporales
2. Incrementa contador de herramientas
3. Registra nombre de la herramienta usada
4. Actualiza timestamp de última herramienta

#### Fase 3: Stop
1. Lee el transcript JSONL completo
2. Extrae la última respuesta del asistente
3. Marca la conversación como completada
4. Guarda todo en el archivo temporal (listo para próximo UserPromptSubmit)

**Formato de salida** (`.claude/logs_system/logs/prompt-chat-history.log`):
```
================================================================================
[2026-01-08 18:15:36] [Session: abc123]
================================================================================

USER:
¿Qué es este animalito?

IMAGES ATTACHED:
  - .claude/logs_system/images/screenshot_20260108_181536_524241.png (11220 bytes, image/png)

--------------------------------------------------------------------------------

ASSISTANT:
Ese "animalito" es un cangrejo pixelado en estilo ASCII/pixel art...

================================================================================
```

**Archivos auxiliares**:
- `.claude/logs_system/data/.chat_temp.json`: Estado temporal de conversación activa
- `.claude/logs_system/data/.images_index.json`: Índice de imágenes para correlación temporal

**Funciones clave**:
- `get_recent_images()`: Busca imágenes guardadas en ventana de tiempo (±5 segundos)
- Correlación temporal entre imágenes y prompts

---

### Script 3: `save-images.py`
**Propósito**: Extracción y archivo de imágenes del transcript

**Funcionamiento**:
1. Se ejecuta en el hook `Stop`
2. Lee el transcript JSONL línea por línea
3. Busca bloques de contenido tipo `image` con source `base64`
4. Decodifica y guarda cada imagen como archivo PNG/JPG

**Proceso de guardado**:
```python
filename = f"screenshot_{timestamp}.{ext}"
filepath = .claude/logs_system/images/{filename}
```

**Índice de imágenes** (`.claude/logs_system/data/.images_index.json`):
```json
{
  "images": [
    {
      "filename": "screenshot_20260108_181536_524241.png",
      "path": "C:\\parse\\proyectos\\apps\\promet\\.claude\\images\\screenshot_...",
      "relative_path": ".claude/logs_system/images/screenshot_20260108_181536_524241.png",
      "timestamp": "2026-01-08T18:15:36.524241",
      "role": "user",
      "media_type": "image/png",
      "size_bytes": 11220
    }
  ]
}
```

**Prevención de duplicados**:
- Compara timestamps con diferencia menor a 1 segundo
- Evita guardar la misma imagen múltiples veces

---

## Estructura de Directorios

```
proyecto/
└── .claude/
    ├── settings.local.json       # Configuración de hooks y permisos
    ├── commands/                 # Skills/comandos personalizados
    │
    └── logs_system/              # Sistema de logging
        ├── hooks/                # Scripts de hooks
        │   ├── log-prompt.py         # Registro de prompts
        │   ├── log-chat-history.py   # Registro de conversaciones
        │   └── save-images.py        # Extracción de imágenes
        ├── logs/                 # Archivos de log
        │   ├── prompt-history.log    # Prompts simples
        │   ├── prompt-chat-history.log  # Conversaciones completas
        │   ├── debug-transcript.log  # Debug de transcripts
        │   └── debug-images.log      # Debug de imágenes guardadas
        ├── images/               # Imágenes extraídas
        │   └── screenshot_*.png      # Capturas guardadas
        ├── data/                 # Datos temporales
        │   ├── .chat_temp.json       # Estado temporal de sesión
        │   └── .images_index.json    # Índice de imágenes
        └── docs/                 # Documentación
            └── log_system.md         # Este archivo
```

---

## Flujo de Datos Completo

### Ejemplo de Interacción:

1. **Usuario envía mensaje con imagen**
   - Hook `UserPromptSubmit` dispara
   - `log-prompt.py`: Guarda en `prompt-history.log`
   - `log-chat-history.py`: Guarda datos previos completos + inicia nueva sesión temporal

2. **Claude usa herramientas** (ej: Read, Bash, Edit)
   - Hook `PostToolUse` dispara por cada herramienta
   - `log-chat-history.py`: Incrementa contador, registra herramienta

3. **Claude termina de responder**
   - Hook `Stop` dispara
   - `save-images.py`: Extrae imagen del transcript, la guarda en `.claude/logs_system/images/`
   - `log-chat-history.py`: Lee transcript, extrae respuesta del asistente, marca como completado

4. **Siguiente mensaje del usuario**
   - Hook `UserPromptSubmit` dispara
   - `log-chat-history.py`: Detecta sesión anterior completa, la escribe en `prompt-chat-history.log` con imágenes correlacionadas

---

## Características Avanzadas

### Manejo de UTF-8 en Windows
```python
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
```
Asegura compatibilidad con caracteres especiales en Windows.

### Correlación Temporal de Imágenes
- Las imágenes se guardan con timestamp ISO
- Al escribir logs, se buscan imágenes en ventana de ±10 segundos
- Permite asociar imágenes con el prompt correcto incluso si hay lag

### Modo No-Bloqueante
```python
sys.exit(0)  # Siempre retorna éxito
```
Si ocurre un error, se loggea en stderr pero no bloquea el funcionamiento de Claude.

### Prevención de Pérdida de Datos
- Usa archivo temporal `.chat_temp.json` como buffer
- Si Claude se interrumpe, los datos se recuperan en el siguiente prompt

---

## Archivos de Logs

### `prompt-history.log`
Registro simple de solo prompts del usuario (sin respuestas).

**Uso**: Revisión rápida de qué has consultado.

### `prompt-chat-history.log`
Registro completo de conversaciones (USER + ASSISTANT).

**Uso**: Análisis completo de interacciones, debugging, referencia histórica.

### `debug-transcript.log`
Información de debugging sobre rutas de transcripts y su existencia.

### `debug-images.log`
Registro de imágenes guardadas con tamaño y timestamp.

---

## Permisos Configurados

En `settings.local.json` también se definen permisos auto-aprobados:

```json
"permissions": {
  "allow": [
    "Bash(tree:*)",
    "Skill(commit-and-push)",
    "Bash(test:*)",
    "Bash(python:*)",
    "Bash(del:*)",
    "Bash(pytest:*)",
    "WebFetch(domain:sb-ep.sennapay.cl)",
    "Bash(curl:*)",
    "Bash(ls:*)",
    "Bash(cat:*)",
    "Bash(find:*)",
    "Bash(xargs -I {} sh -c 'echo \"\"=== {} ===\"\" && grep -n \"\"display:\"\" {}')",
    "Bash(docker compose:*)"
  ]
}
```

Esto permite que ciertas operaciones se ejecuten sin pedir confirmación.

---

## Ventajas del Sistema

1. **Historial Completo**: Registro automático de todas las interacciones
2. **Recuperación de Imágenes**: Las capturas pegadas se guardan permanentemente
3. **Debugging**: Fácil revisar qué pasó en conversaciones pasadas
4. **No Intrusivo**: No bloquea el flujo de trabajo
5. **Multiplataforma**: Compatible con Windows y Unix
6. **Escalable**: Fácil agregar nuevos hooks o logs

---

## Mantenimiento

### Limpieza de Logs
Los logs crecen indefinidamente. Para limpiarlos manualmente:
```bash
# Limpiar logs
del logs_system\logs\*.log

# Limpiar imágenes antiguas
del logs_system\images\screenshot_*.png

# Resetear índice de imágenes
echo {"images": []} > logs_system\data\.images_index.json
```

### Script de Limpieza Automática (`limpiar_log_system.bat`)
Para facilitar el mantenimiento, se ha creado el script `limpiar_log_system.bat`. Este archivo automatiza el proceso de limpieza.

**Función**:
- Elimina todo el contenido de las carpetas `data`, `images` y `logs`.
- Utiliza rutas relativas, por lo que debe ejecutarse desde su ubicación en `logs_system/`.

Para ejecutarlo, simplemente haz doble clic en el archivo o ejecútalo desde la terminal en el directorio `C:\parse\proyectos\apps\promet\.claude\logs_system\`.

### Modificar Hooks
Para agregar nuevos hooks, editar `.claude/settings.local.json` y agregar scripts en `.claude/logs_system/hooks/`.

---

## Troubleshooting

### Problema: Los logs no se están generando
- Verificar que los scripts tengan permisos de ejecución
- Revisar que Python esté en el PATH
- Verificar encoding UTF-8 en Windows

### Problema: Imágenes no se guardan
- Verificar que el directorio `.claude/logs_system/images/` exista
- Revisar `debug-images.log` para ver errores
- Verificar que el transcript tenga datos de imagen en base64

### Problema: Conversaciones incompletas en logs
- Verificar que el archivo `.chat_temp.json` no esté corrupto
- El sistema se recupera automáticamente en el siguiente prompt

---

## Conclusión

Este sistema proporciona un registro completo y automático de todas las interacciones con Claude Code, permitiendo:
- Auditoría de conversaciones
- Recuperación de información pasada
- Análisis de patrones de uso
- Archivo permanente de recursos (imágenes)

Todo funciona de manera transparente sin interrumpir el flujo de trabajo normal.
