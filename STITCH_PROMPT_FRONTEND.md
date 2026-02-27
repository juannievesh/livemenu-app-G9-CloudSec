# Prompt para Google Stitch – Frontend LiveMenu

Copia y pega el siguiente bloque en Stitch. Luego podrás ir refinando (por ejemplo: “añade reordenamiento por drag and drop en categorías” o “cambia la paleta a tonos verdes”).

---

## Bloque para pegar en Stitch

**Proyecto:** LiveMenu – Dashboard admin para gestionar menús digitales de restaurantes (SaaS). Los dueños del restaurante usan esta app para configurar su menú; los clientes solo ven el menú público (otra URL) al escanear un QR.

**Stack obligatorio:** React (Vite o CRA), Tailwind CSS, shadcn/ui. TypeScript recomendado. Sin backend en este entregable: todo se consume vía API REST existente.

**API base:** `http://localhost:8000` (o variable de entorno `VITE_API_URL`). Todas las rutas admin requieren header `Authorization: Bearer <token>` (JWT devuelto en login). Content-Type: `application/json` salvo en upload (multipart/form-data).

**Autenticación:**
- `POST /api/v1/auth/register` – body: `{ "email": string, "password": string }` → devuelve `{ "id", "email" }`.
- `POST /api/v1/auth/login` – body: `{ "email", "password" }` → devuelve `{ "access_token", "token_type": "bearer" }`.
- `GET /api/v1/auth/me` – con Bearer token → `{ "id", "email" }`.
- Tras login, guardar el token (por ejemplo en memoria o localStorage) y enviarlo en todas las peticiones a rutas admin. Si el backend responde 401, redirigir a login.

**Restaurante (el usuario tiene un solo restaurante en este flujo):**
- `GET /api/v1/restaurants/` – lista restaurantes del usuario (normalmente uno). Respuesta: array de `{ id, name, address, slug, ... }`.
- `POST /api/v1/restaurants/` – body: `{ "name": string, "address"?: string }` – crear restaurante (requiere también `slug` si el backend lo exige; si no, el backend lo genera).
- `PUT /api/v1/restaurants/{restaurant_id}` – body: `{ "name"?, "address"? }` – actualizar.
- `DELETE /api/v1/restaurants/{restaurant_id}` – eliminar.
- Si el usuario no tiene restaurante, debe poder crearlo desde “Mi Restaurante” antes de acceder a categorías/platos/QR.

**Categorías:**
- `GET /api/v1/admin/categories` – listar (ordenadas por posición).
- `POST /api/v1/admin/categories` – body: `{ "name", "description"?, "position"? }`.
- `PUT /api/v1/admin/categories/{id}` – actualizar.
- `DELETE /api/v1/admin/categories/{id}` – eliminar (solo si no tiene platos).
- `PATCH /api/v1/admin/categories/reorder` – body: `{ "order": string[] }` (array de IDs en el orden deseado).

**Platos:**
- `GET /api/v1/admin/dishes` – query params opcionales: `category_id`, `available`, `featured`, `search`. Lista platos.
- `GET /api/v1/admin/dishes/{id}` – detalle de un plato.
- `POST /api/v1/admin/dishes` – body: `{ "category_id", "name", "description"?, "price", "offer_price"?, "available"?, "featured"?, "position"?, "image_urls"?, ... }`.
- `PUT /api/v1/admin/dishes/{id}` – actualizar.
- `DELETE /api/v1/admin/dishes/{id}` – soft delete.
- `PATCH /api/v1/admin/dishes/{id}/availability` – toggle disponibilidad (sin body).

**Imágenes:**
- `POST /api/v1/admin/upload` – multipart: `file` (imagen), `dish_id` (UUID del plato). Límite 5MB; tipos JPEG, PNG, WebP. Respuesta 202: `{ "message", "filename", "dish_id", "status": "processing" }` (el backend procesa en segundo plano).
- `DELETE /api/v1/admin/upload/{filename}` – eliminar imagen del storage.

**QR:**
- `GET /api/v1/admin/qr?format=png|svg&size=S|M|L|XL` – devuelve la imagen del QR (Content-Disposition para descarga). Usar como `src` de `<img>` con el mismo URL + token en header si hace falta, o abrir en nueva pestaña para descargar. Mostrar preview en la pantalla “Mi Código QR” y botones para descargar PNG/SVG y tamaños.

**Menú público (solo referencia):** La vista del menú para el cliente final es `GET /m/{slug}` en el mismo dominio del backend (HTML SSR). El frontend admin no la construye; solo debe mostrar el enlace o el slug para que el dueño sepa qué URL comparte/QR usa.

