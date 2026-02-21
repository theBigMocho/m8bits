# Instrucciones para Claude

- Nunca usar emojis en codigo fuente
- Los comentarios y logs deben ser en texto plano

## Imagenes en la conversacion

Si el usuario hace referencia a una imagen (palabras como "captura", "screenshot",
"imagen", "ves aqui", "en esto", "mira esto", "como ves", etc.) y no hay imagen
embebida en el contexto de la conversacion actual:

1. Leer `.claude/logs_system/data/.images_index.json`
2. Buscar la entrada mas reciente con `"read_by_claude": false`
3. Si existe, usar el tool Read para leer ese archivo de imagen (campo `path`)
4. Despues de leer la imagen, ejecutar:
   `python .claude/logs_system/mark-image-read.py --latest`
   para marcar la imagen como procesada en el indice

Esto es necesario porque cuando Claude Code corre en WSL no puede leer el clipboard
de Windows directamente. El hook `capture-wsl-clipboard.py` captura la imagen al
momento de enviar el prompt y la deja lista en el indice para que Claude la lea.


## Ayuda Memoria de Usuario

- **Git commit multilinea en PowerShell**: Heredoc no funciona. Usar: `pwsh -Command '$msg = "Titulo`n`nCo-Authored-By: ..."; git commit -m $msg'`
- **Encadenar comandos en PowerShell**: `&&` falla si despues hay asignacion de variables. Usar `;` en su lugar.


## Tareas Pendientes
