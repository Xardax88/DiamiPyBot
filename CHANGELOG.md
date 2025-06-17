# Registro de Cambios

Toda la información relevante de los cambios entre versiones se documentará en este archivo.
El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto se adhiere al [Versionado Semántico](https://semver.org/spec/v2.0.0.html).



## [0.9.0-beta.1] - 2023-10-27

Esta es la primera pre-release pública de Diami Bot, marcando la finalización de la estructura base y las funcionalidades iniciales.

### Added
- **Arquitectura Base:** Estructura de proyecto con Cogs, Schemas y separación de lógica.
- **Comando `/help`:** Sistema de ayuda dinámico y paginado.
- **Comando `/config`:** Grupo de comandos para configurar el bot por servidor.
- **Sistema de Flags:** Posibilidad de activar/desactivar módulos.
- **Base de Datos:** Integración con MongoDB.
- **Comandos Generales:** `/ping`, `/confesion`, `/herejia` (con menú contextual).
- **Logs de Auditoría:** Registro de joins, leaves, y ediciones/borrados de mensajes.
- **Tareas Programadas:** Módulo de tareas con "Feliz Jueves".
- **Sistema de Reportes:** Comando `/report` para moderación.