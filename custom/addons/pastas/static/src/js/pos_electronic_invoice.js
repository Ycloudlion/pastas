odoo.define('pastas.pos_electronic_invoice', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');

    class ElectronicInvoiceButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }

        async onClick() {
            const order = this.env.pos.get_order();
            if (!order) return;

            // Verificar si ya tiene factura electrónica
            if (order.electronic_invoice_id) {
                this.showNotification('Esta orden ya tiene una factura electrónica', 'warning');
                return;
            }

            // Crear factura electrónica
            try {
                const result = await this.rpc({
                    model: 'pos.order',
                    method: '_create_electronic_invoice_from_pos',
                    args: [order.id],
                });

                if (result) {
                    order.electronic_invoice_id = result.id;
                    order.is_electronic = true;
                    this.showNotification('Factura electrónica creada exitosamente', 'success');
                }
            } catch (error) {
                console.error('Error creating electronic invoice:', error);
                this.showNotification('Error al crear factura electrónica', 'danger');
            }
        }
    }

    ElectronicInvoiceButton.template = 'ElectronicInvoiceButton';
    Registries.Component.add(ElectronicInvoiceButton);

    return ElectronicInvoiceButton;
});
