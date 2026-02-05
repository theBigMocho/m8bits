# Modulo m8bits - Utilidades para proyectos con Claude Code
# Ruta base de configuraciones (relativa al modulo)
$script:ClaudeCleanPath = Join-Path $PSScriptRoot "templates"

function Invoke-M8bits {
    <#
    .SYNOPSIS
    Comando principal m8bits con subcomandos.

    .DESCRIPTION
    Utilidades para inicializar y gestionar proyectos con Claude Code.

    .PARAMETER Command
    Subcomando a ejecutar: init, help

    .EXAMPLE
    m8bits init
    Copia la configuracion .claude al directorio actual.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Position = 0)]
        [ValidateSet("init", "help", "")]
        [string]$Command = "help"
    )

    switch ($Command) {
        "init" {
            Initialize-ClaudeProject
        }
        default {
            Show-M8bitsHelp
        }
    }
}

function Initialize-ClaudeProject {
    <#
    .SYNOPSIS
    Inicializa la configuracion de Claude Code en el directorio actual.
    #>

    $targetPath = Get-Location
    $claudeFolder = Join-Path $targetPath ".claude"

    # Verificar si ya existe .claude
    if (Test-Path $claudeFolder) {
        Write-Host "[!] Ya existe una carpeta .claude en este directorio." -ForegroundColor Yellow
        $response = Read-Host "Deseas sobrescribir? (s/N)"
        if ($response -notmatch "^[sS]$") {
            Write-Host "Operacion cancelada." -ForegroundColor Gray
            return
        }
    }

    # Verificar que existe la fuente
    if (-not (Test-Path $script:ClaudeCleanPath)) {
        Write-Host "[X] No se encontro la carpeta fuente: $script:ClaudeCleanPath" -ForegroundColor Red
        return
    }

    # Copiar configuracion
    try {
        Copy-Item -Path "$script:ClaudeCleanPath\*" -Destination $targetPath -Recurse -Force
        Write-Host "[OK] Configuracion .claude copiada exitosamente." -ForegroundColor Green
        Write-Host "     Ahora puedes ejecutar 'claude' para iniciar Claude Code." -ForegroundColor Cyan
    }
    catch {
        Write-Host "[X] Error al copiar: $_" -ForegroundColor Red
    }
}

function Show-M8bitsHelp {
    Write-Host ""
    Write-Host "m8bits - Utilidades para proyectos con Claude Code" -ForegroundColor Cyan
    Write-Host "=================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Comandos disponibles:" -ForegroundColor White
    Write-Host "  m8bits init    Inicializa .claude en el directorio actual" -ForegroundColor Gray
    Write-Host "  m8bits help    Muestra esta ayuda" -ForegroundColor Gray
    Write-Host ""
}

# Crear alias 'm8bits' para el comando principal
Set-Alias -Name m8bits -Value Invoke-M8bits

# Exportar funciones y alias
Export-ModuleMember -Function Invoke-M8bits, Initialize-ClaudeProject, Show-M8bitsHelp
Export-ModuleMember -Alias m8bits