**Pantallas a implementar (mobile-first, responsive):**

1. **Login / Registro**  
   - Formularios: email + contraseña. Enlaces “¿No tienes cuenta? Regístrate” / “¿Ya tienes cuenta? Inicia sesión”. Mensajes de error para credenciales inválidas o email ya registrado. Tras login correcto, redirigir al dashboard.

2. **Dashboard principal (post-login)**  
   - Si no hay restaurante: CTA “Crear mi restaurante” → flujo crear restaurante.  
   - Si hay restaurante: resumen breve (nombre del restaurante, enlace a “Ver menú público” con `/m/{slug}`), y accesos rápidos a: Mi Restaurante, Categorías, Platos, Mi Código QR. Opción de cerrar sesión (borrar token y redirigir a login).

3. **Mi Restaurante**  
   - Formulario con nombre, dirección (y los campos que el backend acepte: descripción, teléfono, etc.). Botones Guardar y, si aplica, Eliminar restaurante (con confirmación). Mostrar el slug de solo lectura si el backend lo devuelve.

4. **Categorías**  
   - Lista de categorías (nombre, descripción, orden). Botón “Nueva categoría”. Crear/editar en modal o página con nombre, descripción, posición. Eliminar con confirmación (y aviso si tiene platos). Reordenar: por ejemplo botones “Subir/Bajar” o drag and drop si es posible con shadcn.

5. **Platos**  
   - Lista con filtros: por categoría, por disponibilidad (disponible / no disponible), búsqueda por texto. Cada fila: nombre, categoría, precio, oferta (si hay), disponibilidad (toggle o badge), imagen miniatura si existe. Botón “Nuevo plato”. Crear/editar: categoría, nombre, descripción, precio, precio oferta, disponible, destacado, y subida de imagen (input file → POST a `/api/v1/admin/upload` con `dish_id` una vez creado el plato). Toggle de disponibilidad rápido en la lista (PATCH availability). Eliminar con confirmación (soft delete).

6. **Mi Código QR**  
   - Texto explicando que ese QR lleva al menú público. Preview del QR: imagen obtenida de `GET /api/v1/admin/qr?format=png&size=M` (o similar), mostrando la misma URL con el token si el backend lo requiere para esa ruta). Selector de tamaño (S, M, L, XL) y formato (PNG, SVG). Botón “Descargar” que abra o descargue el archivo (misma URL con params).

7. **Manejo de errores y estados**  
   - 401 en cualquier request admin → cerrar sesión y redirigir a login.  
   - 403/404/422: mostrar mensaje claro (ej. “No tienes permiso”, “Restaurante no encontrado”, “Datos inválidos”).  
   - Loading states en listas y formularios.  
   - Validación básica en formularios (required, email, números para precios).

**Diseño y UX:**  
- Tema consistente (claro u oscuro, o ambos con toggle).  
- Navegación clara entre Dashboard, Mi Restaurante, Categorías, Platos, Mi Código QR.  
- Responsive: usable primero en móvil, luego en tablet y escritorio.  
- Usar componentes shadcn/ui (Button, Input, Card, Table, Dialog, Form, Toast o Alert para feedback).

**Nota para el equipo:** El backend real usa `GET/POST/PUT/DELETE /api/v1/restaurants/` (plural) en lugar de `/api/v1/admin/restaurant`. Si más adelante se unifica a `/admin/restaurant`, se puede cambiar solo la capa de API en el frontend.

---

## Cómo usar este prompt

1. Pega el bloque anterior en Stitch y genera la primera versión del frontend.
2. Ajusta según necesidad, por ejemplo:
   - “Añade un sidebar fijo en desktop para la navegación.”
   - “En Platos, permite arrastrar para reordenar dentro de una categoría.”
   - “El preview del QR debe actualizarse al cambiar tamaño o formato sin recargar.”
   - “Añade toasts de éxito al guardar restaurante/categoría/plato.”
3. Conecta el frontend al backend: configura `VITE_API_URL` (o equivalente) a `http://localhost:8000` y prueba login, CRUD y QR contra tu API real.

---

## Exportar a AI Studio (cuando ya tienes el diseño en Stitch)

Cuando tengas las pantallas diseñadas en Stitch y abras **Export → AI Studio PREVIEW**, en el campo **Description** no uses solo "Make this real." Usa este texto para que el código generado sea funcional y conectado a la API:

**Texto para el campo Description (copiar y pegar):**

