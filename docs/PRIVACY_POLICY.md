# Política de Privacidad de Diami Bot

**Fecha de Entrada en Vigor:** 20 de Mayo de 2024 

Esta Política de Privacidad describe cómo Diami ("el Bot"), desarrollado por Xardax ("nosotros", "nuestro"), recopila, utiliza y comparte información cuando añades o interactúas con el Bot.

Tu privacidad es importante para nosotros. Nos esforzamos por recopilar la mínima cantidad de datos necesarios para que el Bot funcione correctamente.

### 1. Información que Recopilamos

Recopilamos los siguientes tipos de información:

- **Datos Proporcionados por Discord:**
  - **IDs de Servidor (Guild ID):** Para guardar configuraciones específicas de cada servidor 
  - **IDs de Canal (Channel ID):** Para saber dónde enviar mensajes (ej. #general, #logs, #anuncios, #conficiones).
  - **IDs de Usuario (User ID):** Se utilizan temporalmente para identificar al autor de un comando, pero no se almacenan a largo plazo a menos que sea parte de una función específica (como un sistema de economía o niveles, que se detallará si se implementa).
  - **IDs de Mensaje (Message ID):** Para funciones como responder a un mensaje específico.

- **Datos Generados por el Usuario (Contenido):**
  - **Contenido de Comandos:** El texto y los parámetros que proporcionas al usar un comando.
  - **Contenido para la IA:** Cuando interactúas con las funciones de IA del Bot (mencionando o respondiendo a Diami), el contenido de tu mensaje y las imágenes adjuntas se envían a la API de **Google Gemini** para generar una respuesta. El historial de mensajes recientes del canal también se envía como contexto. **No almacenamos permanentemente estas conversaciones en nuestra base de datos.**

- **Datos de Configuración del Servidor:**
  - Almacenamos las configuraciones que los administradores establecen a través de los comandos `/configurar`, como el ID del canal principal, el canal de logs, y la URL del banner personalizado. Esta información está vinculada al ID de su servidor.

### 2. Cómo Utilizamos la Información

Utilizamos la información recopilada exclusivamente para:
- **Proporcionar y mantener la funcionalidad del Bot:** Guardar configuraciones, responder a comandos y participar en conversaciones.
- **Procesar solicitudes a la IA:** Enviar el contexto necesario a la API de Google Gemini para que pueda generar respuestas coherentes y en personaje.
- **Mejorar el Bot:** Analizamos patrones de uso de comandos de forma anónima para identificar bugs y decidir qué características mejorar o añadir.

### 3. Intercambio y Divulgación de Información

**No vendemos, alquilamos ni compartimos tu información personal con terceros**, con las siguientes excepciones:

- **API de Google Gemini:** El contenido de los mensajes e imágenes enviados a la IA se procesa a través de los servicios de Google. Su uso de los datos está sujeto a la [Política de Privacidad de Google](https://policies.google.com/privacy).
- **Cumplimiento Legal:** Podemos divulgar información si así lo exige la ley o en respuesta a solicitudes válidas de las autoridades públicas.

### 4. Almacenamiento y Seguridad de los Datos

- Los datos de configuración del servidor se almacenan en una base de datos **MongoDB Atlas**.
- Tomamos medidas razonables para proteger la información que recopilamos, pero ningún sistema de seguridad es impenetrable. No podemos garantizar la seguridad absoluta de nuestros sistemas.

### 5. Retención de Datos

- Los datos de configuración del servidor se conservan mientras el Bot permanezca en tu servidor. Si eliminas el Bot de tu servidor, puedes solicitar la eliminación de los datos de configuración asociados contactándonos.
- Los logs del bot, que pueden contener IDs y nombres de usuario, se rotan y eliminan periódicamente.

### 6. Tus Derechos

Tienes derecho a solicitar el acceso o la eliminación de los datos de configuración asociados a tu servidor. Para ello, por favor, ponte en contacto con nosotros.

### 7. Cambios a esta Política de Privacidad

Podemos actualizar esta Política de Privacidad de vez en cuando. Te notificaremos de cualquier cambio publicando la nueva política y, si los cambios son significativos, a través de un anuncio en nuestro servidor de soporte.

### 8. Contacto

Si tienes alguna pregunta sobre esta Política de Privacidad, por favor, contáctanos en 999.doom@gmail.com o únete a nuestro [servidor de soporte de Discord](https://discord.com/invite/3x8uMdpeHR).