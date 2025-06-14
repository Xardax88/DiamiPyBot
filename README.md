<div align="center">
  <!-- Opcional: Si tienes un logo, puedes ponerlo aquí -->
  <!-- <img src="URL_DE_TU_LOGO" alt="Logo de Diami" width="120" height="120"> -->
  
  # Diami Bot - Edición Python 🐍
  
  Un bot de Discord versátil y multipropósito, reescrito desde cero en Python con un enfoque en el rendimiento, la escalabilidad y nuevas funcionalidades.

  <!-- Badges -->
  <p>
    <img src="https://img.shields.io/badge/Status-En%20Desarrollo-blue" alt="Estado del Proyecto">
    <img src="https://img.shields.io/github/last-commit/Neodoomed/DiamiPyBot" alt="Último Commit">
    <img src="https://img.shields.io/github/repo-size/Neodoomed/DiamiPyBot" alt="Tamaño del Repositorio">
    <img src="https://img.shields.io/github/license/Neodoomed/DiamiPyBot" alt="Licencia">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Versión de Python">
    <img src="https://img.shields.io/badge/discord.py-v2.3.2-blue?logo=discord&logoColor=white" alt="discord.py">
  </p>
</div>

## 📖 Acerca del Proyecto

**Diami** es la nueva encarnación de mi bot personal de Discord, esta vez escrito completamente en **Python** utilizando la librería `discord.py`.

Este proyecto nace de dos motivaciones principales:
1.  **Migración Tecnológica:** Dejar atrás plataformas de hosting que comenzaban a tener un costo elevado.
2.  **Aprendizaje y Crecimiento:** Poner en práctica y profundizar mis conocimientos en el ecosistema de Python, creando un bot más robusto, eficiente y con una base de código limpia.

El objetivo final es crear un asistente para servidores de Discord que no solo ofrezca las funcionalidades estándar, sino que también integre sistemas complejos de economía, juegos de rol, entretenimiento e inteligencia artificial con la API de Gemini.

<!-- Aquí es un excelente lugar para una captura de pantalla de un comando en acción -->
<!-- ![Ejemplo del Bot](URL_DE_LA_CAPTURA_DE_PANTALLA.png) -->

### 🛠️ Construido Con

Esta es la pila tecnológica que da vida a Diami:

*   **Lenguaje Principal:**
    *   ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
*   **Framework de Discord:**
    *   ![discord.py](https://img.shields.io/badge/discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white)
*   **Base de Datos:**
    *   ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white) (con `motor` para operaciones asíncronas)
*   **Despliegue y Hosting:**
    *   ![Fedora Server](https://img.shields.io/badge/Fedora%20Server-51A2DA?style=for-the-badge&logo=fedora&logoColor=white)
*   **Integración IA:**
    *   ![Gemini](https://img.shields.io/badge/Google%20Gemini-8E77F0?style=for-the-badge&logo=google-gemini&logoColor=white)

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
    *   Crea un archivo llamado `.env` en la raíz del proyecto.
    *   Copia el contenido de `.env.example` (si lo tienes) o usa la siguiente plantilla:
    ```env
    # .env
    DISCORD_TOKEN="EL_TOKEN_DE_TU_BOT_AQUÍ"
    MONGO_URI="TU_URI_DE_CONEXIÓN_A_MONGODB_AQUÍ"
    
    # Opcional: Para sincronización instantánea de comandos en un servidor de pruebas
    GUILD_ID="EL_ID_DE_TU_SERVIDOR_DE_PRUEBAS"
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
- [ ] **Administration**
  - [ ] Anti-Spam
  - [ ] Anti-Raid
- [ ] **Interacción Básica**
  - [ ] Comandos de texto personalizados
  - [ ] Menús contextuales (Click derecho en usuario/mensaje)
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
- [ ] **Inteligencia Artificial**
  - [ ] Implementación de IA conversacional `(powered by Gemini)`

---

## 📜 Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.

---

## 👤 Autor

**Xardax**

*   GitHub: [@Neodoomed](https://github.com/Neodoomed/)
*   Enlace al Proyecto: [https://github.com/Neodoomed/DiamiPyBot](https://github.com/Neodoomed/DiamiPyBot)