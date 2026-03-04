# Levantamiento de Medidas para Odoo 17

Módulo para gestionar levantamientos de medidas en sucursales de clientes, con seguimiento tipo CRM para instalaciones y reimpresiones futuras.

## Características

### Gestión de Levantamientos
- **Registro de medidas** por cliente y sucursal
- **Tipos de elementos configurables** (cristales, vallas, letreros, banners, etc.)
- **Soporte para unidades de medida** con conversiones automáticas (cm, m, pulgadas)
- **Cálculo automático de áreas** en metros cuadrados

### Galería de Fotos
- Adjuntar múltiples fotos de referencia
- Categorización por tipo (antes, durante, después, incidencia)
- Fotos individuales por cada línea de medida

### Seguimiento y Trazabilidad
- **Estados tipo pipeline**: Borrador → Medido → En Producción → En Instalación → Instalado → Cerrado
- **Notas de instalación** e incidencias
- **Historial completo** vía chatter de Odoo
- **Vinculación con pedidos de venta**

### Reportes
- **Reporte PDF imprimible** con medidas, fotos y notas
- Perfecto para entregar al cliente o archivar

## Instalación

1. Copiar el módulo a la carpeta `addons` de Odoo
2. Reiniciar el servidor de Odoo
3. Activar el modo desarrollador
4. Ir a Aplicaciones → Actualizar lista de aplicaciones
5. Buscar "Levantamiento de Medidas" e instalar

## Dependencias

- `base`
- `contacts`
- `mail`
- `sale`
- `uom`

## Configuración

1. Ir a **Levantamientos → Configuración → Tipos de Elementos**
2. Configurar los tipos de elementos según su negocio
3. Asignar usuarios a los grupos de seguridad correspondientes

## Uso

1. Crear un nuevo levantamiento desde **Levantamientos → Levantamientos de Medidas**
2. Seleccionar cliente y sucursal
3. Agregar las líneas de medidas con tipo, ubicación y dimensiones
4. Adjuntar fotos de referencia
5. Confirmar las medidas y seguir el flujo de trabajo

## Licencia

LGPL-3

## Autor

Tu Empresa
