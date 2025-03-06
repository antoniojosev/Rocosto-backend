# Rocosto

  

Rocosto es un sistema que facilita el desarrollo e implementación de análisis de precio unitario y la automatización de la gestión de documentos de contrato. En un futuro se planea ampliar sus funcionalidades para cubrir más áreas relacionadas con la gestión de proyectos y documentos.

  

## Tabla de Contenido

  

1. [Requisitos](#requisitos)

2. [Estructura del Proyecto](#estructura-del-proyecto)

3. [Instalación y Configuración](#instalaci%C3%B3n-y-configuraci%C3%B3n)

    - [1. Clonar el Repositorio](#1-clonar-el-repositorio)

    - [2. Crear y Activar Entorno Virtual](#2-crear-y-activar-entorno-virtual)

    - [3. Instalar Dependencias](#3-instalar-dependencias)

    - [4. Configurar la Base de Datos](#4-configurar-la-base-de-datos)

    - [5. Migraciones de la Base de Datos](#5-migraciones-de-la-base-de-datos)

    - [6. Crear Usuario Administrador](#6-crear-usuario-administrador)

    - [7. Ejecutar el Servidor de Desarrollo](#7-ejecutar-el-servidor-de-desarrollo)

4. [Uso](#uso)


  

----------

  

## Requisitos

  

-  **Python 3.8+** (Se recomienda usar la versión 3.9 o superior)

-  **Pip** (Administrador de paquetes de Python)

-  **Entorno virtual** (opcional, pero recomendado) — puedes usar `venv` o `virtualenv`

-  **Base de datos** (por defecto, Django usa SQLite, que no requiere configuración adicional. Para producción, podrías usar PostgreSQL, MySQL, etc.)

-  **Git** (para clonar el repositorio)

  

----------

  

# Estructura del Proyecto

La estructura principal del proyecto (según la captura de pantalla y tu descripción) es la siguiente:

    rocosto/
  
      ├── apps/
      
      ├── backend/
      
      ├── utils/
      
      ├── .gitignore
      
      ├── manage.py
      
      ├── pre-commit-config.yaml
      
      ├── pylintrc
    
      ├── requirements.txt
      
      └── ...

  

-  **apps/**: Aquí se encuentran las aplicaciones de Django que contienen la lógica de negocio y los modelos.

-  **backend/**: Puede incluir la configuración del proyecto, serializadores, vistas, endpoints de la API, etc.

-  **utils/**: Funciones de utilidad y helpers que se pueden usar en todo el proyecto.

-  **manage.py**: Archivo principal para ejecutar comandos de Django.

-  **requirements.txt**: Archivo con todas las dependencias necesarias para el proyecto.

- Otros archivos y carpetas relacionadas con la configuración y la documentación (como `.gitignore`, `pre-commit-config.yaml`, etc.).

  

----------

  

## Instalación y Configuración

  

A continuación, se describe el proceso paso a paso para poner en marcha el proyecto localmente.

  

### 1. Clonar el Repositorio


1. Abre tu terminal o línea de comandos.

2. Navega hasta la carpeta donde deseas clonar el proyecto.

3. Ejecuta:

        git clone https://github.com/antoniojosev/Rocosto-backend.git

4. Entra a la carpeta del proyecto:

        cd rocosto

### 2. Crear y Activar Entorno Virtual

  

Crear un entorno virtual te permite mantener las dependencias de este proyecto separadas de las de otros proyectos.

  

- En sistemas Unix (Linux/Mac):

    bash

        python3 -m venv venv
        source venv/bin/activate

- En Windows:

    batch

        python -m venv venv
        venv\Scripts\activate

  

Verás que tu línea de comandos cambia, indicando que estás dentro del entorno virtual.

  

### 3. Instalar Dependencias

  

En el proyecto encontrarás un archivo `requirements.txt` que contiene las dependencias necesarias.

  

1. Asegúrate de estar en la carpeta del proyecto (donde se encuentra `requirements.txt`).

2. Ejecuta:

        pip install -r requirements.txt

  

Esto instalará todas las librerías y paquetes que el proyecto requiere para funcionar.

  

### 4. Configurar la Base de Datos

  

Por defecto, Django usa SQLite. Si estás de acuerdo con usar SQLite en desarrollo, no necesitas configurar nada adicional. Si deseas usar otra base de datos (PostgreSQL, MySQL, etc.), deberás:

  

1. Instalar el conector correspondiente (por ejemplo, `psycopg2` para PostgreSQL).

2. Actualizar el archivo de configuración del proyecto (generalmente `settings.py`) en la sección `DATABASES` con tus credenciales y parámetros.

  

### 5. Migraciones de la Base de Datos

  

Django utiliza migraciones para crear y actualizar la estructura de la base de datos según los modelos definidos en las aplicaciones. Para ejecutar las migraciones:


    python manage.py migrate

  

Esto creará (o actualizará) las tablas necesarias en tu base de datos.

  

### 6. Crear Usuario Administrador

  

Para acceder al panel de administración de Django, necesitas un superusuario:

  

    python manage.py createsuperuser

  

El sistema te pedirá un nombre de usuario, correo electrónico (opcional) y contraseña. **Recuerda** esta información para poder acceder al panel de administración.

  

### 7. Ejecutar el Servidor de Desarrollo

  

Finalmente, para levantar el servidor de desarrollo de Django, ejecuta:
  

    python manage.py runserver

  

Por defecto, el servidor se iniciará en `http://127.0.0.1:8000/`.

  

Abre tu navegador y visita esa dirección para verificar que el proyecto esté funcionando. Si quieres acceder al panel de administración, ve a `http://127.0.0.1:8000/admin/` e ingresa las credenciales del superusuario que creaste.

  

----------

  

## Uso

  

1.  **Panel de administración**: te permite gestionar los modelos, usuarios y otros recursos de manera sencilla. Se accede desde `http://127.0.0.1:8000/admin/`.

2.  **Funcionalidades principales**:

-  **Análisis de precio unitario** (en desarrollo).

-  **Automatización de gestión de documentos de contrato** (en desarrollo).

3.  **Futuras expansiones**: se planea integrar más módulos y aplicaciones para cubrir otras necesidades relacionadas con la gestión de proyectos y documentos.
