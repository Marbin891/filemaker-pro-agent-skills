# FileMaker Pro Agent Skills

<p align="center">
  <img src="assets/logo-512.png" alt="Logo del proyecto FileMaker Pro Agent Skills" width="128" height="128">
</p>

Conjunto modular de referencia, con prioridad local, para el desarrollo de
**Claris FileMaker** con **ChatGPT y Codex**. Cubre cálculos nativos, pasos de
guion, errores y API, junto con los dialectos de los complementos BaseElements,
MBS y bBox. Cada área es una Agent Skill independiente; una skill de
enrutamiento selecciona el conjunto mínimo útil y mantiene los catálogos
detallados fuera del contexto hasta que se necesitan.

El proyecto se distribuye en dos formatos:

- **Un plugin portátil** que contiene las cinco skills.
- **Cinco skills independientes** que pueden instalarse o cargarse por separado.

No se necesita ningún binario de complemento, clave de licencia ni conexión con
FileMaker para leer el material de referencia. Ejecutar una llamada `BE_`, `MBS`
o `bBox` sí requiere el complemento correspondiente en el entorno FileMaker de
destino.

[English](README.md) · [Seguridad](SECURITY.md) · [Contribución](CONTRIBUTING.md) ·
[Atribución](ATTRIBUTION.md) · [Límites de terceros](THIRD-PARTY.md)

## Propósito

El desarrollo en FileMaker abarca varios vocabularios: funciones de cálculo
nativas, pasos de guion, códigos de error, productos de servidor y complementos
opcionales. El conocimiento genérico de un modelo suele mezclar esos dialectos,
inventar firmas o aplicar un comportamiento al producto equivocado.

Este proyecto ofrece una alternativa acotada:

- catálogos locales con nombres, firmas, parámetros, versiones y datos de
  plataforma exactos;
- enrutamiento explícito entre FileMaker nativo y cada complemento;
- divulgación progresiva: una petición carga una skill y una referencia, no todo
  el corpus;
- herramientas de consulta deterministas y de solo lectura, sin acceso a red;
- paquetes reproducibles con manifiestos de integridad y avisos por paquete.

## Cobertura

| Área | Incluido |
|---|---|
| FileMaker nativo | **368 funciones de cálculo**, **216 pasos de guion** en 16 categorías, **292 códigos de error**, catálogo completo de tipos de campo |
| Referencias nativas | Arquitectura, patrones profesionales, compatibilidad, SQL, Data API, OData, FileMaker Go, WebDirect, HTTP/integraciones, ejemplos resueltos |
| BaseElements | **133 entradas** que cubren **129 funciones `BE_` únicas**, 11 entradas obsoletas/renombradas/retiradas, 10 constantes con nombre, 18 categorías |
| MBS | **7.859 funciones** en **245 componentes**, divididas en 20 grupos de consulta, con estado de plataforma y licencia |
| bBox | **87 funciones y pasos de guion** en 15 categorías: 39 con página propia del proveedor, 48 confirmadas con fuentes primarias del proveedor |
| Enrutamiento | Un orquestador, una matriz de rutas y casos de contrato deterministas |

Líneas base de los catálogos:

| Fuente | Línea base |
|---|---|
| Instantánea nativa de FileMaker | FileMaker 26.0.3, instantánea de origen revisada el 2026-10-02 |
| BaseElements | Complemento 5.1.0.6 |
| MBS | Complemento 16.4 |
| bBox | Complemento 1.06, build 1.06.7 |

Una coincidencia en el catálogo significa que la entrada existe en la
instantánea. No implica que la función se comporte igual en todas las versiones
de FileMaker o del complemento, ni constituye una prueba del motor. Véase
[compatibilidad](filemaker-pro/references/compatibility.md) y
[resultados de pruebas](docs/TEST-RESULTS.md).

## Skills

| Skill | Responsabilidad | Señales de ejemplo |
|---|---|---|
| `filemaker-pro` | Funciones, pasos, errores, esquema, arquitectura, API, comportamiento de producto y seguridad nativos | Cálculo FileMaker, paso de guion, Data API, OData, WebDirect, FileMaker Go, ExecuteSQL |
| `goya-be-plugin` | Funciones, constantes y patrones operativos de BaseElements | `BE_HTTP_POST`, BaseElements, `BE_` |
| `monkeybread-mbs-plugin` | Componentes, firmas, plataforma y licencias de MBS | `MBS( ... )`, Monkeybread, DynaPDF, LibXL, Saxon |
| `beezwax-bbox-plugin` | Funciones, pasos, mode flags e integración con shell y lenguajes de bBox | `bBox_Shell`, `bBox_Zsh`, Beezwax |
| `fmp-dev-orchestrator` | Selecciona y combina las skills propietarias; no duplica catálogos | “¿Qué skill corresponde?”, peticiones mixtas nativas/complemento |

