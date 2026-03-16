# 🍱 Sistema Integrado de Viandas (Micro-SaaS)

**Plataforma ágil para la gestión integral de negocios gastronómicos de viandas y *meal-prep*.** Diseñada para eliminar la fricción operativa de la toma de pedidos manual, automatizar la consolidación de producción en cocina y optimizar la logística de reparto.

[![App en Vivo](https://img.shields.io/badge/🟢_App_en_Vivo-Abrir_Plataforma-2ea44f?style=for-the-badge)](https://viandas-saas.streamlit.app)

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?style=flat&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Wrangling-150458?style=flat&logo=pandas&logoColor=white)

## 🚀 Arquitectura y Funcionalidades

El sistema está dividido en interfaces dedicadas según el usuario final, conectadas en tiempo real mediante una base de datos relacional en la nube.

### 🛒 1. Recepción de Pedidos (Frontend Cliente)
Menú digital interactivo optimizado para dispositivos móviles.
- **Carrito Dinámico:** Cálculo de subtotales y total en tiempo real.
- **Checkout:** Formulario de captura de datos de envío, notas y método de pago.
- **Ingesta Segura:** Conexión nativa asíncrona mediante SQLAlchemy para evitar inyecciones SQL.

### 🍳 2. Monitor de Cocina (Backend Operativo)
Dashboard privado (protegido por credenciales) para el equipo de producción.
- **Consolidación de Datos:** Lectura de PostgreSQL y procesamiento de strings de texto usando `pandas` (`groupby`).
- **Métricas Financieras:** Visualización en tiempo real de facturación acumulada y ticket promedio.
- **Planilla de Despacho:** Listado limpio y ordenado de clientes para el armado de bolsas.

---

## 📌 Roadmap de Desarrollo

- [x] **Fase 1: Motor de Ventas.** UI de clientes e integración de base de datos relacional (Supabase / PostgreSQL).
- [x] **Fase 2: Consolidación de Producción.** Dashboard de cocina con métricas e ingeniería de datos (Pandas).
- [ ] **Fase 3: Última Milla.** Ingesta automática de direcciones desde SQL para generar la ruta óptima de entrega y App de Chofer.
- [ ] **Fase 4: Automatización.** Integración con WhatsApp API y LLMs (IA) para carga de menú dinámica.

---

## 🛠️ Instalación y Uso Local

Para correr este Micro-SaaS en un entorno de desarrollo local:

1. **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/pgimenezlopez/viandas-saas.git](https://github.com/pgimenezlopez/viandas-saas.git)
    cd viandas-saas
    ```

2. **Crear y activar entorno virtual (Recomendado):**
    ```bash
    # En macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configurar credenciales de Base de Datos:**
    El sistema requiere conexión a Supabase para funcionar. Creá la carpeta `.streamlit` en la raíz del proyecto y adentro un archivo llamado `secrets.toml`:
    
    ```toml
    # Archivo: .streamlit/secrets.toml
    [connections.sql]
    url = "postgresql://postgres:[TU_PASSWORD]@[aws-0-sa-east-1.pooler.supabase.com:6543/postgres](https://aws-0-sa-east-1.pooler.supabase.com:6543/postgres)"
    ```

5. **Ejecutar la aplicación:**
    ```bash
    streamlit run app.py
    ```