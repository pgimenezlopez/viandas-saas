# 📋 Backlog de Producto: Cadalu SaaS

## Estado General: MVP en Producción 🚀

| Estado | Prioridad | Tipo | Tarea / Descripción |
| :---: | :---: | :---: | :--- |
| ✅ | 🔴 Alta | `Setup` | **Limpiar Base de Datos:** Ejecutar comandos `TRUNCATE` en Supabase para purgar pedidos de prueba y dejar DB limpia. |
| ✅ | 🔴 Alta | `Contenido` | **Cargar Menú Oficial:** Ingresar el catálogo real a través del panel `st.data_editor`. |
| ✅ | 🟡 Media | `Operativa` | **Manejo de Stock Dinámico:** Columna de stock en DB enlazada al carrito. Bloqueo automático ("Agotado") al llegar a cero. |
| ✅ | 🟡 Media | `Operativa` | **Mensaje de Cierre (Horarios):** Validador con `ZoneInfo` para ocultar el carrito y evitar pedidos fuera de la franja operativa. |
| ✅ | 🔵 Baja | `Analítica` | **Filtro Histórico de Fechas:** Implementación de `st.date_input` en el Monitor de Cocina para aislar la facturación de la semana actual. |
| ✅ | 🔵 Baja | `UI/UX` | **Customización Visual:** Aplicación de paleta *Pink & Cream* inyectada nativamente vía CSS. |
| 📋 | 🟡 Media | `Deuda Técnica` | **Refactor ABM (Bulk Updates):** Modificar el guardado de `02_Administrar_Menu.py` para enviar cambios masivos a SQLAlchemy en lugar de iterar filas. |
| 📋 | 🔴 Alta | `Integración` | **Notificaciones Push a Cocina:** Conectar un Webhook ligero en `app.py` para avisar al celular de producción sobre nuevos pedidos ingresados. |
| 📋 | 🔵 Baja | `Logística` | **Ruteo de Última Milla:** Extraer direcciones de Postgres y generar un link de ruta óptima en Google Maps para el chofer de la noche. |
| 📋 | 🟣 Visión | `IA / Auto` | **Menú Bot (Gemini):** Desarrollar agente que procese audios de WhatsApp dictando el menú, estructure el JSON y lo inyecte directo a Supabase. |

**Leyenda de Estados:**
- 📋 Pendiente (To Do)
- 🏃‍♂️ En Progreso (Doing)
- ✅ Completado (Done)