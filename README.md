# m8bits - Modulo PowerShell para Claude Code

Utilidades para inicializar y gestionar proyectos con Claude Code.

---

## Indice

1. [Que es PowerShell](#que-es-powershell)
2. [Que son los modulos de PowerShell](#que-son-los-modulos-de-powershell)
3. [Instalacion](#instalacion)
4. [Comandos disponibles](#comandos-disponibles)
5. [Como funciona internamente](#como-funciona-internamente)
6. [Agregar nuevos comandos](#agregar-nuevos-comandos)
7. [Distribuir el modulo](#distribuir-el-modulo)
8. [Troubleshooting](#troubleshooting)

---

## Que es PowerShell

PowerShell es el shell de linea de comandos moderno de Microsoft. A diferencia de CMD (el antiguo Command Prompt), PowerShell es un lenguaje de scripting completo orientado a objetos.

### Diferencias clave con CMD y Bash

| Caracteristica | CMD | Bash | PowerShell |
|----------------|-----|------|------------|
| Tipo de datos | Solo texto | Solo texto | Objetos .NET |
| Extensibilidad | Limitada | Scripts | Modulos, clases |
| Sintaxis | Comandos DOS | Unix | Verbo-Sustantivo |
| Plataforma | Solo Windows | Unix/Linux | Multiplataforma |

### PowerShell 7 vs Windows PowerShell

- **Windows PowerShell (5.1)**: Viene preinstalado en Windows, ejecutable `powershell.exe`
- **PowerShell 7+**: Version moderna y multiplataforma, ejecutable `pwsh.exe`

Este modulo usa **PowerShell 7** (`pwsh`).

[Volver al indice](#indice)

---

## Que son los modulos de PowerShell

Un **modulo** es un paquete reutilizable que contiene funciones, variables y otros recursos de PowerShell. Es la forma estandar de organizar y distribuir codigo.

### Estructura de un modulo

```
NombreModulo/
├── NombreModulo.psm1    # Codigo del modulo (funciones)
├── NombreModulo.psd1    # Manifiesto (metadatos, versiones, exports)
└── README.md            # Documentacion (opcional)
```

### Archivos principales

| Archivo | Extension | Proposito |
|---------|-----------|-----------|
| Module Script | `.psm1` | Contiene las funciones y logica del modulo |
| Module Manifest | `.psd1` | Define metadatos: version, autor, que se exporta |

### Donde se instalan los modulos

PowerShell busca modulos en estas rutas (en orden):

```powershell
$env:PSModulePath -split ";"
```

Tipicamente:
1. `~\Documents\PowerShell\Modules` - Modulos del usuario (aqui esta m8bits)
2. `C:\Program Files\PowerShell\Modules` - Modulos compartidos
3. `C:\Program Files\PowerShell\7\Modules` - Modulos del sistema

### Auto-carga de modulos

Desde PowerShell 3.0, los modulos se **cargan automaticamente** cuando usas un comando que exportan. No necesitas hacer `Import-Module` manualmente.

Esto funciona porque:
1. PowerShell escanea las carpetas de `$env:PSModulePath`
2. Lee los manifiestos (`.psd1`) para saber que comandos exporta cada modulo
3. Cuando escribes un comando, busca cual modulo lo provee y lo carga

[Volver al indice](#indice)

---

## Instalacion

El modulo ya esta instalado en:

```
C:\Users\crist\OneDrive\Documentos\PowerShell\Modules\m8bits\
```

Para verificar que esta disponible:

```powershell
Get-Module -ListAvailable m8bits
```

Para ver informacion del modulo:

```powershell
Get-Module m8bits | Format-List
```

[Volver al indice](#indice)

---

## Comandos disponibles

### m8bits init

Copia la configuracion base de Claude Code (`.claude/`) al directorio actual.

```powershell
cd C:\_dev\mi-nuevo-proyecto
m8bits init
```

**Que copia:**
- `.claude/commands/` - Comandos personalizados (commit-and-push, etc.)
- `.claude/logs_system/` - Sistema de logging con hooks
- `.claude/settings.local.json` - Configuracion local

**Comportamiento:**
- Si ya existe `.claude/`, pregunta antes de sobrescribir
- Muestra mensaje de exito o error con colores

### m8bits help

Muestra la ayuda con los comandos disponibles.

```powershell
m8bits help
```

[Volver al indice](#indice)

---

## Como funciona internamente

### Flujo de ejecucion

```
Usuario escribe: m8bits init
         │
         ▼
PowerShell detecta comando 'm8bits'
         │
         ▼
Busca en $env:PSModulePath
         │
         ▼
Encuentra m8bits.psd1, lee exports
         │
         ▼
Carga m8bits.psm1 automaticamente
         │
         ▼
Ejecuta alias 'm8bits' → Invoke-M8bits
         │
         ▼
Switch detecta subcomando 'init'
         │
         ▼
Ejecuta Initialize-ClaudeProject
         │
         ▼
Copy-Item copia archivos de .claude_clean
```

### Estructura del codigo

```powershell
# Variable de script (privada al modulo)
$script:ClaudeCleanPath = "C:\_dev\.claude_proyect\.claude_clean"

# Funcion principal con subcomandos
function Invoke-M8bits {
    param([string]$Command)
    switch ($Command) {
        "init" { Initialize-ClaudeProject }
        default { Show-M8bitsHelp }
    }
}

# Funcion que hace el trabajo real
function Initialize-ClaudeProject {
    # 1. Verifica si ya existe .claude
    # 2. Verifica que existe la fuente
    # 3. Copia archivos con Copy-Item
}

# Alias para usar 'm8bits' en vez de 'Invoke-M8bits'
Set-Alias -Name m8bits -Value Invoke-M8bits

# Exporta funciones y alias para que sean visibles
Export-ModuleMember -Function ... -Alias m8bits
```

### Por que usar un alias

La convencion de PowerShell es `Verbo-Sustantivo` (ej: `Get-Process`, `Set-Location`). Pero para comandos CLI cortos, se usan **alias**:

| Comando real | Alias |
|--------------|-------|
| `Invoke-M8bits` | `m8bits` |
| `Get-ChildItem` | `ls`, `dir` |
| `Set-Location` | `cd` |

[Volver al indice](#indice)

---

## Agregar nuevos comandos

Para agregar un nuevo subcomando (ej: `m8bits clean`):

### 1. Editar m8bits.psm1

Agregar el caso en el switch:

```powershell
switch ($Command) {
    "init" { Initialize-ClaudeProject }
    "clean" { Clear-ClaudeLogs }        # Nuevo
    default { Show-M8bitsHelp }
}
```

### 2. Crear la funcion

```powershell
function Clear-ClaudeLogs {
    $logsPath = Join-Path (Get-Location) ".claude\logs_system\logs"
    if (Test-Path $logsPath) {
        Remove-Item "$logsPath\*" -Recurse -Force
        Write-Host "[OK] Logs limpiados." -ForegroundColor Green
    }
}
```

### 3. Actualizar ValidateSet

```powershell
[ValidateSet("init", "clean", "help", "")]
[string]$Command = "help"
```

### 4. Actualizar la ayuda

```powershell
function Show-M8bitsHelp {
    # Agregar linea para el nuevo comando
    Write-Host "  m8bits clean   Limpia los logs de Claude" -ForegroundColor Gray
}
```

### 5. Exportar la nueva funcion

```powershell
Export-ModuleMember -Function Invoke-M8bits, Initialize-ClaudeProject, Clear-ClaudeLogs, Show-M8bitsHelp
```

### 6. Recargar el modulo

```powershell
Remove-Module m8bits -Force; Import-Module m8bits
```

[Volver al indice](#indice)

---

## Distribuir el modulo

Los modulos de PowerShell pueden compartirse con otras personas de varias formas.

### Metodos de distribucion

| Metodo | Complejidad | Ideal para |
|--------|-------------|------------|
| Copiar carpeta | Baja | Amigos, equipo pequeno |
| Repositorio Git | Media | Equipos, open source |
| PowerShell Gallery | Alta | Distribucion publica mundial |
| Repositorio privado | Alta | Empresas con modulos internos |

### 1. Copiar carpeta (mas simple)

Compartir la carpeta del modulo directamente. El destinatario la copia a su ruta de modulos:

```powershell
# El destinatario ejecuta esto para ver donde copiar
$env:PSModulePath -split ";" | Select-Object -First 1
# Resultado tipico: C:\Users\USUARIO\Documents\PowerShell\Modules

# Copiar la carpeta m8bits/ ahi
```

**Estructura a compartir:**
```
m8bits/
├── m8bits.psm1
├── m8bits.psd1
└── README.md
```

### 2. Repositorio Git (GitHub, GitLab, etc.)

Subir el modulo a un repositorio. Los usuarios lo clonan directamente:

```powershell
# Clonar a la carpeta de modulos
git clone https://github.com/usuario/m8bits.git "$HOME\Documents\PowerShell\Modules\m8bits"
```

**Ventajas:**
- Control de versiones
- Issues y colaboracion
- Facil de actualizar (`git pull`)

### 3. PowerShell Gallery (distribucion publica)

[PowerShell Gallery](https://www.powershellgallery.com/) es el repositorio oficial, similar a npm (Node) o PyPI (Python).

**Para el usuario final:**
```powershell
# Instalar cualquier modulo publico
Install-Module -Name NombreModulo

# Actualizar
Update-Module -Name NombreModulo
```

**Para publicar un modulo:**

1. Crear cuenta en [powershellgallery.com](https://www.powershellgallery.com/)

2. Obtener API Key desde tu perfil

3. Completar el manifiesto `.psd1` con metadata requerida:
```powershell
@{
    RootModule = 'm8bits.psm1'
    ModuleVersion = '1.0.0'
    GUID = 'guid-unico-aqui'
    Author = 'Tu Nombre'
    Description = 'Descripcion del modulo'
    PowerShellVersion = '7.0'

    # Requeridos para Gallery
    PrivateData = @{
        PSData = @{
            Tags = @('claude', 'cli', 'productivity')
            ProjectUri = 'https://github.com/usuario/m8bits'
            LicenseUri = 'https://github.com/usuario/m8bits/blob/main/LICENSE'
        }
    }
}
```

4. Publicar:
```powershell
Publish-Module -Path ".\m8bits" -NuGetApiKey "tu-api-key"
```

### 4. Repositorio privado (empresas)

Para modulos internos que no deben ser publicos:

```powershell
# Registrar repositorio privado (NuGet, Azure Artifacts, etc.)
Register-PSRepository -Name "MiEmpresa" -SourceLocation "https://nuget.miempresa.com/v3/index.json"

# Instalar desde repositorio privado
Install-Module -Name m8bits -Repository "MiEmpresa"
```

### Consideraciones para distribuir m8bits

Este modulo tiene una **dependencia de ruta hardcodeada**:

```powershell
$script:ClaudeCleanPath = "C:\_dev\.claude_proyect\.claude_clean"
```

Para distribuirlo, considera:

1. **Hacer la ruta configurable** via variable de entorno:
```powershell
$script:ClaudeCleanPath = $env:M8BITS_TEMPLATE_PATH ?? "C:\_dev\.claude_proyect\.claude_clean"
```

2. **Incluir los templates** dentro del modulo:
```
m8bits/
├── m8bits.psm1
├── m8bits.psd1
├── README.md
└── templates/
    └── .claude/
        ├── commands/
        ├── logs_system/
        └── settings.local.json
```

3. **Documentar el requisito** para que el usuario cree su propia carpeta de templates.

[Volver al indice](#indice)

---

## Troubleshooting

### El comando m8bits no se reconoce

```powershell
# Verificar que el modulo existe
Get-Module -ListAvailable m8bits

# Si no aparece, verificar la ruta
Test-Path "~\Documents\PowerShell\Modules\m8bits\m8bits.psd1"

# Importar manualmente
Import-Module m8bits -Verbose
```

### Cambios en el modulo no se reflejan

PowerShell cachea los modulos. Para recargar:

```powershell
Remove-Module m8bits -Force
Import-Module m8bits
```

### Ver errores detallados

```powershell
$ErrorActionPreference = "Stop"
Import-Module m8bits -Verbose
```

### Verificar que exporta el modulo

```powershell
Get-Command -Module m8bits
```

[Volver al indice](#indice)

---

## Referencias

- [Documentacion oficial de modulos PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/developer/module/writing-a-windows-powershell-module)
- [PowerShell 7 - Novedades](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/what-s-new-in-powershell-70)
