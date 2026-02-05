# Commit y Push con Versionado

Realiza el siguiente flujo completo:

1. **Incrementa la versión**: Lee `Promet/arp-components/arp-turnos-component/version.txt`, incrementa el número de patch (tercer dígito), y escribe la nueva versión
2. **Verifica cambios**: Ejecuta `git status` y `git diff` para ver qué archivos han cambiado
3. **Revisa commits recientes**: Ejecuta `git log --oneline -5` para ver el estilo de mensajes de commit
4. **Agrega archivos**: Agrega todos los archivos relevantes al staging area (NO agregues archivos de .claude/settings.local.json)
5. **Crea commit**: Genera un mensaje de commit apropiado basado en los cambios, siguiendo el estilo del repositorio
6. **Push**: Sube los cambios al repositorio remoto

Al finalizar, muestra un resumen de:
- Versión anterior → Nueva versión
- Archivos commiteados
- Mensaje del commit
- Resultado del push
