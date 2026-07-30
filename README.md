Proyecto usado para comprender los procesos bases de backend
🌿 EcoEnergy-IC
Sistema de monitoreo energético para PYMEs, desarrollado con Django. Permite registrar dispositivos, productos y mediciones de consumo, y genera alertas automáticas ante valores fuera de rango.

https://img.shields.io/badge/Python-3.10+-blue.svg
https://img.shields.io/badge/Django-5.2.6-green.svg
https://img.shields.io/badge/DB-SQLite-blue.svg
https://img.shields.io/badge/License-MIT-yellow.svg

📖 Descripción
EcoEnergy-IC nace con el objetivo de ayudar a las pequeñas y medianas empresas a centralizar y visualizar su consumo energético. A través de un panel intuitivo, los usuarios pueden:

Organizar dispositivos y productos por zonas y categorías.

Registrar mediciones periódicas de consumo.

Definir alertas personalizadas (Grave, Alto, Mediano) que se activan automáticamente cuando los valores superan los rangos establecidos.

Gestionar usuarios con roles dentro de cada organización.

El sistema implementa borrado lógico (soft delete) en todos los modelos, lo que permite auditoría y recuperación de datos eliminados.

✨ Características principales
Dashboard con indicadores clave:

Conteo de productos por categoría/zonas.

Alertas de la última semana.

Últimas mediciones registradas.

Eventos de alerta recientes.

Gestión de dispositivos: creación, edición, listado con filtros.

Gestión de productos: asociados a dispositivos, con historial de mediciones.

Alertas automáticas: se activan al registrar una medición que supera los límites configurados.

Autenticación completa: login, logout, recuperación de contraseña.

Internacionalización: configurado en español y zona horaria America/Santiago.

Modelo de usuario personalizado: extiende AbstractUser para incluir relación con Organization.

🛠️ Tecnologías utilizadas
Backend: Django 5.2.6

Base de datos: SQLite (desarrollo), compatible con PostgreSQL/MySQL en producción.

Frontend: Django Templates + CSS/JS estáticos.

Autenticación: sistema de usuarios propio con roles.

📋 Requisitos previos
Python 3.10 o superior

pip

(Opcional) virtualenv

🚀 Instalación y configuración
Sigue estos pasos para levantar el proyecto en tu entorno local:

bash
# 1. Clonar el repositorio
git clone https://github.com/Bacorsx/EcoEnergy-IC.git
cd EcoEnergy-IC

# 2. Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Crear un superusuario
python manage.py createsuperuser

# 6. Iniciar servidor de desarrollo
python manage.py runserver
Accede a http://localhost:8000 y comienza a usar el sistema.

🧑‍💻 Uso básico
Inicia sesión con el superusuario o registra un nuevo usuario.

Desde el Dashboard visualiza el resumen de consumo y alertas.

Accede a Dispositivos para agregar nuevos equipos y asignar productos.

En Productos, registra mediciones periódicas y observa las alertas generadas.

Gestiona alertas y umbrales desde la interfaz de administración o mediante los modelos.

📁 Estructura del proyecto
text
EcoEnergy-IC/
├── core/                   # Modelos base (BaseModel, Organization, soft delete)
├── dispositivos/           # Lógica de negocio (dispositivos, productos, mediciones, alertas)
├── monitoreo/              # Configuración del proyecto Django (settings, urls, wsgi)
├── usuarios/               # Modelo de usuario personalizado y vistas de autenticación
├── templates/              # Plantillas HTML globales
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
├── manage.py               # Script de gestión de Django
└── requirements.txt        # Lista de dependencias
📊 Modelos de datos principales
Modelo	Descripción
Organization	Empresa o entidad que agrupa usuarios y dispositivos.
User	Usuario del sistema, asociado a una organización y con roles.
Zone	Zona dentro de una organización (ej. planta, oficina).
Category	Categoría para clasificar productos.
Device	Dispositivo físico que contiene productos.
Product	Producto o equipo específico (ej. motor, compresor).
Measurement	Medición de consumo (valor, unidad, fecha).
Alert	Definición de alerta con severidad (Grave, Alto, Mediano).
ProductAlert	Asociación entre un producto y una alerta, con rango de valores.
ProductAlertEvent	Evento de alerta disparado por una medición concreta.
Todos los modelos heredan de BaseModel, que añade automáticamente created_at, updated_at y soporte para soft delete (deleted_at y estado).

🤝 Contribución
Las contribuciones son bienvenidas. Si deseas mejorar el proyecto:

Haz un fork del repositorio.

Crea una rama con tu nueva funcionalidad (git checkout -b feature/nueva-funcionalidad).

Realiza tus cambios y haz commit (git commit -m 'Agrega nueva funcionalidad').

Sube tus cambios (git push origin feature/nueva-funcionalidad).

Abre un Pull Request.

📄 Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

📧 Contacto
Para dudas o sugerencias, puedes abrir un issue en el repositorio o contactar al equipo de desarrollo.

¡Gracias por usar EcoEnergy-IC! 🌱