### Compatibilidad

- **ChatGPT:** skills y plugins, sujetos al plan del espacio de trabajo, al rol y
  a los controles del administrador. Las skills independientes se cargan una a
  una; el paquete con varias skills es un plugin.
- **Codex:** skills de usuario y de proyecto en las ubicaciones documentadas
  `.agents/skills`; el plugin también puede instalarse mediante un marketplace
  local.
- **Python:** las herramientas requieren Python 3.10 o posterior. Las
  referencias Markdown y JSON pueden leerse sin Python.
- **FileMaker:** la guía nativa cubre Pro, Go, WebDirect, Server, Cloud, Data API
  y CWP cuando los catálogos registran soporte. `Partial` es una limitación, no
  un sinónimo de `Yes`.
- **BaseElements:** línea base documentada 5.1.0.6. El soporte de plataforma es
  por función; el complemento debe estar instalado y permitido por el archivo o
  el servidor.
- **MBS:** línea base documentada 16.4. Algunas funciones requieren licencia base
  de pago; DynaPDF, XL y Saxon requieren licencias adicionales separadas.
- **bBox:** línea base documentada 1.06.7. bBox funciona en macOS y Ubuntu, no en
  Windows.

## Instalación

### ChatGPT: skills individuales

1. Abra un espacio de trabajo de ChatGPT con permisos de skills o plugins.
2. Abra el área de skills (**Plugins → Skills** en el directorio de plugins
   actual, o **Skills** en la aplicación de escritorio).
3. Elija **Create** o **Upload from your computer**.
4. Cargue un archivo de `dist/skills/`:
   - `filemaker-pro.zip`
   - `goya-be-plugin.zip`
   - `monkeybread-mbs-plugin.zip`
   - `beezwax-bbox-plugin.zip`
   - `fmp-dev-orchestrator.zip`
5. Espere a que termine el análisis del espacio de trabajo y resuelva cualquier
   hallazgo de revisión.

Cada archivo tiene **una carpeta de skill de nivel superior** y un `SKILL.md`.
No cargue el repositorio, `dist/plugin.zip` ni una instantánea del código fuente
de GitHub como skill individual.

### ChatGPT: el plugin

Use `dist/plugin.zip` para distribuir el plugin. Su raíz contiene `plugin.json` y
un directorio `skills/`; no es un archivo de una sola skill.

- **Directorio público:** cargue el ZIP en el portal de envío de plugins de
  OpenAI, resuelva los hallazgos automáticos y envíelo a revisión.
- **Prueba local:** instale el plugin en un marketplace personal o de
  repositorio, reinicie la aplicación de escritorio y instálelo desde el
  directorio de plugins.

```sh
# Marketplace personal: ~/.codex/plugins + ~/.agents/plugins/marketplace.json
python3 scripts/install_codex.py --scope user --plugin --register-marketplace

# Marketplace de repositorio: <project>/plugins + <project>/.agents/plugins/marketplace.json
python3 scripts/install_codex.py --scope project --project /absolute/path/to/project --plugin --register-marketplace
```

