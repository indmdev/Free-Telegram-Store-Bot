# Bot de Tienda Gratuita para Telegram

<!-- hy-mt2-i18n:start -->
[English](./README.md) | [中文](./README_zh-CN.md) | [日本語](./README_ja.md) | **Español**
<!-- hy-mt2-i18n:end -->


He hecho que este bot sea 100% gratuito.

> Envíame un mensaje a [@InDMDev](https://t.me/InDMDev) si deseas personalizaciones avanzadas para tu bot.
> Para conocer más bots como este y ser el primero en saber cuando publique bots más avanzados, únete a mi canal: [@InDMDevBots](https://t.me/InDMDevBots)
Bot de Telegram para vender productos digitales: · vender claves de licencia de software en Telegram · bot de tienda en Telegram · bot de pagos en criptomonedas · integración con CryptoBot · pago con tarjeta de Telegram Payments · entrega digital automática · bot de comercio electrónico en Python · tienda con python-telegram-bot · bot de Telegram con SQLAlchemy y SQLite · tienda online de bienes digitales autohospedada.
> 
# Tienda de Productos Digitales — Bot de Telegram

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20.7-26A5E4?logo=telegram&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/database-SQLite%20%7C%20PostgreSQL-003B57?logo=sqlite&logoColor=white)
![Plataforma](https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20macOS-555)
[![Licencia: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Un bot de Telegram para vender productos digitales (claves de licencia de software y archivos descargables).  
Los clientes exploran un catálogo, cargan dinero en una billetera interna con criptomonedas o tarjeta, y utilizan ese saldo para comprar productos.  
Las claves de licencia se entregan automáticamente desde el inventario; los productos en formato de archivo se envían a través de enlaces de descarga.  
Un panel de administración completo dentro de Telegram permite gestionar productos, categorías, existencias, pedidos, disputas, usuarios, transmisiones y configuraciones de la tienda.

Desarrollado con **Python**, **python-telegram-bot v20** (asíncrono) y **SQLAlchemy** (SQLite de forma predeterminada).

---

<img width="434" height="501" alt="imagen" src="https://github.com/user-attachments/assets/45c50008-6b86-4d0c-b0a9-d329b492862b" />

## Índice

1. [Características](#features)  
2. [Stack tecnológico](#tech-stack)  
3. [Estructura del proyecto](#project-structure)  
4. [Requisitos previos](#prerequisites)  
5. [Paso 1: Obtener las credenciales de Telegram](#step-1--get-your-telegram-credentials)  
6. [Paso 2: Clonar el repositorio](#step-2--clone-the-repository)  
7. [Paso 3: Crear un entorno virtual](#step-3--create-a-virtual-environment)  
8. [Paso 4: Instalar dependencias](#step-4--install-dependencies)  
9. [Paso 5: Configurar variables de entorno](#step-5--configure-environment-variables)  
10. [Paso 6: Ejecutar el bot](#step-6--run-the-bot)  
11. [Paso 7: Usar el bot (`/start` y `/admin`)](#step-7--use-the-bot-start-and-admin)  
12. [Opcional: Webhooks en tiempo real de CryptoBot](#optional--real-time-cryptobot-webhooks)  
13. [Opcional: Mantener el bot en ejecución las 24 horas del día](#optional--keep-the-bot-running-247)  
14. [Notas sobre la base de datos](#database-notes)  
15. [Solución de problemas](#troubleshooting)  
16. [Notas de seguridad](#security-notes)

---

## Características

- 🛒 Catálogo de productos con categorías y subcategorías  
- 🔑 Dos tipos de productos: **claves de licencia** (entregadas automáticamente desde el inventario) y **archivos descargables** (entregados como enlaces)  
- 💰 Billetera interna: los usuarios realizan recargas y luego gastan el saldo en compras  
- 💳 Dos métodos de recarga, ambos opcionales y activables de forma independiente mediante la configuración:  
  - **CryptoBot**: pagar con cualquier criptomoneda a través de [@CryptoBot](https://t.me/CryptoBot)  
  - **Tarjeta**: pagos con tarjeta directamente dentro de Telegram a través de Telegram Payments  
- 🛠 Panel de **administración** completo dentro de Telegram: productos, categorías, inventario/reabastecimiento, pedidos, disputas, usuarios (bloquear/desbloquear), transmisiones y ajustes de la tienda  
- ⏱ Tareas en segundo plano para la verificación de pagos y la emisión periódica de notificaciones sobre disponibilidad

## Stack tecnológico

| Componente | Versión |
|-----------|---------|
| Python | Se recomienda 3.10+ (se soporta 3.9+) |
| python-telegram-bot | 20.7 |
| SQLAlchemy | 2.0.23 |
| Base de datos | SQLite (por defecto) o PostgreSQL |

# Requisitos previos

# Cómo funciona todo junto: `bot.py` es el punto de conexión único: primero valida la configuración (`config/`), inicializa la base de datos (`database/`), y luego registra todos los `handlers/`. Estos últimos se comunican con Telegram y hacen llamadas a `services/` (APIs externas) y `utils/` (teclados y herramientas auxiliares); todo el acceso a datos se realiza a través de `get_db_session()` en `database/db.py`.

# Restricciones estrictas
1. **Bloqueo estructural**: Mantener absolutamente intacta la estructura de datos en Markdown original, incluyendo la indentación, los niveles de título, las tablas, los enlaces, las URLs, los emblemas, los bloques de código y el código inline.
2. **Traducción selectiva**: Solo traducir el contenido de lenguaje natural visible para el usuario.
3. **Prohibición de modificaciones**: Está **estrictamente prohibido** traducir o cambiar etiquetas de código, nombres de claves, placeholders de variables (como {{var}}, ${var}, %s, %d, etc.), ejemplos de comandos, rutas de archivos, nombres de proyectos, nombres de API, nombres de paquetes, nombres de modelos, identificadores y símbolos de código; a menos que la información de contexto ya proporcione una traducción correspondiente.
4. La traducción de términos, estilos y nombres propios debe ser coherente con la información de contexto proporcionada.

## Requisitos previos

Instale estos antes de comenzar:

- **Git** — [git-scm.com/downloads](https://git-scm.com/downloads)  
- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)  
  - En **Windows**, marque la opción **“Agregar Python a PATH”** durante la instalación.  
- Una **cuenta de Telegram**

Verifique que sus herramientas estén instaladas:

**Windows (PowerShell):**
```powershell
git --version
python --version
```

**Linux / macOS:**
```bash
git --version
python3 --version
```

---

## Paso 1: Obtener sus credenciales de Telegram

Necesita un **token de bot** y su **ID de Telegram de administrador**. Las dos claves de pago son opcionales.

### 1a. Token del bot (obligatorio)
1. Abra [@BotFather](https://t.me/BotFather) en Telegram.
2. Envíe `/newbot` y siga las indicaciones (elija un nombre y un nombre de usuario que termine en `bot`).
3. Copie el **token API** que le proporcione (tiene el aspecto de `1234567890:ABCdef...`).

### 1b. Tu ID de Telegram como administrador (obligatorio)
1. Abre [@userinfobot](https://t.me/userinfobot) en Telegram.
2. Envía cualquier mensaje; te responderá con tu **ID** numérico (por ejemplo, `123456789`).
3. Este ID corresponde a la única cuenta que puede acceder a `/admin`.

### 1c. Clave API de CryptoBot (opcional: permite recargas con criptomonedas)
1. Abra [@CryptoBot](https://t.me/CryptoBot) → **Crypto Pay** → **Mis aplicaciones** → cree una aplicación.
2. Copie el **token API**. Deje el campo en blanco para desactivar la opción de CryptoBot.

### 1d. Token del proveedor de pagos de Telegram (opcional: habilita recargas con tarjeta)
1. Abra [@BotFather](https://t.me/BotFather) → seleccione su bot → **Payments**.
2. Conecte un proveedor de pagos y copie el **token del proveedor**. Deje el campo en blanco para desactivar la opción de tarjeta.
   > La disponibilidad de proveedores de tarjetas depende de la región; elija uno compatible con su país. Utilice el token **TEST** del proveedor durante el desarrollo.

# Restricciones estrictas
1. **Bloqueo estructural**: Mantener absolutamente intacta la estructura de datos Markdown original, los sangrados, los niveles de título, las tablas, los enlaces, las URLs, las insignias, los bloques de código y el código inline.
2. **Traducción selectiva**: Solo traducir el contenido de lenguaje natural visible para el usuario.
3. **Prohibición de modificaciones**: Está **estrictamente prohibido** traducir o cambiar etiquetas de código, nombres de claves, placeholders de variables (como {{var}}, ${var}, %s, %d, etc.), ejemplos de comandos, rutas de archivos, nombres de proyectos, nombres de API, nombres de paquetes, nombres de modelos, identificadores y símbolos de código; a menos que ya se haya proporcionado una traducción correspondiente en la información de contexto.
4. La traducción de términos, estilos y nombres propios debe ser coherente con la información de contexto proporcionada.

## Paso 2: Clonar el repositorio

**Windows (PowerShell) y Linux / macOS** (mismos comandos):
```bash
git clone <YOUR_REPOSITORY_URL>
cd FreeTelegramStoreBot
```
> Reemplace `<YOUR_REPOSITORY_URL>` por la URL de clonación de su repositorio, y `FreeTelegramStoreBot` por el nombre de la carpeta si es diferente.

---

## Paso 3 — Crear un entorno virtual

Un entorno virtual mantiene aisladas las dependencias de este proyecto.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
> Si la activación se bloquea debido a la política de ejecución, ejecute una vez:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned.`
> (o utilice el activador de CMD: `venv\Scripts\activate.bat`).

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Cuando esté activo, el símbolo del prompt de su shell llevará el prefijo `(venv)`. Para dejarlo desactivado posteriormente, ejecute `deactivate`.

## Paso 5 — Configurar variables de entorno

## Paso 4 — Instalar dependencias

Con el entorno virtual activo:

**Windows (PowerShell):**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Paso 5 — Configurar las variables de entorno

Copia el archivo de ejemplo a un archivo `.env` real e introduce tus valores.

**Windows (PowerShell):**
```powershell
Copy-Item.env.example.env
notepad.env
```

**Linux / macOS:**
```bash
cp.env.example.env
nano.env
```

Rellene los valores de las variables:

| Variable | Requerido | Descripción |
|----------|:--------:|-------------|
| `BOT_TOKEN` | ✅ | Token del bot obtenido de [@BotFather](https://t.me/BotFather) (Paso 1a). |
| `ADMIN_TELEGRAM_ID` | ✅ | Tu ID numérico de Telegram (Paso 1b). Es la única cuenta de administrador. |
| `ADMIN_TELEGRAM_USERNAME` | ➖ | Tu nombre de usuario sin el `@` (se utiliza en algunos mensajes). |
| `DATABASE_URL` | ➖ | Tiene como valor predeterminado `sqlite:///bot_database.db`. Establece una URL de PostgreSQL si deseas usarlo. |
| `CRYPTO_BOT_API_KEY` | ➖ | Token de CryptoBot Crypto Pay (Paso 1c). Dejarlo en blanco desactiva los recargos criptográficos. |
| `TELEGRAM_PROVIDER_TOKEN` | ➖ | Token del proveedor de Telegram Payments (Paso 1d). Dejarlo en blanco desactiva los recargos con tarjeta. |
| `PAYMENT_CURRENCY` | ➖ | Moneda para las facturas con tarjeta (valor predeterminado: `USD`). Debe ser en USD para coincidir con las cantidades de la billetera. |

El bot **no se iniciará** hasta que se hayan configurado al menos `BOT_TOKEN` y `ADMIN_TELEGRAM_ID`, ya que los valida al arrancar y sale con un mensaje claro si falta alguno de ellos.

---

## Paso 6: Ejecutar el bot

La base de datos se crea y se popula automáticamente la primera vez que se ejecuta el bot; no existe un comando de configuración separado.

**Windows (PowerShell):**
```powershell
python bot.py
```

# Restricciones estrictas
1. **Bloqueo estructural**: Mantener absolutamente intacta la estructura de Markdown original, los sangrados, los niveles de título, las tablas, los enlaces, las URLs, los emblemas, los bloques de código y el código inline.
2. **Traducción selectiva**: Solo traducir el contenido de lenguaje natural visible para el usuario.
3. **Prohibición de modificaciones**: Está **estrictamente prohibido** traducir o cambiar etiquetas de código, nombres de claves, placeholders de variables (como {{var}}, ${var}, %s, %d, etc.), ejemplos de comandos, rutas de archivos, nombres de proyectos, nombres de API, nombres de paquetes, nombres de modelos, identificadores y símbolos de código; a menos que la información de contexto ya proporcione una traducción correspondiente.
4. Las traducciones de términos, estilos y nombres propios deben ser consistentes con la información de contexto proporcionada.

Debería ver líneas de registro que terminen con:
```
Bot started successfully!
```
Deje esta terminal abierta: el bot seguirá funcionando mientras el proceso esté en ejecución. Presione **Ctrl+C** para detenerlo.

## Paso 7 — Usar el bot (`/start` y `/admin`)

## Paso 7 — Usar el bot (`/start` y `/admin`)

Mientras el bot esté en ejecución:

1. Abra Telegram y busque su bot utilizando el nombre de usuario que eligió en el Paso 1a.  
2. Envíe **`/start`**; recibirá el mensaje de bienvenida y el menú principal (Productos, Recarga, Historial de pedidos, Disponibilidad, Soporte).  
3. Envíe **`/admin`**; si su ID de Telegram coincide con `ADMIN_TELEGRAM_ID`, se abrirá el **panel de administración** (Gestión de productos, Gestión de usuarios, Gestión de pedidos, Configuración de la tienda, Transmisiones).

Si al usar `/admin` aparece el mensaje de que se deniega el acceso o no ocurre nada, significa que su `ADMIN_TELEGRAM_ID` no coincide con el de su cuenta; revise nuevamente el paso 1b, corrija el archivo `.env` y reinicie el bot.

🎉 ¡Y listo! Su bot ya está en funcionamiento. Ejecución típica la primera vez como administrador: abra `/admin` → **Product Management** → cree una categoría, luego un producto, y después use **Restock Keys** para agregar inventario. Como usuario, haga **/start** → **Top Up** para cargar fondos en la billetera y, a continuación, compre un producto.

---

## Opcional: webhooks en tiempo real de CryptoBot

De forma predeterminada, las pagos de CryptoBot se confirman mediante consultas cada ~30 segundos (sin necesidad de configuración adicional). Para obtener una confirmación **inmediata**, ejecute el servidor de webhook incluido junto con el bot.

1. Inicie el servidor de webhook (terminal separado, mismo entorno virtual):

   # Windows (PowerShell):
   ```powershell
   python webhook_server.py
   ```
   # Linux / macOS:
   ```bash
   python3 webhook_server.py
   ```
   Escucha en el puerto **5000**.

2. Hágalo accesible mediante HTTPS (por ejemplo, con [ngrok](https://ngrok.com/)):
   ```bash
   ngrok http 5000
   ```

3. En [@CryptoBot](https://t.me/CryptoBot) → **Crypto Pay → Mis aplicaciones → Webhooks**, establezca la URL en:
   ```
   https://<su-ngrok-o-dominio>/webhook/cryptobot
   ```

En Windows, puede ejecutar tanto el bot como el servidor de webhook junto con `start_with_webhooks.bat` (de todas formas, usted mismo debe usar ngrok).  
Los pagos con tarjeta no requieren webhook, ya que Telegram envía la confirmación a través de las consultas normales de actualización del bot.

---

## Opcional: Mantener el bot en ejecución las 24 horas del día

### Linux (systemd)

Cree el archivo `/etc/systemd/system/digitalstore-bot.service` (ajuste las rutas y el `User`):

```ini
[Unit]
Descripción: Bot de Telegram para la Tienda de Productos Digitales
After=network.target

[Service]
Tipo=simple
Usuario=youruser
DirectorioDeTrabajo=/home/youruser/FreeTelegramStoreBot
ExecStart=/home/youruser/FreeTelegramStoreBot/venv/bin/python bot.py
Restart=siempre
RestartSec=5

[Install]
DesearPor=multi-user.target
```

Luego, háblelo y arránquelo:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now digitalstore-bot
sudo systemctl status digitalstore-bot      # verifique que esté en ejecución
journalctl -u digitalstore-bot -f            # siga los registros
```

### Windows
Deje abierta la ventana de `python bot.py`, o ejecútelo como tarea en segundo plano o programada (por ejemplo, mediante el Planificador de tareas), o hospédelo en un servidor Linux siguiendo los pasos anteriores.

# Notas sobre la base de datos

## Notas sobre la base de datos

- **Predeterminado:** SQLite, almacenado en `bot_database.db` dentro de la carpeta del proyecto. Se crea automáticamente al ejecutarse por primera vez.
- **Copia de seguridad:** basta con copiar el archivo `bot_database.db`.
- **Restablecer (elimina todos los datos):** detenga el bot, elimine `bot_database.db` y vuelva a iniciar el bot para crear una base de datos vacía.

  **Windows (PowerShell):**
  ```powershell
  Remove-Item bot_database.db
  ```
  **Linux / macOS:**
  ```bash
  rm bot_database.db
  ```
- **PostgreSQL (opcional):** establezca `DATABASE_URL` con una URL de Postgres, por ejemplo:
  `postgresql+psycopg2://user:password@localhost:5432/digitalstore`
  (El controlador `psycopg2-binary` ya está incluido en `requirements.txt`).
- **Actualización de una base de datos antigua:** si está migrando una base de datos SQLite existente creada antes de que los campos de categoría se hicieran opcionales, ejecute una sola vez:
  `python migrations/001_make_category_id_nullable.py` (no es necesario en instalaciones nuevas).

---

## Preguntas frecuentes

**¿Qué es este proyecto?**
Un **bot de Telegram de código abierto y autohospedado para vender productos digitales**, como claves de licencia o activación de software y archivos descargables, que cuenta con una tienda online orientada al cliente y un panel de administración completo, todo dentro de Telegram.

**¿Qué puedo vender con él?**
Cualquier producto digital: claves de licencia de software, claves de juegos, códigos de tarjetas regalo, libros electrónicos, PDFs, cursos, plantillas, o cualquier archivo descargable que se envíe a través de un enlace.

**¿Cómo pagan los clientes?**
Los clientes depositan fondos en una **billetera** dentro del bot y luego utilizan ese saldo para realizar compras. Se admiten recargas a través de **CryptoBot** (cualquier criptomoneda) y **pagos con tarjeta** (Telegram Payments). Ambos métodos son opcionales y se activan o desactivan mediante la configuración.

**¿Es automática la entrega?**
Sí. Las claves de licencia se asignan automáticamente desde su inventario en el momento en que se confirma una compra; los productos en formato de archivo se entregan como un enlace de descarga, sin necesidad de procesamiento manual.

**¿Necesito saber programar para usarlo?**
No. Clona el repositorio, completa un archivo `.env` y ejecuta una sola orden. La base de datos se crea automáticamente al iniciar por primera vez.

**¿Qué base de datos utiliza?**
Por defecto, **SQLite** (sin configuración necesaria). Puede cambiar a **PostgreSQL** modificando una sola variable de entorno.

# ¿Funciona en Windows y Linux?
Sí: la [guía de instalación](#table-of-contents) contiene comandos paso a paso para **Windows, Linux y macOS**, además de un servicio `systemd` para un funcionamiento las 24 horas del día, los 7 días de la semana.

**¿Es gratuito y de código abierto?**
Sí, se distribuye bajo la [Licencia MIT](LICENSE).

---
## Solución de problemas

| Síntoma | Solución |
|---------|---------|
| `Error de configuración: Se requiere BOT_TOKEN` | Falta el archivo `.env` o los valores de `BOT_TOKEN`/`ADMIN_TELEGRAM_ID` están vacíos. Revise el Paso 5 y asegúrese de que `.env` se encuentre en la raíz del proyecto. |
| Acceso denegado a `/admin` o sin respuesta | `ADMIN_TELEGRAM_ID` no coincide con su cuenta. Obtenga nuevamente su ID (Paso 1b), actualice `.env` e inicie de nuevo el programa. |
| `ModuleNotFoundError` / errores de importación | El entorno virtual no está activo o las dependencias no están instaladas. Repita los Pasos 3 y 4. |
| No se encuentra `python` (Windows) | Vuelva a instalar Python marcando la opción **“Agregar Python a PATH”**, o utilice el lanzador `py` (`py bot.py`). |
| Activación bloqueada (Windows) | Ejecute `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` y luego reactive la activación. |
| El botón de tarjeta muestra “no configurado” | `TELEGRAM_PROVIDER_TOKEN` está vacío o es inválido; consulte el Paso 1d. |
| Los recargos en criptomoneda no se confirman automáticamente | Verifique `CRYPTO_BOT_API_KEY`, revise la consola en busca de errores de API o configure webhooks para una confirmación instantánea. |
| El bot deja de funcionar al cerrar la terminal | Esto es normal; utilice la sección [para funcionamiento 24/7](#optional--keep-the-bot-running-247). |


## Licencia

Publicado bajo la [Licencia MIT](LICENSE).

> ⚠️ **Nota: Utilice este programa únicamente con fines legales.**
> InDMDev no es ni será responsable de ninguna actividad ilegal en la que usted incurra al usar cualquiera de nuestros programas.
