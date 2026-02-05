@{
    RootModule = 'm8bits.psm1'
    ModuleVersion = '1.0.0'
    GUID = 'b8f3c2a1-4d5e-6f78-9abc-def012345678'
    Author = 'Cristobal Lopez'
    CompanyName = 'theBigMocho'
    Copyright = '(c) 2026 Cristobal Lopez. MIT License.'
    Description = 'Utilidades para inicializar y gestionar proyectos con Claude Code'
    PowerShellVersion = '7.0'
    FunctionsToExport = @('Invoke-M8bits', 'Initialize-ClaudeProject', 'Show-M8bitsHelp')
    AliasesToExport = @('m8bits')
    PrivateData = @{
        PSData = @{
            Tags = @('claude', 'claude-code', 'cli', 'productivity', 'initialization')
            ProjectUri = 'https://github.com/theBigMocho/m8bits'
            LicenseUri = 'https://github.com/theBigMocho/m8bits/blob/master/LICENSE'
        }
    }
}
