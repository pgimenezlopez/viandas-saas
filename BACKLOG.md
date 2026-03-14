# 📋 Backlog de Producto: App Viandas

| Estado | Prioridad | Tipo | Tarea / Descripción | Fecha Est. |
| :---: | :---: | :---: | :--- | :--- |
| 🏃‍♂️ | 🔴 Alta | `Setup` | **Limpiar Base de Datos:** Ejecutar comando SQL `TRUNCATE` para vaciar los pedidos de prueba antes del lanzamiento oficial. | - |
| 🏃‍♂️ | 🔴 Alta | `Contenido` | **Cargar Menú Real:** Reemplazar los platos de prueba usando el nuevo panel de administrador con los platos reales de esta semana. | - |
| 📋 | 🟡 Media | `Mejora` | **Manejo de Stock:** Agregar una variable o límite en el código para que un plato se marque como "Agotado" si se superan X porciones. | - |
| 📋 | 🟡 Media | `UI/UX` | **Mensaje de Cierre:** Ocultar el carrito y mostrar un cartel de "Pedidos Cerrados" fuera del horario o días de entrega. | - |
| 📋 | 🟡 Media | `Integración` | **Notificaciones WhatsApp (Pedidos):** Conectar una API (ej: Twilio o Evolution API) para enviar una alerta automática al celular de la cocina apenas el cliente confirma el pedido. | - |
| 📋 | 🔵 Baja | `Feature` | **Fase 3 - Reparto:** Conectar las direcciones ingresadas en PostgreSQL con una vista de ruta óptima para el chofer/repartidor. | - |
| 📋 | 🔵 Baja | `Feature` | **Filtro de Fechas:** En el Monitor de Cocina, agregar un selector para ver pedidos de semanas anteriores (historial). | - |
| 📋 | 🔵 Baja | `UI/UX` | **Customización Visual (Branding):** Configurar `config.toml` y CSS inyectado para aplicar la paleta de colores de la marca y darle aspecto de web nativa. | - |
| 📋 | 🟣 Vision | `IA / Automatización` | **Carga de Menú vía WhatsApp + IA:** Crear un bot de WhatsApp donde la administradora pase los platos por texto/audio. Usar Gemini para estructurar el JSON e inyectar el menú en Supabase. | - |

**Leyenda de Estados:**
- 📋 Pendiente (To Do)
- 🏃‍♂️ En Progreso (Doing)
- ✅ Completado (Done)