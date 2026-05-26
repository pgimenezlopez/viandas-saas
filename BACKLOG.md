# 📋 Backlog de Producto: Cadalu SaaS

## Estado General: MVP Sólido -> Fase 4 (Automatización) 🚀

| Estado | Prioridad | Tipo | Tarea / Descripción |
| :---: | :---: | :---: | :--- |
| ✅ | 🔴 Alta | `Setup` | **Limpiar Base de Datos:** Ejecutar comandos `TRUNCATE` en Supabase. |
| ✅ | 🔴 Alta | `Contenido` | **Cargar Menú Oficial:** Ingresar el catálogo real a través del panel. |
| ✅ | 🟡 Media | `Operativa` | **Manejo de Stock Dinámico:** Columna de stock en DB enlazada al carrito. |
| ✅ | 🟡 Media | `Operativa` | **Mensaje de Cierre (Horarios):** Validador con `ZoneInfo` (America/Montevideo). |
| ✅ | 🔵 Baja | `Analítica` | **Filtro Histórico de Fechas:** Implementación de `st.date_input` en el Monitor. |
| ✅ | 🔵 Baja | `UI/UX` | **Customización Visual:** Aplicación de paleta *Pink & Cream* vía CSS. |
| ✅ | 🔴 Alta | `Deuda Técnica`| **Fix Bugs Frontend:** Scope de variables, limpieza de código y extracción a `secrets.toml`. |
| ✅ | 🟡 Media | `Deuda Técnica`| **Refactor ABM (Bulk Updates):** Transacción masiva en SQLAlchemy para el menú. |
| 📋 | 🔴 Alta | `Integración` | **Notificaciones Push a Cocina:** Webhook/Telegram para avisar de nuevos pedidos. |
| 📋 | 🔵 Baja | `Logística` | **Ruteo de Última Milla:** Extraer direcciones y generar ruta óptima en Google Maps. |
| 📋 | 🟣 Visión | `IA / Auto` | **Menú Bot (Gemini):** Agente para procesar audios de WhatsApp a JSON e inyectar en Supabase. |

**Leyenda de Estados:**
- 📋 Pendiente (To Do)
- 🏃‍♂️ En Progreso (Doing)
- ✅ Completado (Done)