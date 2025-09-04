# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    enable_electronic_invoice = fields.Boolean(
        string='Habilitar Facturación Electrónica',
        default=True,
        help='Permitir generar facturas electrónicas desde el punto de venta'
    )
    dgi_config_id = fields.Many2one(
        'dgi.config',
        string='Configuración DGI',
        help='Configuración DGI para facturas electrónicas del POS'
    )
    branch_id = fields.Many2one(
        'branch',
        string='Sucursal',
        help='Sucursal asociada a este punto de venta'
    )
    
    @api.model
    def get_electronic_invoice_config(self):
        """Obtiene la configuración de facturación electrónica para el POS"""
        config = self.search([('enable_electronic_invoice', '=', True)], limit=1)
        if config and config.dgi_config_id:
            return config.dgi_config_id
        return self.env['dgi.config'].search([], limit=1)
