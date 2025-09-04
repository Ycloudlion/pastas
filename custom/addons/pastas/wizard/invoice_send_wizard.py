# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class InvoiceSendWizard(models.TransientModel):
    _name = 'invoice.send.wizard'
    _description = 'Wizard para Envío de Facturas Electrónicas'

    move_ids = fields.Many2many(
        'account.move',
        string='Facturas',
        required=True
    )
    send_type = fields.Selection([
        ('individual', 'Envío Individual'),
        ('batch', 'Envío por Lotes'),
    ], string='Tipo de Envío', default='individual', required=True)
    test_mode = fields.Boolean(
        string='Modo de Prueba',
        default=True,
        help='Si está marcado, se enviará en modo de pruebas'
    )

    @api.model
    def default_get(self, fields_list):
        res = super(InvoiceSendWizard, self).default_get(fields_list)
        
        # Obtener facturas del contexto
        if self.env.context.get('active_model') == 'account.move':
            move_ids = self.env.context.get('active_ids', [])
            res['move_ids'] = [(6, 0, move_ids)]
        
        return res

    def action_send_invoices(self):
        """Envía las facturas electrónicas seleccionadas"""
        self.ensure_one()
        
        if not self.move_ids:
            raise UserError(_('No se seleccionaron facturas para enviar.'))
        
        # Verificar configuración DGI
        dgi_config = self.env['dgi.config'].get_dgi_config()
        if not dgi_config:
            raise UserError(_('No se encontró configuración DGI. Configure primero los datos de la empresa.'))
        
        success_count = 0
        error_count = 0
        errors = []
        
        for move in self.move_ids:
            try:
                if not move.electronic_invoice_id:
                    # Crear factura electrónica si no existe
                    electronic_invoice = self.env['electronic.invoice'].create({
                        'move_id': move.id,
                        'document_type': '01',  # Factura
                    })
                    move.electronic_invoice_id = electronic_invoice.id
                    move.is_electronic = True
                
                # Generar XML si no existe
                if not move.electronic_invoice_id.xml_request:
                    move.electronic_invoice_id.generate_xml()
                
                # Enviar al DGI
                move.electronic_invoice_id.send_to_dgi()
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(_('Factura %s: %s') % (move.name, str(e)))
                _logger.error('Error enviando factura %s: %s', move.name, str(e))
        
        # Mostrar resultado
        if error_count == 0:
            message = _('Se enviaron exitosamente %d facturas electrónicas.') % success_count
            message_type = 'success'
        elif success_count == 0:
            message = _('No se pudo enviar ninguna factura. Errores:\n%s') % '\n'.join(errors)
            message_type = 'danger'
        else:
            message = _('Se enviaron %d facturas exitosamente y %d fallaron.\nErrores:\n%s') % (
                success_count, error_count, '\n'.join(errors)
            )
            message_type = 'warning'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Resultado del Envío'),
                'message': message,
                'type': message_type,
            }
        }
    
    def action_check_status(self):
        """Verifica el estado de las facturas electrónicas seleccionadas"""
        self.ensure_one()
        
        if not self.move_ids:
            raise UserError(_('No se seleccionaron facturas para verificar.'))
        
        success_count = 0
        error_count = 0
        errors = []
        
        for move in self.move_ids:
            try:
                if not move.electronic_invoice_id:
                    errors.append(_('Factura %s: No tiene factura electrónica asociada.') % move.name)
                    error_count += 1
                    continue
                
                move.electronic_invoice_id.check_status()
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(_('Factura %s: %s') % (move.name, str(e)))
                _logger.error('Error verificando estado de factura %s: %s', move.name, str(e))
        
        # Mostrar resultado
        if error_count == 0:
            message = _('Se verificó el estado de %d facturas electrónicas.') % success_count
            message_type = 'success'
        elif success_count == 0:
            message = _('No se pudo verificar ninguna factura. Errores:\n%s') % '\n'.join(errors)
            message_type = 'danger'
        else:
            message = _('Se verificaron %d facturas exitosamente y %d fallaron.\nErrores:\n%s') % (
                success_count, error_count, '\n'.join(errors)
            )
            message_type = 'warning'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Resultado de la Verificación'),
                'message': message,
                'type': message_type,
            }
        }
