# AeternumBot

Addon de Discord y Minecraft para **Aeternum SMP**, pensado para ejecutarse sobre **DisManager**.

## Uso rápido

1. Coloca este repositorio dentro de la carpeta `.addons/` de tu instancia de **DisManager** (o móntalo como `.addons`).
2. Inicia **DisManager**. Si `config.yml` aún no existe, se creará automáticamente con la plantilla vacía.
3. En Discord, ejecuta `/config` (solo administradores) para configurar canales, servidores, RCON, banners y opcionalmente el repositorio/token de GitHub.
4. Ejecuta `!!adreload` en el panel de **DisManager** para aplicar la configuración.

## Actualizaciones

Una vez configurado el bloque **GitHub Updater** en `/config`, puedes actualizar los archivos de código desde Discord con `/update addons` (preserva `config.yml` y los registros locales) y recargar automáticamente los addons.
