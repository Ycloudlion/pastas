# 📋 Módulo de Facturación Electrónica DGI Panamá

## 🚀 Instalación Rápida

### 1. Instalar el Módulo
1. Ve a **Aplicaciones** en Odoo
2. Busca **"Facturación Electrónica DGI Panamá"**
3. Haz clic en **Instalar**

### 2. Configurar Datos de la Empresa
1. Ve a **Contabilidad > Configuración > Configuración DGI**
2. Completa los datos de tu empresa:
   - **RUC:** 8 dígitos (ej: 12345678)
   - **DV:** 1 dígito (ej: 1)
   - **Razón Social:** Nombre legal de la empresa
   - **Dirección:** Dirección completa
   - **Teléfono:** +507 200-0000
   - **Email:** contabilidad@empresa.com

### 3. Configurar el PAC (Proveedor Autorizado Calificado)

#### Para The Factory HKA:
- **Proveedor PAC:** The Factory HKA
- **Ambiente:** Pruebas (recomendado para desarrollo)
- **Token Empresa:** [Tu token de empresa]
- **Token Password:** [Tu token de contraseña]
- **URL Producción:** https://emision.thefactoryhka.com.pa/ws/obj/v1.0/Service.svc?wsdl
- **URL Pruebas:** https://demoemision.thefactoryhka.com.pa/ws/obj/v1.0/Service.svc?wsdl

#### Para Otros PACs:
- **Sistecrédito:** Contacta para obtener URLs y credenciales
- **Certicámara:** Contacta para obtener URLs y credenciales

### 4. Verificar la Configuración
1. Haz clic en **"Probar Conexión"**
2. Si aparece ✅, la configuración está correcta

## 📊 Características del Módulo

### ✅ Funcionalidades Incluidas:
- **Facturas Electrónicas** desde Ventas
- **Facturas Electrónicas** desde Compras
- **Notas de Crédito** electrónicas
- **Notas de Débito** electrónicas
- **Envío automático** al DGI
- **Verificación de estado** de documentos
- **Reportes** de facturación electrónica

### 🔧 Configuración Automática:
- **Impuestos ITBMS:** 7%, 10%, 15%
- **Secuencias:** FE-, NCE-, NDE-
- **Cuentas contables** para ITBMS
- **Diarios contables** con facturación electrónica

## 🎯 Uso del Módulo

### Crear Factura Electrónica:
1. Ve a **Ventas > Facturas**
2. Crea una factura normal
3. Haz clic en **"Crear Factura Electrónica"**
4. Completa los datos requeridos
5. Haz clic en **"Enviar al DGI"**

### Verificar Estado:
1. En la factura electrónica
2. Haz clic en **"Verificar Estado"**
3. El sistema consultará el estado con el DGI

## ⚠️ Notas Importantes

### Para Pruebas:
- Usa **ambiente de Pruebas**
- Los documentos no son válidos fiscalmente
- Perfecto para desarrollo y testing

### Para Producción:
- Usa **ambiente de Producción**
- Requiere **certificado digital** del DGI
- Los documentos son válidos fiscalmente

## 🆘 Soporte

Si tienes problemas:
1. Verifica que todos los campos estén completos
2. Prueba la conexión con el PAC
3. Revisa los logs de Odoo
4. Contacta al soporte técnico

## 📞 Contacto

- **Email:** soporte@empresa.com
- **Teléfono:** +507 200-0000
- **Documentación:** [Enlace a documentación completa]