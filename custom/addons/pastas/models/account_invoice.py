# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    electronic_invoice_id = fields.One2many(
        'electronic.invoice',
        'move_id',
        string='Factura Electrónica'
    )
    is_electronic = fields.Boolean(
        string='Es Electrónica',
        default=False
    )
    electronic_state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviado'),
        ('authorized', 'Autorizado'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado Electrónico', compute='_compute_electronic_state', store=True)
    dgi_number = fields.Char(
        string='Número DGI',
        compute='_compute_electronic_data',
        store=True
    )
    authorization_code = fields.Char(
        string='Código de Autorización',
        compute='_compute_electronic_data',
        store=True
    )
    authorization_date = fields.Datetime(
        string='Fecha de Autorización',
        compute='_compute_electronic_data',
        store=True
    )

    @api.depends('electronic_invoice_id.state')
    def _compute_electronic_state(self):
        for record in self:
            if record.electronic_invoice_id:
                record.electronic_state = record.electronic_invoice_id[0].state
            else:
                record.electronic_state = False

    @api.depends('electronic_invoice_id.number', 'electronic_invoice_id.authorization_code', 'electronic_invoice_id.authorization_date')
    def _compute_electronic_data(self):
        for record in self:
            if record.electronic_invoice_id:
                record.dgi_number = record.electronic_invoice_id[0].number
                record.authorization_code = record.electronic_invoice_id[0].authorization_code
                record.authorization_date = record.electronic_invoice_id[0].authorization_date
            else:
                record.dgi_number = False
                record.authorization_code = False
                record.authorization_date = False

    def action_create_electronic_invoice(self):
        """Crea una factura electrónica a partir de la factura normal"""
        self.ensure_one()
        
        if self.electronic_invoice_id:
            raise UserError(_('Esta factura ya tiene una factura electrónica asociada.'))
        
        if self.state != 'posted':
            raise UserError(_('Solo se pueden crear facturas electrónicas de facturas confirmadas.'))
        
        # Verificar configuración DGI
        dgi_config = self.env['dgi.config'].get_dgi_config()
        if not dgi_config:
            raise UserError(_('No se encontró configuración DGI. Configure primero los datos de la empresa.'))
        
        # Crear factura electrónica
        electronic_invoice = self.env['electronic.invoice'].create({
            'move_id': self.id,
            'document_type': '01',  # Factura
        })
        
        self.is_electronic = True
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Factura Electrónica'),
            'res_model': 'electronic.invoice',
            'res_id': electronic_invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_send_electronic_invoice(self):
        """Envía la factura electrónica al DGI"""
        self.ensure_one()
        
        if not self.electronic_invoice_id:
            raise UserError(_('No hay factura electrónica asociada.'))
        
        return self.electronic_invoice_id[0].send_to_dgi()
    
    def action_check_electronic_status(self):
        """Verifica el estado de la factura electrónica"""
        self.ensure_one()
        
        if not self.electronic_invoice_id:
            raise UserError(_('No hay factura electrónica asociada.'))
        
        return self.electronic_invoice_id[0].check_status()
    
    def action_cancel_electronic_invoice(self):
        """Cancela la factura electrónica"""
        self.ensure_one()
        
        if not self.electronic_invoice_id:
            raise UserError(_('No hay factura electrónica asociada.'))
        
        return self.electronic_invoice_id[0].cancel_invoice()
    
    def action_post(self):
        """Override para crear factura electrónica automáticamente"""
        res = super().action_post()
        
        # Crear factura electrónica solo para facturas de venta
        for move in self:
            if move.move_type in ['out_invoice', 'out_refund'] and not move.electronic_invoice_id:
                self._create_electronic_invoice(move)
        
        return res
