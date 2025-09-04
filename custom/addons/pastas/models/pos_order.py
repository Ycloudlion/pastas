# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    electronic_invoice_id = fields.One2many(
        'electronic.invoice',
        'pos_order_id',
        string='Factura Electrónica'
    )
    is_electronic = fields.Boolean(
        string='Es Electrónica',
        default=False
    )
    
    def _create_electronic_invoice_from_pos(self):
        """Crear factura electrónica desde orden POS"""
        for order in self:
            if order.state == 'paid' and order.account_move:
                move = order.account_move
                if move.move_type == 'out_invoice' and not move.electronic_invoice_id:
                    # Crear factura electrónica
                    electronic_invoice = self.env['electronic.invoice'].create({
                        'pos_order_id': order.id,
                        'move_id': move.id,
                        'partner_id': order.partner_id.id or self.env.user.partner_id.id,
                        'date': order.date_order.date(),
                        'amount_total': order.amount_total,
                        'document_type': 'out_invoice',
                        'state': 'draft',
                    })
                    
                    order.is_electronic = True
                    order.electronic_invoice_id = [(4, electronic_invoice.id)]
    
    def action_pos_order_paid(self):
        """Override para crear factura electrónica cuando se paga la orden"""
        res = super().action_pos_order_paid()
        
        # Crear factura electrónica automáticamente
        self._create_electronic_invoice_from_pos()
        
        return res
