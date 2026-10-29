# Plan: Nuevo flujo pedidos - Salesforce System API

## Contexto

Se necesita un nuevo flujo independiente para recibir peticiones en el endpoint `/salesforce/sys/v1/pedidos`. Este endpoint **no** está gestionado por APIKit ni RAML — es un listener HTTP independiente. El flujo debe registrar el XML entrante, pasar por un Transform Message vacío (placeholder), y registrar el JSON resultante.

---

## Archivos afectados

| Acción | Archivo |
|--------|---------|
| **Crear** | `src/main/mule/pedidos-flow.xml` |
| Sin cambios | `src/main/mule/api-cert-level-2.xml` |
| Sin cambios | `src/main/mule/api-cert-level-2-v1.xml` |
| Sin cambios | `src/main/mule/business-partner-service.xml` |
| Sin cambios | `src/main/resources/api/` (ningún RAML) |
| Sin cambios | `pom.xml` |

---

## Estructura del flujo

```
POST /salesforce/sys/v1/pedidos
        │
        ▼
[1] http:listener
    config-ref="api-cert-level-2-httpListenerConfig"
    path="/salesforce/sys/v1/pedidos"
    allowedMethods="POST"
        │
        ▼
[2] logger  ──► INFO · "Log XML payload" · message="#[payload]"
        │
        ▼
[3] ee:transform  ──► "Transform Message" (body vacío — placeholder)
        │
        ▼
[4] logger  ──► INFO · "Log JSON payload" · message='#[%dw 2.0 output application/json --- payload]'
```

---

## Implementación

### Archivo: `src/main/mule/pedidos-flow.xml`

El archivo reutiliza la configuración HTTP existente `api-cert-level-2-httpListenerConfig` (puerto 8081, host 0.0.0.0), definida en `api-cert-level-2.xml`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mule xmlns="http://www.mulesoft.org/schema/mule/core"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:http="http://www.mulesoft.org/schema/mule/http"
      xmlns:ee="http://www.mulesoft.org/schema/mule/ee/core"
      xmlns:doc="http://www.mulesoft.org/schema/mule/documentation"
      xsi:schemaLocation="
        http://www.mulesoft.org/schema/mule/core
          http://www.mulesoft.org/schema/mule/core/current/mule.xsd
        http://www.mulesoft.org/schema/mule/http
          http://www.mulesoft.org/schema/mule/http/current/mule-http.xsd
        http://www.mulesoft.org/schema/mule/ee/core
          http://www.mulesoft.org/schema/mule/ee/core/current/mule-ee.xsd">

    <flow name="pedidos-flow">

        <!-- 1. Listener HTTP independiente — sin APIKit, sin RAML -->
        <http:listener
            config-ref="api-cert-level-2-httpListenerConfig"
            path="/salesforce/sys/v1/pedidos"
            allowedMethods="POST" />

        <!-- 2. Log XML entrante -->
        <logger
            level="INFO"
            doc:name="Log XML payload"
            message="#[payload]" />

        <!-- 3. Transform Message vacío (placeholder para lógica futura) -->
        <ee:transform doc:name="Transform Message">
            <ee:message>
                <ee:set-payload><![CDATA[%dw 2.0
output application/json
---
{}]]></ee:set-payload>
            </ee:message>
        </ee:transform>

        <!-- 4. Log JSON final -->
        <logger
            level="INFO"
            doc:name="Log JSON payload"
            message='#[%dw 2.0
output application/json
---
payload]' />

    </flow>

</mule>
```

---

## Decisiones de diseño

- **Reutilizar `api-cert-level-2-httpListenerConfig`**: ya existe en `api-cert-level-2.xml`; no se necesita una segunda config HTTP. Todos los flujos del proyecto comparten el mismo listener en puerto 8081.
- **Archivo separado `pedidos-flow.xml`**: mantiene el flujo aislado de los flujos de la API REST/commodities y del flujo SOAP de business-partner. Facilita su mantenimiento y evolución independiente.
- **Sin APIKit**: el listener apunta directamente al flujo; no pasa por ningún router RAML. Esto permite activarlo sin modificar ninguna especificación existente.
- **Transform Message vacío `{}`**: produce un JSON vacío en `application/json`. Sirve como placeholder para la lógica de transformación que se implementará en iteraciones futuras.
- **Método `POST`**: alineado con el patrón del resto de flujos de integración del proyecto (clientes-flow). Puede ampliarse a otros métodos cuando se defina el contrato.

---

## Verificación

1. Iniciar la aplicación Mule localmente (puerto 8081).
2. Enviar un `POST` a `http://localhost:8081/salesforce/sys/v1/pedidos` con cuerpo XML (p.ej. con Postman).
3. Revisar los logs y confirmar:
   - Primera entrada de log: payload XML recibido.
   - Segunda entrada de log: `{}` en `application/json`.
4. Confirmar que los flujos existentes siguen funcionando sin cambios:
   - `GET /api/v1/commodities`
   - `POST /soap/BusinessPartnerService/SuiteReplicateRequest`
