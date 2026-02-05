@{
    RootModule = 'm8bits.psm1'
    ModuleVersion = '1.0.0'
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    Author = 'crist'
    Description = 'Utilidades para inicializar y gestionar proyectos con Claude Code'
    PowerShellVersion = '7.0'
    FunctionsToExport = @('Invoke-M8bits', 'Initialize-ClaudeProject', 'Show-M8bitsHelp')
    AliasesToExport = @('m8bits')
}
