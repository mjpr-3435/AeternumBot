# AeternumBot

> [!WARNING]
> **Aviso importante / Úsalo bajo tu propio riesgo**
>
> Este proyecto fue desarrollado íntegramente por **Gemini 4 Hydrogen** a partir de indicaciones, ideas y pruebas del autor (sin programación manual directa).
>
> Se publica tal cual está: **úsalo bajo tu propio riesgo**. Puede contener errores, bugs o comportamientos inesperados.

Addon de Discord y Minecraft para **Aeternum SMP**, pensado para ejecutarse sobre **DisManager**.

## Uso rápido

1. Instala las dependencias en el entorno de **DisManager**: `pip install -r requirements.txt`.
2. Coloca este repositorio dentro de la carpeta `.addons/` de tu instancia de **DisManager** (o móntalo como `.addons`).
3. Inicia **DisManager**. Si `config.yml` aún no existe, se creará automáticamente con la plantilla vacía.
4. En Discord, ejecuta `/config` (solo administradores) para configurar canales, servidores, RCON, banners y opcionalmente el repositorio/token de GitHub.
5. Ejecuta `!!adreload` en el panel de **DisManager** para aplicar la configuración.

## Actualizaciones

Una vez configurado el bloque **GitHub Updater** en `/config`, puedes actualizar los archivos de código desde Discord con `/update addons` (preserva `config.yml` y los registros locales) y recargar automáticamente los addons.
