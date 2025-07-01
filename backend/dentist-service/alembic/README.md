# Migraciones de Base de Datos para Dentist Service

Este directorio contiene las migraciones de base de datos para el servicio de dentistas, gestionadas con Alembic.

## Comandos básicos

### Crear una nueva migración

```bash
# Generar automáticamente una migración basada en los cambios en los modelos
alembic revision --autogenerate -m "descripción de la migración"

# Crear una migración vacía para editar manualmente
alembic revision -m "descripción de la migración"
```

### Aplicar migraciones

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar hasta una revisión específica
alembic upgrade <revision_id>

# Aplicar un número específico de migraciones
alembic upgrade +2
```

### Revertir migraciones

```bash
# Revertir la última migración
alembic downgrade -1

# Revertir hasta una revisión específica
alembic downgrade <revision_id>

# Revertir todas las migraciones
alembic downgrade base
```

### Ver información

```bash
# Ver el historial de migraciones
alembic history

# Ver la migración actual
alembic current
```

## Estructura del esquema

El servicio utiliza un esquema dedicado llamado `dentist` en la base de datos PostgreSQL para mantener todas sus tablas separadas de otros servicios.

## Notas importantes

1. Siempre revise las migraciones generadas automáticamente antes de aplicarlas
2. Ejecute las pruebas después de aplicar migraciones para verificar que todo funciona correctamente
3. Para entornos de producción, haga una copia de seguridad de la base de datos antes de aplicar migraciones
