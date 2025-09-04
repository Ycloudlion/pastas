# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging
import xml.etree.ElementTree as ET
import base64
import hashlib
import uuid

_logger = logging.getLogger(__name__)


class ElectronicInvoice(models.Model):
    _name = 'electronic.invoice'
    _description = 'Factura Electrónica DGI'
    _order = 'create_date desc'
    _rec_name = 'number'

    # Información básica
    name = fields.Char(
        string='Número de Factura',
        required=True,
        copy=False,
        readonly=True,
        index=True
    )
    number = fields.Char(
        string='Número DGI',
        help='Número asignado por el DGI'
    )
    
    # Relaciones
    move_id = fields.Many2one(
        'account.move',
        string='Factura Original',
        ondelete='cascade'
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Orden de Compra',
        ondelete='cascade'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        compute='_compute_company_id',
        store=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente/Proveedor',
        compute='_compute_partner_id',
        store=True
    )

    @api.depends('move_id.company_id', 'purchase_order_id.company_id')
    def _compute_company_id(self):
        for record in self:
            if record.move_id:
                record.company_id = record.move_id.company_id
            elif record.purchase_order_id:
                record.company_id = record.purchase_order_id.company_id
            else:
                record.company_id = False

    @api.depends('move_id.partner_id', 'purchase_order_id.partner_id')
    def _compute_partner_id(self):
        for record in self:
            if record.move_id:
                record.partner_id = record.move_id.partner_id
            elif record.purchase_order_id:
                record.partner_id = record.purchase_order_id.partner_id
            else:
                record.partner_id = False
    
    # Datos del documento
    document_type = fields.Selection([
        ('01', 'Factura'),
        ('02', 'Nota de Crédito'),
        ('03', 'Nota de Débito'),
        ('04', 'Comprobante de Retención'),
        ('05', 'Comprobante de Pago'),
    ], string='Tipo de Documento', required=True, default='01')
    
    # Fechas
    invoice_date = fields.Date(
        string='Fecha de Factura',
        related='move_id.invoice_date',
        store=True
    )
    due_date = fields.Date(
        string='Fecha de Vencimiento',
        related='move_id.invoice_date_due',
        store=True
    )
    purchase_date = fields.Datetime(
        string='Fecha de Compra',
        related='purchase_order_id.date_order',
        store=True
    )
    authorization_date = fields.Datetime(
        string='Fecha de Autorización',
        help='Fecha y hora de autorización por el DGI'
    )
    
    # Montos
    amount_untaxed = fields.Monetary(
        string='Subtotal',
        related='move_id.amount_untaxed',
        store=True
    )
    amount_tax = fields.Monetary(
        string='Impuestos',
        related='move_id.amount_tax',
        store=True
    )
    amount_total = fields.Monetary(
        string='Total',
        related='move_id.amount_total',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='move_id.currency_id',
        store=True
    )
    
    # Estado del documento
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviado'),
        ('authorized', 'Autorizado'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', required=True)
    
    # Archivos XML
    xml_request = fields.Binary(
        string='XML de Solicitud',
        help='XML enviado al DGI'
    )
    xml_filename = fields.Char(
        string='Nombre del XML'
    )
    xml_response = fields.Binary(
        string='XML de Respuesta',
        help='XML de respuesta del DGI'
    )
    xml_response_filename = fields.Char(
        string='Nombre del XML de Respuesta'
    )
    
    # Códigos de respuesta
    response_code = fields.Char(
        string='Código de Respuesta'
    )
    response_message = fields.Text(
        string='Mensaje de Respuesta'
    )
    authorization_code = fields.Char(
        string='Código de Autorización'
    )
    
    # Información adicional
    notes = fields.Text(
        string='Notas'
    )
    
    # Campos técnicos
    uuid = fields.Char(
        string='UUID',
        help='Identificador único del documento'
    )
    hash = fields.Char(
        string='Hash',
        help='Hash del documento para verificación'
    )
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('electronic.invoice')
        if not vals.get('uuid'):
            vals['uuid'] = str(uuid.uuid4())
        return super(ElectronicInvoice, self).create(vals)
    
    def generate_xml(self):
        """Genera el XML según los estándares del DGI"""
        self.ensure_one()
        
        # Obtener configuración DGI
        dgi_config = self.env['dgi.config'].get_dgi_config()
        if not dgi_config:
            raise UserError(_('No se encontró configuración DGI. Configure primero los datos de la empresa.'))
        
        # Crear estructura XML
        root = ET.Element('FacturaElectronica')
        root.set('xmlns', 'http://www.dgi.gob.pa/')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:schemaLocation', 'http://www.dgi.gob.pa/ factura_electronica.xsd')
        
        # Información del emisor
        emisor = ET.SubElement(root, 'Emisor')
        ET.SubElement(emisor, 'RUC').text = dgi_config.ruc
        ET.SubElement(emisor, 'DV').text = dgi_config.dv
        ET.SubElement(emisor, 'RazonSocial').text = dgi_config.company_name
        ET.SubElement(emisor, 'NombreComercial').text = dgi_config.commercial_name or ''
        ET.SubElement(emisor, 'Direccion').text = dgi_config.address
        ET.SubElement(emisor, 'Telefono').text = dgi_config.phone or ''
        ET.SubElement(emisor, 'Email').text = dgi_config.email or ''
        
        # Información del receptor
        receptor = ET.SubElement(root, 'Receptor')
        ET.SubElement(receptor, 'RUC').text = self.partner_id.ruc or self.partner_id.vat or ''
        ET.SubElement(receptor, 'DV').text = self.partner_id.dv or ''
        ET.SubElement(receptor, 'RazonSocial').text = self.partner_id.name
        ET.SubElement(receptor, 'Direccion').text = self.partner_id.street or ''
        ET.SubElement(receptor, 'Telefono').text = self.partner_id.phone or ''
        ET.SubElement(receptor, 'Email').text = self.partner_id.email or ''
        
        # Información del documento
        documento = ET.SubElement(root, 'Documento')
        ET.SubElement(documento, 'TipoDocumento').text = self.document_type
        ET.SubElement(documento, 'Numero').text = self.name
        ET.SubElement(documento, 'FechaEmision').text = self.invoice_date.strftime('%Y-%m-%d')
        ET.SubElement(documento, 'FechaVencimiento').text = self.due_date.strftime('%Y-%m-%d') if self.due_date else ''
        ET.SubElement(documento, 'Moneda').text = self.currency_id.name
        ET.SubElement(documento, 'TipoCambio').text = '1.00'  # Asumir 1:1 para PAB
        
        # Líneas de factura
        lineas = ET.SubElement(root, 'Lineas')
        for line in self.move_id.invoice_line_ids:
            linea = ET.SubElement(lineas, 'Linea')
            ET.SubElement(linea, 'NumeroLinea').text = str(line.sequence)
            ET.SubElement(linea, 'CodigoProducto').text = line.product_id.default_code or ''
            ET.SubElement(linea, 'Descripcion').text = line.name
            ET.SubElement(linea, 'Cantidad').text = str(line.quantity)
            ET.SubElement(linea, 'PrecioUnitario').text = str(line.price_unit)
            ET.SubElement(linea, 'Descuento').text = str(line.discount)
            ET.SubElement(linea, 'Subtotal').text = str(line.price_subtotal)
            
            # Impuestos de la línea
            impuestos_linea = ET.SubElement(linea, 'Impuestos')
            for tax in line.invoice_line_tax_ids:
                impuesto = ET.SubElement(impuestos_linea, 'Impuesto')
                ET.SubElement(impuesto, 'CodigoImpuesto').text = 'ITBMS'
                ET.SubElement(impuesto, 'TasaImpuesto').text = str(tax.amount)
                ET.SubElement(impuesto, 'MontoImpuesto').text = str(line.price_subtotal * tax.amount / 100)
        
        # Totales
        totales = ET.SubElement(root, 'Totales')
        ET.SubElement(totales, 'Subtotal').text = str(self.amount_untaxed)
        ET.SubElement(totales, 'TotalImpuestos').text = str(self.amount_tax)
        ET.SubElement(totales, 'Total').text = str(self.amount_total)
        
        # Convertir a string
        xml_string = ET.tostring(root, encoding='unicode')
        
        # Guardar XML
        self.xml_request = base64.b64encode(xml_string.encode('utf-8'))
        self.xml_filename = 'factura_%s.xml' % self.name
        
        # Generar hash
        self.hash = hashlib.sha256(xml_string.encode('utf-8')).hexdigest()
        
        return xml_string
    
    def send_to_dgi(self):
        """Envía la factura al DGI a través del PAC"""
        self.ensure_one()
        
        if not self.xml_request:
            self.generate_xml()
        
        # Aquí implementarías la lógica de envío al PAC
        # Por ahora simulamos el envío
        self.state = 'sent'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Factura Enviada'),
                'message': _('La factura %s ha sido enviada al DGI.') % self.name,
                'type': 'success',
            }
        }
    
    def check_status(self):
        """Verifica el estado de la factura en el DGI"""
        self.ensure_one()
        
        # Aquí implementarías la consulta de estado al PAC
        # Por ahora simulamos la respuesta
        if self.state == 'sent':
            self.state = 'authorized'
            self.authorization_date = fields.Datetime.now()
            self.authorization_code = 'AUTH' + str(uuid.uuid4())[:8].upper()
            self.response_code = '00'
            self.response_message = 'Documento autorizado exitosamente'
    
    def cancel_invoice(self):
        """Cancela la factura electrónica"""
        self.ensure_one()
        
        if self.state not in ['draft', 'sent']:
            raise UserError(_('Solo se pueden cancelar facturas en estado Borrador o Enviado.'))
        
        self.state = 'cancelled'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Factura Cancelada'),
                'message': _('La factura %s ha sido cancelada.') % self.name,
                'type': 'warning',
            }
        }
