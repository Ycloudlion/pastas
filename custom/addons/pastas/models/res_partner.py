# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Campos para facturación electrónica
    ruc = fields.Char(
        string='RUC',
        help='Registro Único de Contribuyente (8 dígitos)'
    )
    dv = fields.Char(
        string='DV',
        size=1,
        help='Dígito Verificador (1 dígito)'
    )
    commercial_name = fields.Char(
        string='Nombre Comercial',
        help='Nombre comercial del cliente/proveedor'
    )
    
    @api.constrains('ruc')
    def _check_ruc(self):
        for record in self:
            if record.ruc and len(record.ruc) != 8:
                raise ValidationError(_('El RUC debe tener exactamente 8 dígitos.'))
            if record.ruc and not record.ruc.isdigit():
                raise ValidationError(_('El RUC debe ser numérico.'))
    
    @api.constrains('dv')
    def _check_dv(self):
        for record in self:
            if record.dv and not record.dv.isdigit():
                raise ValidationError(_('El DV debe ser un dígito numérico.'))
    
    def get_full_ruc(self):
        """Retorna el RUC completo con DV"""
        if self.ruc and self.dv:
            return f"{self.ruc}-{self.dv}"
        return self.ruc or ''
    
