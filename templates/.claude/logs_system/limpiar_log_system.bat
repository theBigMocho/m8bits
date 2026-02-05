@echo off
echo Limpiando carpetas...

REM Limpiar carpeta data
echo Limpiando data...
if exist "data\*" del /Q "data\*"
for /D %%p in ("data\*") do rmdir "%%p" /s /q
if not exist "data" mkdir "data"

REM Limpiar carpeta images
echo Limpiando images...
if exist "images\*" del /Q "images\*"
for /D %%p in ("images\*") do rmdir "%%p" /s /q
if not exist "images" mkdir "images"

REM Limpiar carpeta logs
echo Limpiando logs...
if exist "logs\*" del /Q "logs\*"
for /D %%p in ("logs\*") do rmdir "%%p" /s /q
if not exist "logs" mkdir "logs"

echo.
echo Limpieza completada.
pause
