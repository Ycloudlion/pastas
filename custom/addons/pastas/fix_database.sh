#!/bin/bash

# Script para agregar las columnas faltantes a res_partner
# Ejecutar este script desde la carpeta del proyecto

echo "=== CORRECCIÓN DE BASE DE DATOS ==="
echo "Este script agregará las columnas faltantes a res_partner"

# Verificar si estamos en el directorio correcto
if [ ! -f "__manifest__.py" ]; then
    echo "Error: Ejecuta este script desde la carpeta del módulo pastas"
    exit 1
fi

echo ""
echo "PASO 1: Crear archivo SQL temporal"
cat > temp_add_columns.sql << 'EOF'
-- Agregar columnas faltantes a res_partner
ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS ruc VARCHAR(8);
ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS dv VARCHAR(1);
ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS commercial_name VARCHAR(255);

-- Verificar que las columnas se crearon
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'res_partner' 
AND column_name IN ('ruc', 'dv', 'commercial_name');
EOF

echo "Archivo SQL creado: temp_add_columns.sql"
echo ""
echo "PASO 2: Ejecutar SQL en la base de datos"
echo "Copia y pega este SQL en tu cliente de base de datos:"
echo ""
echo "--- INICIO DEL SQL ---"
cat temp_add_columns.sql
echo "--- FIN DEL SQL ---"
echo ""

echo "PASO 3: Después de ejecutar el SQL"
echo "1. Reinicia Odoo"
echo "2. El error debería desaparecer"
echo "3. Los campos RUC, DV aparecerán en Contactos"
echo ""

echo "¿Tienes acceso a pgAdmin o MySQL Workbench?"
read -p "Presiona Enter para continuar..."

# Limpiar archivo temporal
rm -f temp_add_columns.sql

echo "Script completado"
