-- Agregar columnas faltantes a res_partner
ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS ruc VARCHAR(8);
ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS dv VARCHAR(1);
ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS commercial_name VARCHAR(255);

-- Verificar que las columnas se crearon
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'res_partner' 
AND column_name IN ('ruc', 'dv', 'commercial_name');
