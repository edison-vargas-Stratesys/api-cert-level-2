# Plan: Nuevo flujo clientes - BusinessPartnerService

## Context
Se necesita un nuevo flujo independiente para recibir peticiones SOAP del servicio `BusinessPartnerService`. Este endpoint **no** está gestionado por APIKit ni RAML — es un listener HTTP independiente. El flujo debe registrar el XML entrante (sin saltos de línea), pasar por un Transform Message vacío (placeholder), y registrar el JSON resultante (sin saltos de línea).

---

## Archivos afectados

| Acción | Archivo |
|--------|---------|
| **Creado** | `src/main/mule/business-partner-service.xml` |
| Sin cambios | `src/main/mule/api-cert-level-2.xml` |
| Sin cambios | `src/main/mule/api-cert-level-2-v1.xml` |
| Sin cambios | `src/main/resources/api/` (ningún RAML) |

---

## Implementación

### Archivo: `src/main/mule/business-partner-service.xml`

El archivo reutiliza la configuración HTTP existente `api-cert-level-2-httpListenerConfig` (puerto 8081, host 0.0.0.0).

**Estructura del flujo `clientes-flow`:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mule xmlns="http://www.mulesoft.org/schema/mule/core"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:http="http://www.mulesoft.org/schema/mule/http"
      xmlns:ee="http://www.mulesoft.org/schema/mule/ee/core"
      xsi:schemaLocation="
        http://www.mulesoft.org/schema/mule/core
          http://www.mulesoft.org/schema/mule/core/current/mule.xsd
        http://www.mulesoft.org/schema/mule/http
          http://www.mulesoft.org/schema/mule/http/current/mule-http.xsd
        http://www.mulesoft.org/schema/mule/ee/core
          http://www.mulesoft.org/schema/mule/ee/core/current/mule-ee.xsd">

    <flow name="clientes-flow">

        <!-- 1. Listener SOAP — sin APIKit, sin RAML -->
        <http:listener
            config-ref="api-cert-level-2-httpListenerConfig"
            path="/soap/BusinessPartnerService/SuiteReplicateRequest"
            allowedMethods="POST" />

        <!-- 2. Log XML entrante sin saltos de línea -->
        <logger
            level="INFO"
            doc:name="Log XML payload"
            message="#[write(payload, 'application/xml') replace /(\r\n|\r|\n)/ with '']" />

        <!-- 3. Transform Message vacío (placeholder) -->
        <ee:transform doc:name="Transform Message">
            <ee:message>
                <ee:set-payload><![CDATA[%dw 2.0
output application/json
---
{}]]></ee:set-payload>
            </ee:message>
        </ee:transform>

        <!-- 4. Log JSON final sin saltos de línea -->
        <logger
            level="INFO"
            doc:name="Log JSON payload"
            message="#[write(payload, 'application/json') replace /(\r\n|\r|\n)/ with '']" />

    </flow>

</mule>
```

---

## Decisiones de diseño

- **Reutilizar `api-cert-level-2-httpListenerConfig`**: ya existe en `api-cert-level-2.xml`; no se necesita una segunda config HTTP.
- **Archivo separado**: mantiene el flujo SOAP aislado de los flujos de la API REST/commodities.
- **Sin APIKit**: el listener apunta directamente al flujo, no pasa por ningún router RAML.
- **Transform vacío**: produce `{}` en `application/json` — sirve como placeholder para implementación futura.
- **Remoción de saltos de línea**: expresión DataWeave `replace /(\r\n|\r|\n)/ with ''` aplicada sobre `write(payload, ...)` para obtener una sola línea en el log.

---

## Verificación

1. Iniciar la aplicación Mule localmente (puerto 8081).
2. Enviar un POST a `http://localhost:8081/soap/BusinessPartnerService/SuiteReplicateRequest` con cuerpo XML (p.ej. con Postman o SoapUI).
3. Revisar los logs y confirmar:
   - Primera entrada: XML en una sola línea.
   - Segunda entrada: `{}` en una sola línea.
4. Confirmar que los flujos existentes (`/api/v1/*`, `/console/*`) siguen funcionando sin cambios.
