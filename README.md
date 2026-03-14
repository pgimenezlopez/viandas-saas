# ⚙️ PGL Centro de Soluciones

**Plataforma centralizada de Ingeniería de Datos y Automatización de Procesos.**
Este repositorio aloja una suite de herramientas desarrolladas en Python para resolver ineficiencias operativas en logística, finanzas y gestión de clientes.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Estado-En_Desarrollo-green)

## 🚀 Módulos del Sistema

La aplicación actúa como un "Hub Central" que orquesta cinco soluciones independientes:

### 1. 📊 Monitor STM (Business Intelligence)
Dashboard analítico para la visualización de datos de transporte público.
- **Stack:** Pandas, Plotly.
- **Función:** Mapeo de paradas y detección de patrones de movilidad urbana.

### 2. 📂 Consolidador Excel (ETL Automation)
Motor de procesamiento para unificar reportes dispersos.
- **Problema:** Procesos manuales de copy-paste en departamentos administrativos.
- **Solución:** Script que fusiona múltiples archivos `.xlsx` o `.csv` en un reporte maestro estandarizado en segundos.

### 3. 🐾 Gestión Veterinaria (CRM)
Sistema de retención de clientes basado en alertas preventivas.
- **Función:** Cálculo automático de fechas de vencimiento de vacunas y generación de listas de contacto para recordatorios.

### 4. 🧘 Plataforma de Coaching (Seguimiento)
Herramienta de gestión para profesionales de la salud/coaching.
- **Función:** Registro de evolución de pacientes, historial de sesiones y métricas de progreso personal.

### 5. 🤖 Altiora: Generador Clínico (IA Generativa)
Asistente inteligente para terapeutas y psicólogos.
- **Stack:** Google GenAI (Gemini 2.5 Flash), Dotenv.
- **Función:** Transforma notas sueltas de sesión en informes clínicos estructurados, con candados legales de privacidad y exportación directa a `.txt`.

### 6. 🍱 Sistema Integrado de Viandas (Micro-SaaS)

Plataforma ágil para la gestión integral de negocios gastronómicos de viandas y *meal-prep*. Diseñada para eliminar la fricción operativa de la toma de pedidos manual y automatizar tanto la producción como la logística. 

El desarrollo está planificado en tres iteraciones o *sprints*:

### 📌 Roadmap del Proyecto

- [x] **Fase 1: Recepción de Pedidos (El "Atrapamoscas")**
  - Desarrollo de un menú digital interactivo optimizado para móviles (UX/UI fluida).
  - Sistema de "carrito de compras" con cálculo de subtotales y total en tiempo real.
  - Formulario de captura de datos de envío y método de pago.
  - *Arquitectura:* Integración nativa con base de datos relacional en la nube (**Supabase / PostgreSQL**) mediante SQLAlchemy.

- [x] **Fase 2: Monitor de Cocina (Consolidación de Producción)**
  - Creación de un *dashboard* privado protegido con credenciales.
  - Lectura en tiempo real de la base de datos (SQL) y limpieza de strings de texto.
  - Consolidación de pedidos mediante `pandas` (`groupby`) para totalizar porciones a cocinar.
  - Visualización de métricas financieras (ticket promedio, facturación) y planilla de despacho.

- [ ] **Fase 3: Última Milla (Optimización de Reparto)**
  - Integración nativa con el **Módulo 06 (Logística Pyme)**.
  - Ingesta automática de direcciones desde PostgreSQL para generar la ruta óptima de entrega.
  
## 🗺️ Roadmap y Backlog (Módulo Altiora)

| ✅ HECHO (MVP 1.2) | 🏃‍♂️ EN PROGRESO (Sprint Actual) | 📋 BACKLOG (Pendientes y Mejoras) |
| :--- | :--- | :--- |
| **Arquitectura:** Repositorio Git y entorno virtual. | **Autenticación (Login):** Acceso restringido por contraseña. | **Base de Datos:** Conectar a Google Sheets para historial. |
| **Integración IA:** Conexión segura con Gemini API. | | |
| **Deploy en Nube:** App pública en Streamlit Cloud. | | |
| **Seguridad:** Lógica híbrida API Keys (`.env` / `st.secrets`). | | |
| **Compliance:** Checkbox de consentimiento legal. | | |
| **Prompt Engineering:** Formato clínico SOAP estandarizado. | | |
| **Exportación Avanzada:** Generación y descarga nativa en `.pdf`. | | |

---

## 🛠️ Instalación y Uso Local

1. **Clonar el repositorio:**

    ```bash
    git clone https://github.com/pgimenezlopez/herramientas-analisis-datos.git
    ```

2. **Instalar dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Configurar variables de entorno:**
    Crear un archivo `.env` en la raíz del proyecto y agregar tu API Key de Gemini:

    ```text
    GEMINI_API_KEY=tu_clave_secreta_aqui
    ```

4. **Ejecutar la suite:**

    ```bash
    streamlit run Home.py
    ```