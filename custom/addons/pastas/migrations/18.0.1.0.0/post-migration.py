# -*- coding: utf-8 -*-

def migrate(cr, version):
    """Migración para agregar campos RUC y DV a res.partner"""
    
    # Verificar si las columnas ya existen
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'res_partner' 
        AND column_name IN ('ruc', 'dv', 'commercial_name')
    """)
    
    existing_columns = [row[0] for row in cr.fetchall()]
    
    # Agregar columna RUC si no existe
    if 'ruc' not in existing_columns:
        cr.execute("""
            ALTER TABLE res_partner 
            ADD COLUMN ruc VARCHAR(8)
        """)
    
    # Agregar columna DV si no existe
    if 'dv' not in existing_columns:
        cr.execute("""
            ALTER TABLE res_partner 
            ADD COLUMN dv VARCHAR(1)
        """)
    
    # Agregar columna commercial_name si no existe
    if 'commercial_name' not in existing_columns:
        cr.execute("""
            ALTER TABLE res_partner 
            ADD COLUMN commercial_name VARCHAR(255)
        """)
    
    # Crear índices para mejorar el rendimiento
    try:
        cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_res_partner_ruc 
            ON res_partner(ruc) 
            WHERE ruc IS NOT NULL
        """)
    except:
        pass  # El índice ya existe o hay un error menor
