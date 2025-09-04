# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ElectronicInvoiceReport(models.AbstractModel):
    _name = 'report.electronic_invoice.report_electronic_invoice'
    _description = 'Reporte de Facturas Electrónicas'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Obtiene los valores para el reporte"""
        docs = self.env['electronic.invoice'].browse(docids)
        
        if not docs:
            raise UserError(_('No se encontraron facturas electrónicas para reportar.'))
        
        return {
            'doc_ids': docids,
            'doc_model': 'electronic.invoice',
            'docs': docs,
            'data': data,
        }


class ElectronicInvoiceReportWizard(models.TransientModel):
    _name = 'electronic.invoice.report.wizard'
    _description = 'Wizard para Reporte de Facturas Electrónicas'

    date_from = fields.Date(
        string='Fecha Desde',
        required=True,
        default=fields.Date.today
    )
    date_to = fields.Date(
        string='Fecha Hasta',
        required=True,
        default=fields.Date.today
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviado'),
        ('authorized', 'Autorizado'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado')
    document_type = fields.Selection([
        ('01', 'Factura'),
        ('02', 'Nota de Crédito'),
        ('03', 'Nota de Débito'),
        ('04', 'Comprobante de Retención'),
        ('05', 'Comprobante de Pago'),
    ], string='Tipo de Documento')
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        default=lambda self: self.env.user.company_id
    )

    def action_generate_report(self):
        """Genera el reporte de facturas electrónicas"""
        self.ensure_one()
        
        # Construir dominio de búsqueda
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]
        
        if self.state:
            domain.append(('state', '=', self.state))
        
        if self.document_type:
            domain.append(('document_type', '=', self.document_type))
        
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        
        # Buscar facturas electrónicas
        electronic_invoices = self.env['electronic.invoice'].search(domain)
        
        if not electronic_invoices:
            raise UserError(_('No se encontraron facturas electrónicas con los criterios seleccionados.'))
        
        # Generar reporte
        return {
            'type': 'ir.actions.report',
            'report_name': 'electronic_invoice.report_electronic_invoice',
            'report_type': 'qweb-pdf',
            'data': {
                'ids': electronic_invoices.ids,
                'model': 'electronic.invoice',
            },
            'context': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'state': self.state,
                'document_type': self.document_type,
                'partner_id': self.partner_id.id if self.partner_id else False,
            }
        }