Referencias oficiales: [Build skills](https://developers.openai.com/plugins/build/skills),
[Package a plugin](https://developers.openai.com/plugins/build/plugins),
[Submit a plugin](https://developers.openai.com/plugins/deploy/submission).

### Codex: skills individuales

```sh
# Las cinco skills para el usuario actual
python3 scripts/install_codex.py --scope user --all

# Una sola skill
python3 scripts/install_codex.py --scope user --skill goya-be-plugin

# Un proyecto existente concreto
python3 scripts/install_codex.py --scope project --project /absolute/path/to/project --all
```

Windows PowerShell:

```powershell
py -3 scripts/install_codex.py --scope user --all
py -3 scripts/install_codex.py --scope project --project 'C:\work\my-project' --all
```

Destinos:

- usuario: `$HOME/.agents/skills/<nombre-de-skill>`
- proyecto: `<project>/.agents/skills/<nombre-de-skill>`

El instalador usa una lista explícita de archivos, prepara la copia fuera del
directorio de descubrimiento, la promueve solo cuando está completa y rechaza
sobrescribir una skill existente o seguir un enlace simbólico. Nunca elimina una
instalación anterior.

### Codex: el plugin

```sh
python3 scripts/install_codex.py --scope user --plugin --register-marketplace
```

Copia el plugin en `~/.codex/plugins/filemaker-pro-agent-skills` y añade una
entrada local a `~/.agents/plugins/marketplace.json`. Reinicie la aplicación
después de instalar. El plugin contiene varias skills; las skills individuales
siguen disponibles con los comandos anteriores.

### Instalación manual

- Skill individual: extraiga `dist/skills/<nombre>.zip` en un directorio
  documentado `.agents/skills/`. Conserve la única carpeta de nivel superior.
- Plugin: extraiga `dist/plugin.zip` en un directorio de plugins de marketplace y
  apunte la entrada del marketplace a esa carpeta.
- Verifique las descargas con `dist/SHA256SUMS` y `dist/manifest.json`.

Codex detecta los cambios de skills automáticamente. Invoque una skill de forma
explícita con `$nombre-de-skill` o mediante `/skills`. La activación implícita
depende del host y del modelo.

## Ejemplos

### FileMaker nativo

> Usa `filemaker-pro` para revisar este guion de FileMaker 19.6.1 Server.
> Conserva los nombres de tabla y campo proporcionados, revisa el tratamiento de
> errores e identifica los pasos incompatibles con Server.

> En FileMaker 26.0.3, construye un parámetro JSON tipado sin acceder a una
> solución activa. Muestra el cálculo y un procedimiento de verificación.

> Compara el soporte en Go y WebDirect de `Go to Layout`. Trata `Partial` como
> una limitación y cita la entrada del catálogo.

### Funciones de complementos

> Usa `goya-be-plugin` para consultar `BE_HTTP_POST`, muestra sus parámetros y la
> señal de error que debo comprobar después de la llamada.

> Usa `monkeybread-mbs-plugin` para encontrar una función MBS que lea un archivo
> de texto y indica su plataforma y requisitos de licencia.

> Usa `beezwax-bbox-plugin` para explicar los mode flags de `bBox_Zsh` y si la
> función es adecuada para Perform Script on Server.

### Petición mixta

> Usa `fmp-dev-orchestrator`. Escribe un guion de FileMaker que lea un archivo
> con bBox, lo valide y termine con un resultado JSON. Carga solo las skills
> necesarias.

### Consulta local

```sh
# Nativo
python3 filemaker-pro/scripts/catalog.py function JSONSetElement --version 16
python3 filemaker-pro/scripts/catalog.py step 'Open Transaction' --version 19.6.1 --platform Server
python3 filemaker-pro/scripts/catalog.py error 401

# Complementos
python3 goya-be-plugin/scripts/catalog.py function BE_HTTP_POST
python3 monkeybread-mbs-plugin/scripts/catalog.py function "Dialog.SetMessage"
python3 beezwax-bbox-plugin/scripts/catalog.py function bBox_Shell

# Enrutamiento
python3 fmp-dev-orchestrator/scripts/route.py route "Why does bBox_Zsh fail in a server script?"
```

Las herramientas instaladas de consulta y enrutamiento son de solo lectura, usan la biblioteca estándar de
Python y no realizan peticiones de red.

## Arquitectura

### Identidad del proyecto

El logo del proyecto es distinto de las marcas de los proveedores.
`assets/logo.png` es el PNG maestro; las variantes transparentes de 512 y 128 px,
remuestreadas con Lanczos, se usan para el listado, GitHub y el compositor. Solo
esos dos PNG optimizados se incluyen en el plugin; las skills individuales no
dependen de los recursos gráficos del plugin.

Regeneración y avisos de la imagen: [assets/README.md](assets/README.md).

```text
filemaker-pro-agent-skills/
├── plugin.json                 # manifiesto de plugin portátil
├── filemaker-pro/              # fuente canónica de cada skill
├── goya-be-plugin/
├── monkeybread-mbs-plugin/
├── beezwax-bbox-plugin/
├── fmp-dev-orchestrator/
├── scripts/                    # importación, validación, build, instalación, auditoría
├── tests/
├── docs/
└── dist/
    ├── skills/<nombre>.zip     # archivos de una sola skill
    ├── plugin.zip              # archivo de plugin con varias skills
    ├── manifest.json
    └── SHA256SUMS
```

El repositorio mantiene cada skill en su propio directorio de nivel superior para
editarla e instalarla de forma independiente. El constructor crea la estructura
del plugin al empaquetar: `plugin.json`, avisos y `skills/<nombre-de-skill>/...`.

### Divulgación progresiva

1. El host lee el `name` y la `description` de cada skill.
2. Carga un `SKILL.md` cuando la petición coincide.
3. La skill carga una referencia concreta solo cuando hace falta.
4. Los catálogos grandes exponen primero un índice:
   - MBS resuelve un componente mediante `references/index.json` y después lee un
     solo grupo;
   - BaseElements y bBox cargan una categoría o una entrada;
   - FileMaker nativo usa la herramienta de consulta y la guía correspondiente.

El orquestador no contiene ningún catálogo de funciones. Enruta y delega, de modo
que las firmas y las referencias del proveedor no se duplican entre skills.

### Política de catálogos

Los catálogos conservan metadatos factuales de API y síntesis de CadenceUX bajo
CC BY 4.0: nombres, firmas, nombres y flags de parámetros, resultados, versiones,
soporte de plataforma, estado de licencia y URL de origen. No se redistribuyen
la prosa ni los ejemplos del proveedor. Cada entrada enlaza a la página
autoritativa. Los ejemplos originales de este proyecto se identifican como tales.
Véase [THIRD-PARTY.md](THIRD-PARTY.md) para el límite detallado.

### Evidencia

Las respuestas deben distinguir:

- **catalog-checked** — coincidencia con una entrada local;
- **documentation-checked** — comprobación de la página enlazada del proveedor o
  de Claris;
- **engine syntax-validated** — analizado por un motor FileMaker;
- **engine-evaluated** — evaluado por un motor FileMaker;
- **written and read back** — aplicado y verificado en una solución.

Una consulta al catálogo o una prueba en Python no es una prueba del motor.

## Validación y limitaciones

La consulta de catálogos, instalación y construcción de paquetes solo necesitan
la biblioteca estándar de Python. La regeneración de imágenes y la validación
completa de desarrollo usan además las herramientas fijadas en
`requirements-dev.txt`:

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/generate_assets.py --check
```

```sh
python3 scripts/validate.py
python3 scripts/import_plugin_catalogs.py ../sources   # mantenedores; clones revisados
python3 scripts/verify_provenance.py ../sources
python3 scripts/verify_plugin_provenance.py ../sources
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 scripts/lint_examples.py
python3 scripts/audit.py
```

La suite automática comprueba la integridad de los catálogos, las consultas de
los complementos, los contratos de enrutamiento, la independencia de las skills,
la estructura de los paquetes, los avisos y propiedades estáticas acotadas de
seguridad. No ejecuta un motor FileMaker, un complemento real, el análisis de un
espacio de trabajo de ChatGPT ni una sesión de modelo de Codex.

Límites conocidos:

- las instantáneas de catálogo envejecen; versiones nuevas de FileMaker o de los
  complementos pueden añadir funciones;
- las matrices de plataforma pueden cambiar entre versiones de parche;
- el enrutamiento implícito depende del host y del modelo;
- los complementos, las licencias adicionales y FileMaker son instalaciones
  separadas;
- las páginas del proveedor, no este proyecto, son la autoridad sobre el
  comportamiento del proveedor.

Véanse [resultados de pruebas](docs/TEST-RESULTS.md), [seguridad](SECURITY.md),
[notas de investigación](docs/RESEARCH.md) y
[estado de la versión](docs/RELEASE-STATUS.md).

## Actualizaciones y contribuciones

El procedimiento de actualización está en [docs/UPDATING.md](docs/UPDATING.md).
Los commits de origen están fijados y se comprueban antes de importar. Los
cambios de catálogo deben actualizar a la vez los recuentos esperados, los
registros de procedencia, las pruebas y los paquetes.

Las contribuciones son bienvenidas mediante issues o pull requests. Lea
[CONTRIBUTING.md](CONTRIBUTING.md) y [SECURITY.md](SECURITY.md). No incluya
credenciales, datos de clientes, binarios de proveedores ni copias de
documentación sin licencia.

## Licencias y atribución

- Texto original del proyecto, lógica de enrutamiento, herramientas de consulta y
  ejemplos originales: **CC BY 4.0**.
- Material de CadenceUX: **CC BY 4.0**, obra original de Darrin Southern /
  CadenceUX. Los commits exactos se registran en [ATTRIBUTION.md](ATTRIBUTION.md)
  y en `references/provenance.json` de cada skill.
- Material de Claris, Goya, Monkeybread y Beezwax: este proyecto no lo
  relicencia. Se conservan metadatos factuales de API; no se incluyen prosa,
  ejemplos, binarios ni claves de licencia de los proveedores. Véase
  [THIRD-PARTY.md](THIRD-PARTY.md).

Esta es una adaptación independiente. No está afiliada ni respaldada por
CadenceUX, Claris, Goya, Monkeybread Software, Beezwax u OpenAI. Los nombres de
producto se usan únicamente para identificar interoperabilidad.
