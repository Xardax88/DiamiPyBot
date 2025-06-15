
![banner](docs/assets/diami_banner.png)

# Diami Bot - Edición Python 🐍
  
Un bot de Discord versátil y multipropósito, reescrito desde cero en Python con un enfoque en el rendimiento, la escalabilidad y nuevas funcionalidades.


<!-- Badges -->
![Status](https://img.shields.io/badge/Status-En%20Desarrollo-blue)
![Last Commit](https://img.shields.io/github/last-commit/Neodoomed/DiamiPyBot)
![Repo Size](https://img.shields.io/github/repo-size/Neodoomed/DiamiPyBot)
![License](https://img.shields.io/github/license/Neodoomed/DiamiPyBot)
![Python Ver](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![discord.py](https://img.shields.io/badge/discord.py-v2.3.2-blue?logo=discord&logoColor=white)
[![Discord Server](https://discordapp.com/api/guilds/774727090188320808/embed.png)](https://discord.com/invite/3x8uMdpeHR)

---
## ✨ Características Principales

| Característica | Descripción |
| :---: | :--- |
| **🧠 IA Conversacional** | Impulsado por **Google Gemini**, Diami puede entender imágenes, mantener conversaciones contextuales y participar proactivamente con una personalidad única. |
| **🤖 Comandos Intuitivos** | Implementación completa de **Comandos Slash** y **Menús Contextuales** para una integración perfecta con la interfaz de Discord. |
| **⚙️ Configuración por Servidor** | Cada servidor puede personalizar sus propios canales principales y de logs a través de una base de datos **MongoDB**. |
| **📅 Tareas Programadas** | Publicaciones automáticas y eventos recurrentes, como el clásico meme de "Feliz Jueves". |
| **🧩 Arquitectura Modular** | Código organizado en **Cogs** para una fácil expansión y mantenimiento. |


---
## 📖 Acerca del Proyecto

**Diami** es la nueva encarnación de mi bot personal de Discord, esta vez escrito completamente en **Python** utilizando la librería `discord.py`.

Este proyecto nace de varios motivos:
1.  **Migración Tecnológica:** Dejar atrás plataformas de hosting que comenzaban a tener un costo elevado.
2.  **Aprendizaje y Crecimiento:** Poner en práctica y profundizar mis conocimientos en el ecosistema de Python, creando un bot más robusto, eficiente y con una base de código limpia.
3.  **Implementación de IA:** Mejorar la integración de la IA con el codigo.
4.  **Optimizar el uso de Tasks:** Python tiene un mejor manejo del tiempo y de aplicación de tareas.

El objetivo final es crear un asistente para servidores de Discord que no solo ofrezca las funcionalidades estándar, sino que también integre sistemas complejos de economía, juegos de rol, entretenimiento e inteligencia artificial con la API de Gemini.

### Origen: De TypeScript a Python

La versión original de Diami fue desarrollada en **TypeScript**. Si bien fue un excelente proyecto para aprender y validar conceptos, la migración a Python se realizó por varias razones estratégicas:

1.  **Ecosistema de IA y Machine Learning:** Python es el lenguaje líder indiscutible en el campo de la IA. La integración con librerías como `google-generativeai` y el acceso a un vasto ecosistema de herramientas de data science es nativa y mucho más sencilla.
2.  **Facilidad y Rapidez de Desarrollo:** La sintaxis limpia  de Python permiten un desarrollo más ágil y un código más legible, ideal para un proyecto con una hoja de ruta tan ambiciosa.
3.  **Rendimiento y Manejo de Concurrencia:** Con `asyncio` como pilar, `discord.py` ofrece un manejo de la concurrencia extremadamente eficiente y maduro, perfecto para un bot que debe manejar cientos de eventos simultáneos.
4.  **Optimización de Hosting:** Este cambio también fue motivado por la necesidad de migrar desde plataformas de hosting (como Railway) que comenzaban a tener un costo elevado, hacia soluciones más personalizadas y rentables como un servidor dedicado.
5.  **Crecimiento Personal:** Poner en práctica y profundizar mis conocimientos en el ecosistema de Python, creando un bot más robusto y con una base de código profesional.
<!-- Aquí es un excelente lugar para una captura de pantalla de un comando en acción -->
<!-- ![Ejemplo del Bot](URL_DE_LA_CAPTURA_DE_PANTALLA.png) -->

### 🛠️ Construido Con

Esta es la tecnológica que da vida a Diami:

*   **Lenguaje Principal:**
    *   ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
*   **Framework de Discord:**
    *   ![discord.py](https://img.shields.io/badge/discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white)
*   **Base de Datos:**
    *   ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white) (con `motor` para operaciones asíncronas)
*   **IA:**
    *   ![Gemini](https://img.shields.io/badge/Google%20Gemini-8E77F0?style=for-the-badge&logo=google-gemini&logoColor=white)
*   **IDE**
    *   ![PyCharm](https://img.shields.io/badge/pycharm-143?style=for-the-badge&logo=pycharm&logoColor=black&color=black&labelColor=green)
*   **Despliegue y Hosting:**
    *   ![Railway](https://img.shields.io/badge/Railway-131415?style=for-the-badge&logo=railway&logoColor=white)
    *   ![Fedora Server](https://img.shields.io/badge/Fedora%20Server-51A2DA?style=for-the-badge&logo=fedora&logoColor=white)

---

### Instalación

1.  **Clona el repositorio:**
    ```sh
    git clone https://github.com/Neodoomed/DiamiPyBot.git
    cd DiamiPyBot
    ```

2.  **Crea y activa un entorno virtual** (recomendado):
    ```sh
    # Para Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configura tus variables de entorno:**
    *   Crea un archivo llamado `.env` en la raíz del proyecto y usa la siguiente plantilla:
    ```env
    # .env
    DISCORD_TOKEN="EL_TOKEN_DE_TU_BOT_AQUÍ"
    MONGO_URI="TU_URI_DE_CONEXIÓN_A_MONGODB_AQUÍ"
    
    # Opcional: Para sincronización instantánea de comandos en un servidor de pruebas
    GUILD_ID="EL_ID_DE_TU_SERVIDOR_DE_PRUEBAS"

    # Token de Gamini Api para el uso de la IA
    GEMINI_API_KEY="AQUÍ_VA_TU_CLAVE_DE_API_DE_GEMINI"
    ```

5.  **Ejecuta el bot:**
    ```sh
    python main.py
    ```

---

## 🗺️ Hoja de Ruta (Roadmap)

Esta es la lista de funcionalidades planificadas y su estado actual. ¡Hay mucho por hacer!

- [x] **Fundamentos del Bot**
  - [x] Comandos Slash
  - [x] Logger para depuración
  - [x] Task (Feliz jueves)
- [ ] **Administration**
  - [ ] Anti-Spam
  - [ ] Anti-Raid
- [ ] **Interacción Básica**
  - [ ] Comandos de texto personalizados
  - [x] Menús contextuales (Click derecho en usuario/mensaje)
  - [ ] Mensajes de bienvenida y despedida personalizables
- [ ] **Utilidades Avanzadas**
  - [ ] Dashboard web para configuración
  - [ ] Avatar animado (cambia según eventos o el día)
- [ ] **Música**
  - [ ] Reproducción desde YouTube, Spotify, etc.
  - [ ] Cola de reproducción, control de volumen y efectos.
- [ ] **Sistema de Niveles**
  - [ ] Experiencia por enviar mensajes
  - [ ] Experiencia por estar en canales de voz
  - [ ] Comando `/leaderboard`
  - [ ] Comando `/rank` para ver el nivel personal
  - [ ] Notificaciones de subida de nivel con roles
- [ ] **Sistema de Economía**
  - [ ] **Fundamentos:**
    - [ ] `/balance`, `/extract`, `/deposit`, `/daily`, `/pay`
  - [ ] **Sistema de Empleos:**
    - [ ] Trabajos con cooldown y diferentes pagos
  - [ ] **Tienda y Objetos:**
    - [ ] Compra de insignias (badges) para el perfil
    - [ ] Compra de objetos de un solo uso o permanentes
  - [ ] **Inventario:**
    - [ ] Comando `/inventory` para ver los objetos
- [ ] **Sistema de Rol (RPG)**
  - [ ] Comando de dados (`/roll 1d20+5`)
  - [ ] Hojas de personaje simplificadas
  - [ ] Sistema de canales dedicados para partidas
- [ ] **Juegos y Eventos**
  - [ ] Gachapón (colección de personajes/objetos)
  - [ ] Combate de héroes automático (Auto-battler)
  - [ ] Tower Defense (Concepto en desarrollo)
  - [ ] Eventos globales periódicos
- [ ] **Módulos de Entretenimiento**
  - [ ] Lectura de cartas del Tarot
  - [ ] Mascota virtual para el servidor
- [x] **Inteligencia Artificial** `(powered by Gemini)`
  - [x] Implementación de IA conversacional 
  - [x] Integracion en conversaciones de manera dinamica.
  - [ ] Efemérides con IA e imagen generada.

---

## 👤 Autor

**Xardax**

*   GitHub: [@Neodoomed](https://github.com/Neodoomed/)
*   Enlace al Proyecto: [https://github.com/Neodoomed/DiamiPyBot](https://github.com/Neodoomed/DiamiPyBot)