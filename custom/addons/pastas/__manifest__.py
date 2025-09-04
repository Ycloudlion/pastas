# -*- coding: utf-8 -*-
{
    'name': 'Facturación Electrónica DGI Panamá',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Módulo de facturación electrónica para cumplir con las regulaciones del DGI de Panamá',
    'description': """
        Módulo de Facturación Electrónica DGI Panamá
        ===========================================
        
        Este módulo permite:
        * Generar facturas electrónicas según estándares del DGI
        * Integración con PAC (Proveedor Autorizado Calificado)
        * Firma digital de documentos
        * Envío automático al DGI
        * Reportes y consultas de estado
        
        Requisitos:
        * Certificado de firma electrónica del DGI
        * Integración con PAC autorizado
        * Configuración de datos fiscales de la empresa
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'depends': [
        'base',
        'account',
        'sale',
        'purchase',
        'point_of_sale',
        'l10n_pa',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'data/account_data.xml',
        'views/dgi_config_views.xml',
        'views/electronic_invoice_views.xml',
        'views/account_invoice_views.xml',
        'views/purchase_order_views.xml',
        'views/pos_order_views.xml',
        'views/pos_config_views.xml',
        'views/branch_views.xml',
        'wizard/invoice_send_wizard.xml',
        'reports/electronic_invoice_report.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
