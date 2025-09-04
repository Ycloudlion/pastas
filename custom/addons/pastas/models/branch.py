# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Branch(models.Model):
    _name = 'branch'
    _description = 'Sucursales de la Empresa'
    _rec_name = 'name'

    name = fields.Char(
        string='Nombre de la Sucursal',
        required=True
    )
    code = fields.Char(
        string='Código',
        required=True,
        help='Código único para identificar la sucursal'
    )
    address = fields.Text(
        string='Dirección'
    )
    phone = fields.Char(
        string='Teléfono'
    )
    email = fields.Char(
        string='Email'
    )
    manager_id = fields.Many2one(
        'res.users',
        string='Gerente de Sucursal'
    )
    is_active = fields.Boolean(
        string='Activa',
        default=True
    )
    dgi_config_id = fields.Many2one(
        'dgi.config',
        string='Configuración DGI',
        help='Configuración específica de facturación electrónica para esta sucursal'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        default=lambda self: self.env.user.company_id,
        required=True
    )
    
    @api.model
    def get_branch_by_code(self, code):
        """Obtiene una sucursal por su código"""
        return self.search([('code', '=', code)], limit=1)
    
    def get_dgi_config(self):
        """Obtiene la configuración DGI de la sucursal"""
        self.ensure_one()
        if self.dgi_config_id:
            return self.dgi_config_id
        # Si no tiene configuración específica, usar la principal
        return self.env['dgi.config'].search([('company_id', '=', self.company_id.id)], limit=1)
