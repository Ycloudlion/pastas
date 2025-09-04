# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    electronic_invoice_id = fields.Many2one(
        'electronic.invoice',
        string='Factura Electrónica',
        copy=False
    )
    is_electronic = fields.Boolean(
        string='Es Electrónica',
        default=False
    )
    electronic_state = fields.Selection(
        related='electronic_invoice_id.state',
        string='Estado Electrónico',
        store=True
    )
    
    def _create_electronic_invoice_from_pos(self):
        """Crear factura electrónica desde orden POS"""
        self.ensure_one()
        if not self.account_move:
            return False
            
        if self.electronic_invoice_id:
            return self.electronic_invoice_id
            
        # Obtener configuración DGI del POS
        pos_config = self.env['pos.config'].search([('enable_electronic_invoice', '=', True)], limit=1)
        dgi_config = pos_config.dgi_config_id if pos_config else self.env['dgi.config'].search([], limit=1)
        
        # Crear factura electrónica
        electronic_invoice = self.env['electronic.invoice'].create({
            'pos_order_id': self.id,
            'move_id': self.account_move.id,
            'partner_id': self.partner_id.id or self.env.user.partner_id.id,
            'amount_total': self.amount_total,
            'document_type': 'invoice',
            'state': 'draft',
            'branch_id': pos_config.branch_id.id if pos_config else False,
        })
        
        self.write({
            'is_electronic': True,
            'electronic_invoice_id': electronic_invoice.id,
        })
        
        return electronic_invoice
    
    def action_pos_order_paid(self):
        """Override para crear factura electrónica cuando se paga la orden"""
        res = super().action_pos_order_paid()
        
        # Crear factura electrónica automáticamente
        for order in self:
            if order.account_move and not order.electronic_invoice_id:
                order._create_electronic_invoice_from_pos()
        
        return res
