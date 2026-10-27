# FileMaker Pro Agent Skills

<p align="center">
  <img src="assets/logo-512.png" alt="Logo de FileMaker Pro Agent Skills" width="128" height="128">
</p>

**Agent Skills para desarrollar soluciones Claris FileMaker** con ChatGPT y Codex. Permiten consultar funciones, revisar guiones, comprobar compatibilidad y utilizar referencias nativas de FileMaker, BaseElements, MBS y bBox.

[English](README.md) · [Seguridad](SECURITY.md) · [Contribuir](CONTRIBUTING.md)

## Skills incluidas

| Skill | Función |
|---|---|
| `filemaker-pro` | Cálculos nativos, pasos de guion, errores, esquema, SQL y API |
| `goya-be-plugin` | Firmas, parámetros y compatibilidad de BaseElements (`BE_`) |
| `monkeybread-mbs-plugin` | Funciones MBS, componentes, licencias y plataformas |
| `beezwax-bbox-plugin` | Funciones bBox, pasos de guion e integración con el sistema |
| `fmp-dev-orchestrator` | Selecciona las skills necesarias para consultas mixtas |

**Cobertura:** 368 funciones nativas, 216 pasos de guion, 292 errores, 129 funciones únicas de BaseElements, 7.859 funciones MBS enumeradas y 87 funciones/pasos de bBox. Consulta las [versiones de referencia y limitaciones](docs/RELEASE-STATUS.md).

## Instalación

### ChatGPT

- **Plugin:** si FileMaker Pro Agent Skills aparece en el directorio de plugins de tu espacio de trabajo, selecciona **Instalar**. La disponibilidad depende del plan y de la configuración del espacio de trabajo.
- **Skills individuales:** descarga un ZIP desde [`dist/skills/`](dist/skills/) y súbelo desde la sección Skills de tu espacio de trabajo, si está habilitada. Sube **un ZIP por skill**; `dist/plugin.zip` no es una skill individual.

### Codex

Primero clona el repositorio (el instalador requiere Python 3.10 o posterior):

```sh
git clone https://github.com/Marbin891/filemaker-pro-agent-skills.git
cd filemaker-pro-agent-skills

# Instalar las cinco skills individuales
python3 scripts/install_codex.py --scope user --all
```

Como alternativa, instala el plugin completo en un marketplace local **en lugar** de las skills individuales:

```sh
python3 scripts/install_codex.py --scope user --plugin --register-marketplace
```

Consulta `python3 scripts/install_codex.py --help` para instalar por proyecto o una sola skill. La disponibilidad del marketplace y la activación automática dependen del cliente.

## Ejemplos

- «Revisa este guion FileMaker y detecta errores y problemas de compatibilidad con Server».
- «Muéstrame los parámetros de `BE_HTTP_POST` y cómo manejar sus errores».
- «Busca una función MBS para combinar PDF y explica sus licencias».
- «¿Funciona `bBox_Zsh` en Windows o FileMaker Server?».
- «Combina funciones JSON nativas y llamadas HTTP de BaseElements en un guion».

## Arquitectura

Cada skill tiene su propio catálogo; el orquestador selecciona únicamente las necesarias. Las referencias se cargan bajo demanda. Las herramientas Python de consulta son de solo lectura y funcionan sin conexión.

## Limitaciones

Son **referencias de desarrollo, no complementos binarios ni una conexión activa con FileMaker**. Ejecutar `BE_`, `MBS(...)` o `bBox_` requiere un complemento compatible y, en algunos casos, licencia. FileMaker Go no admite complementos externos.

Las pruebas de catálogo y Python no verifican el código generado en el motor FileMaker. Comprueba la versión y plataforma de destino y prueba en una copia segura. Consulta [pruebas](docs/TEST-RESULTS.md), [seguridad](SECURITY.md) y [limitaciones](docs/RELEASE-STATUS.md).

## Contribuir

Se aceptan correcciones y contribuciones. Las instrucciones de desarrollo y mantenimiento están en [CONTRIBUTING.md](CONTRIBUTING.md) y [docs/UPDATING.md](docs/UPDATING.md).

## Licencias y Atribución

El material original del proyecto y las adaptaciones de CadenceUX están bajo **CC BY 4.0**, con atribución a Darrin Southern / CadenceUX. Esto no concede licencia sobre material de Claris u otros proveedores ni sobre el logo. Consulta [LICENSE](LICENSE), [ATTRIBUTION.md](ATTRIBUTION.md), [THIRD-PARTY.md](THIRD-PARTY.md) y [notas del logo](assets/README.md).

Proyecto independiente, sin afiliación ni respaldo de Claris, Goya, Monkeybread Software, Beezwax, CadenceUX u OpenAI.
