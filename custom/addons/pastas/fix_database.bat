@echo off
REM Script para agregar las columnas faltantes a res_partner
REM Ejecutar este script desde la carpeta del proyecto

echo === CORRECCION DE BASE DE DATOS ===
echo Este script te ayudara a agregar las columnas faltantes a res_partner

REM Verificar si estamos en el directorio correcto
if not exist "__manifest__.py" (
    echo Error: Ejecuta este script desde la carpeta del modulo pastas
    pause
    exit /b 1
)

echo.
echo PASO 1: Crear archivo SQL temporal
(
echo -- Agregar columnas faltantes a res_partner
echo ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS ruc VARCHAR^(8^);
echo ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS dv VARCHAR^(1^);
echo ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS commercial_name VARCHAR^(255^);
echo.
echo -- Verificar que las columnas se crearon
echo SELECT column_name, data_type 
echo FROM information_schema.columns 
echo WHERE table_name = 'res_partner' 
echo AND column_name IN ^('ruc', 'dv', 'commercial_name'^);
) > temp_add_columns.sql

echo Archivo SQL creado: temp_add_columns.sql
echo.
echo PASO 2: Ejecutar SQL en la base de datos
echo Copia y pega este SQL en tu cliente de base de datos:
echo.
echo --- INICIO DEL SQL ---
type temp_add_columns.sql
echo --- FIN DEL SQL ---
echo.

echo PASO 3: Despues de ejecutar el SQL
echo 1. Reinicia Odoo
echo 2. El error deberia desaparecer
echo 3. Los campos RUC, DV apareceran en Contactos
echo.

echo ¿Tienes acceso a pgAdmin o MySQL Workbench?
pause

REM Limpiar archivo temporal
del temp_add_columns.sql

echo Script completado
pause
