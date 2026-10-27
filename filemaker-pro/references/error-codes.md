# FileMaker: consulta local de errores

`error-codes.json` contiene **292 códigos individuales**, ordenados numéricamente, con resúmenes diagnósticos originales en inglés. Incluye −1 y 0; no rellena huecos de numeración. La cobertura procede del inventario upstream, que declara FileMaker 26; comprueba disponibilidad y significado en la ayuda de tu versión. No se ha probado contra el motor ni contrastado independientemente con la página oficial actual.

## Buscar sin conexión

Desde este directorio, con `jq` instalado:

```sh
jq --argjson code 401 '.errors[] | select(.code == $code)' error-codes.json
jq '.errors | length' error-codes.json
```

Cada entrada tiene `code` entero y `summary` breve. Un código ausente no equivale a éxito: conserva el valor original y consulta documentación de la versión, producto o plug-in que lo emitió. Los resúmenes identifican la condición; no garantizan su causa ni una reparación concreta.

## Capturar el resultado correcto

Captura `Get ( LastError )` **inmediatamente después del paso que quieres comprobar**, antes de ejecutar otros pasos que puedan cambiarlo:

```text
Set Error Capture [ On ]
Perform Find [ Restore ]
Set Variable [ $findError ; Value: Get ( LastError ) ]
If [ $findError = 401 ]
    # Decidir cómo presentar un resultado sin coincidencias.
Else If [ $findError ≠ 0 ]
    # Registrar el fallo y aplicar la política de la solución.
End If
```

`Set Error Capture [ On ]` permite gestionar errores sin los diálogos habituales; no convierte un fallo en éxito. Interpreta cada resultado según el paso ejecutado: 401 puede ser una búsqueda válida sin resultados, 1 una cancelación del usuario y 301 un bloqueo de registro. No reintentes indiscriminadamente operaciones con efectos secundarios.

Para diagnóstico, registra código, paso, versión, cliente, archivo, layout/ocurrencia de tabla y contexto de privilegios. Añade detalles extendidos cuando el paso los proporcione, sin guardar contraseñas, tokens ni datos sensibles. Las familias de códigos no garantizan que todos sus miembros puedan aparecer en todos los clientes o APIs.

## Rangos sin entradas individuales

- **1552–1559:** resultados definidos por plug-ins. La fuente los agrupa; no define ocho diagnósticos distintos. Consulta al proveedor y conserva el código exacto.
- **5000–5499:** resultados personalizados que puede devolver `Revert Transaction`. Su significado lo define la solución, no esta referencia. Mantén un registro local de asignaciones.

Ninguno de estos rangos se expande en `errors`; tampoco se representa un rango como si fuera un código individual. Los 292 registros corresponden a los códigos concretos enumerados por upstream, no a todos los enteros de sus rangos.

## Cálculos y SQL

`ExecuteSQL` devuelve `?` cuando falla; no interpretes ese texto como un código numérico de este archivo ni supongas que `Get ( LastError )` explica el cálculo. En versiones que lo incluyan, `ExecuteSQLe` proporciona información diagnóstica adicional, incluidos identificadores SQL como `FQL…`, que pertenecen a otra referencia. Para expresiones evaluadas con `Evaluate`, utiliza `EvaluationError` según su documentación.

Al investigar SQL, revisa nombres de ocurrencias de tabla y campos, comillas de identificadores, parámetros y tipos. Un `?` aislado no identifica por sí solo cuál de esas condiciones ocurrió.

## APIs, HTTP y transporte

Separa tres resultados: el error del paso FileMaker, el estado HTTP de la respuesta y los mensajes de la API. Por ejemplo, HTTP 404 no significa el error FileMaker 404: son espacios de códigos distintos. Una conexión completada puede devolver una respuesta HTTP o un mensaje de API de fallo.

Con `Insert From URL`, captura primero `Get ( LastError )` y recoge explícitamente las cabeceras/estado HTTP mediante las opciones compatibles. No busques una línea HTTP dentro del cuerpo suponiendo que siempre estará allí. Examina el cuerpo según el contrato de la API; en Data API, comprueba también `messages[].code` y `messages[].message`. No basta buscar la palabra `error` ni equiparar HTTP 200 con éxito funcional.

## Procedencia, atribución y adaptación

- Inventario adaptado de [CadenceUX / Darrin Southern, `claris-filemaker-pro-skill`](https://github.com/CadenceUX/claris-filemaker-pro-skill/blob/bda594e15f4a6981e93403c4b187d262ca820116/references/error-codes.md), commit **bda594e15f4a6981e93403c4b187d262ca820116**, archivo local `sources/claris-filemaker-pro-skill/references/error-codes.md`.
- El proyecto upstream declara [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Se reconoce su autoría del material de partida; esta adaptación conserva el inventario numérico, reescribe los diagnósticos y sustituye las instrucciones y ejemplos.
- Fuente técnica oficial: [Claris FileMaker Pro Help — Error codes](https://help.claris.com/en/pro-help/content/error-codes.html). La licencia del proyecto upstream no implica autorización sobre la documentación de Claris. No se reproduce la tabla oficial ni sus descripciones completas.
- **Independently written diagnostic summaries; not the official Claris wording.** La redacción adaptada no constituye autoría de los códigos ni respaldo de Claris, CadenceUX o Darrin Southern.
