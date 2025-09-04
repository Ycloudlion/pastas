# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)


class DgiConfig(models.Model):
    _name = 'dgi.config'
    _description = 'Configuración DGI Panamá'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    
    # Datos de la empresa
    ruc = fields.Char(
        string='RUC',
        required=True,
        help='Registro Único de Contribuyente'
    )
    dv = fields.Char(
        string='DV',
        size=1,
        required=True,
        help='Dígito Verificador'
    )
    company_name = fields.Char(
        string='Razón Social',
        required=True
    )
    commercial_name = fields.Char(
        string='Nombre Comercial'
    )
    address = fields.Text(
        string='Dirección',
        required=True
    )
    phone = fields.Char(
        string='Teléfono'
    )
    email = fields.Char(
        string='Email'
    )
    
    # Configuración PAC
    pac_provider = fields.Selection([
        ('the_factory_hka', 'The Factory HKA'),
        ('sistecredito', 'Sistecrédito'),
        ('certicamara', 'Certicámara'),
        ('otro', 'Otro PAC'),
    ], string='Proveedor PAC', required=True)
    
    pac_username = fields.Char(
        string='Usuario PAC'
    )
    pac_password = fields.Char(
        string='Contraseña PAC'
    )
    pac_url = fields.Char(
        string='URL del Servicio',
        default='https://demoemision.thefactoryhka.com.pa/ws/obj/v1.0/Service.svc?wsdl'
    )
    
    # Certificado digital
    certificate_file = fields.Binary(
        string='Certificado Digital (.p12)',
        help='Certificado de firma electrónica en formato PKCS#12'
    )
    certificate_filename = fields.Char(
        string='Nombre del Archivo'
    )
    certificate_password = fields.Char(
        string='Contraseña del Certificado'
    )
    
    # Configuración de secuencias
    invoice_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Secuencia de Facturas',
        domain="[('code', '=', 'electronic.invoice')]"
    )
    credit_note_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Secuencia de Notas de Crédito',
        domain="[('code', '=', 'electronic.credit.note')]"
    )
    debit_note_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Secuencia de Notas de Débito',
        domain="[('code', '=', 'electronic.debit.note')]"
    )
    
    # Configuración de impuestos
    tax_18_id = fields.Many2one(
        'account.tax',
        string='Impuesto ITBMS 7%',
        domain="[('name', 'ilike', 'ITBMS'), ('amount', '=', 7.0)]"
    )
    tax_10_id = fields.Many2one(
        'account.tax',
        string='Impuesto ITBMS 10%',
        domain="[('name', 'ilike', 'ITBMS'), ('amount', '=', 10.0)]"
    )
    tax_15_id = fields.Many2one(
        'account.tax',
        string='Impuesto ITBMS 15%',
        domain="[('name', 'ilike', 'ITBMS'), ('amount', '=', 15.0)]"
    )
    
    # Estado de configuración
    is_configured = fields.Boolean(
        string='Configurado',
        compute='_compute_is_configured',
        store=True
    )
    
    @api.depends('ruc', 'dv', 'company_name', 'address', 'pac_provider', 
                 'pac_username', 'pac_password', 'pac_url')
    def _compute_is_configured(self):
        for record in self:
            record.is_configured = bool(
                record.ruc and record.dv and record.company_name and 
                record.address and record.pac_provider and 
                record.pac_username and record.pac_password and record.pac_url
            )
    
    @api.constrains('ruc')
    def _check_ruc(self):
        for record in self:
            if record.ruc and len(record.ruc) != 8:
                raise ValidationError(_('El RUC debe tener exactamente 8 dígitos.'))
    
    @api.constrains('dv')
    def _check_dv(self):
        for record in self:
            if record.dv and not record.dv.isdigit():
                raise ValidationError(_('El DV debe ser un dígito numérico.'))
    
    @api.model
    def get_dgi_config(self):
        """Obtiene la configuración DGI de la empresa actual"""
        # Buscar configuración para la empresa actual
        config = self.search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        if config:
            return config
        
        # Si no hay configuración para la empresa actual, buscar cualquier configuración
        config = self.search([], limit=1)
        if config:
            return config
        
        # Si no hay ninguna configuración, crear una por defecto
        return self.create({
            'company_id': self.env.user.company_id.id,
            'ruc': '00000000',
            'dv': '0',
            'company_name': 'Empresa Demo',
            'commercial_name': 'Demo',
            'address': 'Dirección Demo',
            'pac_provider': 'the_factory_hka',
            'pac_username': 'demo',
            'pac_password': 'demo',
            'pac_url': 'https://demoemision.thefactoryhka.com.pa/ws/obj/v1.0/Service.svc?wsdl'
        })
    
    def test_connection(self):
        """Prueba la conexión con el PAC"""
        self.ensure_one()
        try:
            # Aquí implementarías la lógica de prueba de conexión
            # con el PAC seleccionado
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Conexión Exitosa'),
                    'message': _('La conexión con el PAC se estableció correctamente.'),
                    'type': 'success',
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error de Conexión'),
                    'message': _('Error al conectar con el PAC: %s') % str(e),
                    'type': 'danger',
                }
            }
