# Integrar desde Sandbox a Producción

Integra componentes y módulos refactorizados del sandbox al sistema de producción en `C:\parse\proyectos\apps\promet`.

## Flujo de Integración

### 1. **Análisis y Preparación**
- Compara archivos entre sandbox (`C:\parse\proyectos\sandbox\Promet\arp-components\`) y producción (`C:\parse\proyectos\apps\promet\arp-components\`)
- Identifica archivos NUEVOS que no existen en producción
- Identifica archivos MODIFICADOS que tienen cambios respecto a producción
- Lista todos los archivos candidatos a integración

### 2. **Copiar Archivos Nuevos**
Para cada archivo nuevo en sandbox:
- Copiar a la ubicación correspondiente en producción
- Ajustar rutas de imports si es necesario:
  - `import ... from './arp-models.js'` → `import ... from '../arp-models.js'`
  - `import ... from './utils.js'` → `import ... from '../utils.js'`
  - Cualquier otra ruta relativa que deba ajustarse según la estructura

### 3. **Integrar Cambios en Archivos Existentes**
Para archivos que existen en ambos lados (ej: arp-main.js, arp-turnos-data.js):
- Mostrar un diff de los cambios
- Preguntar al usuario si desea aplicar los cambios
- Si el usuario confirma, aplicar los cambios manteniendo la estructura del archivo de producción

### 4. **Actualizar Referencias en HTML/ASPX**
- Verificar si hay nuevos scripts/módulos que necesiten ser importados en `arp.aspx`
- Agregar los `<script>` tags necesarios en la ubicación correcta (después de dependencias, antes de archivos que los usan)
- Usar `type="module"` para archivos ES6 que contienen `import/export`

### 5. **Validación**
- Verificar que no se hayan roto imports
- Buscar referencias rotas o rutas incorrectas
- Validar que archivos críticos sigan siendo accesibles

### 6. **Reporte de Integración**
Al finalizar, mostrar:
- ✅ Archivos NUEVOS copiados (con ajustes de rutas realizados)
- ✅ Archivos MODIFICADOS actualizados
- ✅ Scripts agregados a arp.aspx
- 📋 Lista de archivos listos para commit
- ⚠️ Cualquier advertencia o conflicto detectado

## Archivos a Considerar

### Archivos del componente
- `arp-components/arp-turnos-component/*.js`
- `arp-components/arp-schedule-adapter*.js`
- `arp-components/*.md` (documentación)

### Archivos del sistema principal
- `arp-models.js` (si tiene cambios de exportación)
- `arp-main.js` (si tiene refactorizaciones)
- `arp.aspx` (si necesita nuevos imports)

## Notas Importantes

- **NO** copiar archivos de configuración de Claude (`.claude/`)
- **NO** copiar archivos de git (`.git/`, `.gitignore`)
- **NO** sobrescribir archivos de producción sin confirmar
- **SIEMPRE** ajustar rutas de imports al copiar entre directorios
- **VERIFICAR** que las rutas relativas funcionen correctamente

## Ejemplo de Uso

```
Usuario: /integrar-desde-sandbox arp-schedule-adapter

Claude:
1. Analiza archivos en sandbox/Promet/arp-components/
2. Encuentra: arp-schedule-adapter.js, arp-schedule-adapter-ejemplo.js, ADAPTADOR-README.md
3. Copia a producción con ajustes de rutas
4. Detecta cambios en arp-models.js (exportaciones ES6)
5. Pregunta si aplicar cambios a arp-models.js
6. Detecta necesidad de import en arp.aspx
7. Agrega <script> tag en la ubicación correcta
8. Genera reporte de integración
```

## Después de la Integración

Recomendar al usuario:
1. Probar la aplicación para verificar que todo funciona
2. Usar `/commit-and-push` para versionar y subir cambios
3. Revisar el ADAPTADOR-README.md (si existe) para pasos adicionales de implementación