```
Generate a working React (Vite + TypeScript) app with Tailwind and shadcn/ui. Keep the exact screens and layout from this design. Connect every screen to a real REST API: base URL http://localhost:8000, JWT in Authorization header for all /api/v1/admin/* and /api/v1/restaurants/*. Implement: login/register (POST /api/v1/auth/login, register), dashboard that loads GET /api/v1/restaurants/ and shows "Create restaurant" if empty; restaurant settings CRUD (GET/POST/PUT/DELETE /api/v1/restaurants/); categories CRUD and reorder (GET/POST/PUT/DELETE /api/v1/admin/categories, PATCH reorder); dishes list with filters and CRUD (GET/POST/PUT/DELETE /api/v1/admin/dishes, PATCH .../availability); image upload for dishes (POST /api/v1/admin/upload with dish_id and file); QR screen with preview and download (GET /api/v1/admin/qr?format=png|svg&size=S|M|L|XL). Store token after login (e.g. localStorage), redirect to login on 401. Mobile-first and responsive.
```

Luego pulsa **Build with AI Studio →**. AI Studio descargará HTML/imágenes y abrirá el proyecto; ahí podrás pedir que genere el código React completo o que lo exporte a un repo.

**Pasos después de exportar:**

1. **En AI Studio:** Pide que genere el proyecto como React (Vite) con la estructura de carpetas estándar (src/, components/, pages/, lib/api.ts o similar) y que cada pantalla llame a los endpoints indicados arriba.
2. **Descargar/exportar:** Cuando tengas el código, guarda el proyecto en la carpeta `frontend/` de tu repo (junto a `backend/`).
3. **Configurar API:** Crea `.env` en `frontend/` con `VITE_API_URL=http://localhost:8000` (o la URL de tu backend).
4. **Probar:** Con el backend levantado (`docker compose up`), ejecuta `npm install` y `npm run dev` en `frontend/` y prueba login → crear/editar restaurante → categorías → platos → QR.
5. **Ajustar:** Si algún endpoint falla (ej. restaurante requiere `slug`), corrige el backend o el cliente según lo acordado en el equipo.

---

## Cuándo traer el código aquí (Cursor) para que lo adapte o corrija

**Momento ideal:** En cuanto tengas el proyecto generado por AI Studio **dentro de tu repo** (carpeta `frontend/` en `livemenu-app-G9-CloudSec`). No hace falta que funcione todo; es mejor traerlo pronto para que lo alineemos con tu backend real.

**Dos formas de hacerlo:**

| Cuándo | Qué hacer |
|--------|-----------|
| **Opción A – Preventiva** | Copias/pegas o clonas el código en `livemenu-app-G9-CloudSec/frontend/`, abres ese proyecto en Cursor y me dices: *“Este frontend lo generó Stitch/AI Studio para LiveMenu. Revísalo y adaptalo a nuestro backend: endpoints reales, slug en restaurante, tipos, y que compile y funcione con nuestro API.”* |
| **Opción B – Cuando algo falla** | Ya tienes el código en `frontend/` pero al probar algo no funciona (login, CORS, crear restaurante, upload, QR, etc.). Me pegas el error o describes el fallo y me dices: *“El frontend está en frontend/, el backend en backend/. [Describe qué falla]. Adapta o corrige lo que haga falta.”* |

**Cosas que puedo hacer aquí cuando lo traigas:**

- **Adaptar a tu API real:** Ajustar URLs, cuerpos de request y headers (p. ej. que crear restaurante envíe `slug` si tu backend lo pide).
- **Corregir integración:** CORS, base URL desde `VITE_API_URL`, manejo de 401 (logout y redirección a login).
- **Tipos y contratos:** Alinear tipos TypeScript con las respuestas reales de tu FastAPI (ids UUID, fechas, `image_urls`, etc.).
- **Bugs:** Errores de compilación, rutas que no existen, componentes que faltan, formularios que no envían bien los datos.
- **Integración con el repo:** Añadir `frontend` al `docker-compose.yml`, scripts en el README, o un proxy para desarrollo si hace falta.
- **Detalles del enunciado:** Reorden de categorías, soft delete de platos, validación de imágenes 5MB, etc.

**Frase que puedes copiar y pegarme cuando lo traigas:**

> “Traje el frontend generado por Stitch/AI Studio a la carpeta `frontend/` del proyecto LiveMenu. [Revisa y adapta todo a nuestro backend / Corrige [X] que está fallando]. El backend está en `backend/`, API en http://localhost:8000, documentación en la wiki y en STITCH_PROMPT_FRONTEND.md.”

Así queda claro en qué momento traerlo y qué pedir que adapte o corrija.
