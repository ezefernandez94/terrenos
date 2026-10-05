# Plano interactivo y web pública — guía de uso

La web pública (`/inicio/`) y la página de cada proyecto (`/proyectos/<slug>/`) se arman solas a
partir de la base de datos. Esta guía cubre el circuito completo: cargar un proyecto, dibujar y
subir su plano, vincular los lotes y publicarlo.

Archivo de ejemplo que cumple todas las convenciones:
[`terrenos/projects/sample_data/plano-demo.svg`](../terrenos/projects/sample_data/plano-demo.svg).

---

## Qué muestra la web pública

| Lugar | Qué aparece | De dónde sale |
|---|---|---|
| `/inicio/` → **Proyectos disponibles** | Una tarjeta por proyecto público: nombre, lotes disponibles / totales, precio "desde" y la miniatura del plano (o una ilustración genérica si no tiene) | Proyectos con `is_public` tildado |
| `/inicio/` → **Encontrá tu terreno** | Buscador sobre los lotes **disponibles y reservados** de todos los proyectos públicos; cada resultado abre el lote en su plano | Terrenos de esos proyectos |
| `/proyectos/<slug>/` | Plano interactivo, filtros, listado y detalle de cada lote con botón de WhatsApp | El proyecto, su SVG y sus terrenos |

Siguen siendo contenido fijo de la landing (no salen de la base): "Próximos proyectos", las
secciones 1 y 2, el mapa de contacto y el pie de página.

Un proyecto **sin tildar `is_public` no aparece en ningún lado** (ni tarjeta, ni buscador, ni
página: devuelve 404). Es la forma de prepararlo tranquilo antes de publicarlo.

---

## Paso a paso: publicar un proyecto

### 0. Acceso al admin

Todo se hace en el admin de Django: `/admin/`. Hace falta un usuario con permiso de staff:

```bash
python terrenos/manage.py createsuperuser
```

### 1. Cargar el proyecto y sus terrenos

Si ya existen en el sistema interno, saltear este paso.

- **Proyecto**: desde la app interna (`/projects/create/`) o desde el admin → **Projectos** →
  *Añadir*. El `slug` (la parte de la URL, por ejemplo `las-magnolias`) se genera solo a partir
  del nombre; se puede cambiar en el admin.
- **Terrenos**: la forma más rápida es la carga múltiple de la app interna
  (`/lands/projects/<id>/create_multiple/`). Lo que usa la web pública de cada terreno:
  número (*ID Terreno*), manzana, ancho (frente), largo (fondo), precio, moneda y estado.
  Las notas y el vendedor **nunca** se publican.

| Estado del terreno | Cómo se ve en la web | Precio visible | Botón WhatsApp | En el buscador |
|---|---|---|---|---|
| Disponible | Verde | sí ("Consultar" si no tiene precio) | sí | sí |
| Reservado | Puntos ámbar | sí | no | sí |
| Bajo contrato | Igual que Reservado | sí | no | sí |
| Vendido | Rayado gris + "Vendido" | no | no | no |
| No disponible | Cuadriculado gris | no | no | no |

### 2. Dibujar el plano (SVG)

Usar Inkscape, Illustrator o cualquier editor vectorial. La foto o el plano escaneado se puede
poner de fondo para calcar. Reglas:

1. **Tres grupos con estos `id` exactos**:
   - `lotes` — un **objeto por lote** (rectángulo, polígono o trazo) cuyo `id` es el
     **shape ID** de ese lote, por ejemplo `a-l3` (manzana A, lote 3). Se pueden agrupar por
     manzana dentro de `lotes` (`<g id="manzana-a">`); los grupos en sí no cuentan como lote.
   - `plano` — calles, nombres de calles y manzanas, flecha de norte, perímetro. No es interactivo.
   - `calco` (opcional) — la imagen de fondo para calcar. **Se borra sola al subir.**
2. Los `id` distinguen mayúsculas: usar minúsculas, números y guiones (`a-l3`, `fr8-l12`), y
   que cada uno aparezca una sola vez.
3. El documento tiene que tener `viewBox` (Inkscape e Illustrator lo ponen solos).
4. Los colores de los lotes no importan: la web los pinta según el estado.

**Ojo con el editor:**

- **Inkscape**: el *nombre* de una capa no es su `id`. Para fijar el `id`, seleccionar la capa o
  el objeto y usar *Objeto → Propiedades del objeto* (Ctrl+Shift+O) → campo **ID** → *Fijar*, o el
  Editor XML (Ctrl+Shift+X). Guardar como **SVG plano**.
- **Illustrator**: *Exportar como → SVG*, con **Estilo: Atributos de presentación** (no "Elementos
  de estilo": el bloque `<style>` se elimina al subir y el plano perdería colores y grosores) y
  **ID de objeto: Nombres de capa**. Nombrar cada objeto de lote con su shape ID.

### 3. Subir el plano

Admin → **Projectos** → el proyecto → sección **Plano interactivo** → **Subir plano (SVG)** →
elegir el archivo → **Guardar**.

Al subir, el archivo se **limpia** por seguridad: se eliminan scripts, `<style>`, imágenes, links,
animaciones, referencias externas y metadatos del editor. Si el archivo no es un SVG válido, el
admin lo rechaza con el motivo; si es válido pero algo no coincide, guarda igual y muestra una
advertencia arriba.

Para reemplazar el plano, subir uno nuevo. Para quitarlo, tildar **Quitar el plano actual**.

### 4. Vincular cada terreno con su forma

Admin → **Terrenos** → filtrar por el proyecto (columna derecha). La columna **shape_id** se edita
directo en la lista: escribir el `id` de cada lote tal cual está en el SVG y **Guardar** (abajo).
Si se repite un shape ID dentro del mismo proyecto, el admin lo marca en rojo y no guarda ningún
cambio de esa pantalla hasta corregirlo.

### 5. Revisar el reporte de consistencia

Volver al proyecto: la sección **Plano interactivo** muestra el **Reporte de consistencia** y una
vista previa. Lo ideal es ver *"Todo coincide: cada terreno tiene su forma"*. Si no:

| Aviso | Qué significa | Qué hacer |
|---|---|---|
| *El SVG no tiene un grupo con id="lotes"* | Ningún lote va a ser clickeable | Revisar el `id` del grupo (paso 2, ojo con Inkscape) |
| *Formas sin terreno asociado* | Hay un `id` dibujado que ningún terreno usa | Asignarlo en el paso 4, o corregir el `id` en el dibujo |
| *Terrenos sin forma en el plano* | Terrenos sin `shape_id` o con uno que no está en el SVG | Completarlo en el paso 4. Mientras tanto aparecen sólo en el **Listado** de la página |
| *IDs repetidos en el SVG* | Dos formas con el mismo `id` | Corregir el dibujo y volver a subirlo |

Los avisos nunca bloquean: el proyecto puede publicarse igual.

### 6. (Opcional) Ajustar etiquetas

El número de cada lote se dibuja en el centro de su forma. En lotes irregulares (esquinas,
ochavas) a veces queda mal: en el terreno, completar **label_x / label_y** con la posición en
coordenadas del SVG (las mismas que muestra el editor). Vacío = centro.

### 7. Publicar

Admin → **Projectos** → el proyecto → tildar **is_public** → **Guardar**. En la lista de proyectos
aparece el link a la **Página pública**.

### 8. Verificar

- `/inicio/` → la tarjeta del proyecto en **Proyectos disponibles**, con la miniatura del plano.
- **Encontrá tu terreno** → el proyecto en el desplegable y sus lotes en los resultados.
- `/proyectos/<slug>/` → cada lote se pinta con su estado; al hacer clic se abre el detalle.
- Probar el botón **Consultar este lote** (ver WhatsApp abajo).

Los cambios de estado o precio se ven en la web en **menos de un minuto** (los datos del plano se
cachean 60 segundos).

### Despublicar

Destildar **is_public**. El proyecto desaparece de la landing, del buscador y su página da 404.
No se borra nada.

---

## WhatsApp

El botón "Consultar este lote" abre WhatsApp con un mensaje que nombra proyecto, manzana y lote.
El número se configura con la variable de entorno `PUBLIC_WHATSAPP_NUMBER` (sólo dígitos, con
código de país, por ejemplo `5492342123456`) en `.env` y en Heroku. **Mientras no esté
configurada, el botón no se muestra.**

---

## Datos de muestra

```bash
python terrenos/manage.py mapa_demo           # crea "Loteo Demo (muestra)" (público)
python terrenos/manage.py mapa_demo --borrar  # lo borra junto con sus terrenos
```

Trae a propósito una forma sin terreno (`b-l12`) y un terreno sin forma (lote 13 de la manzana B)
para ver el reporte de consistencia en acción, y lotes en todos los estados. Sus terrenos tienen la
nota "DATO DE MUESTRA". El comando sólo toca el proyecto con slug `loteo-demo-muestra`.
**Borrarlo antes de publicar la web**, porque aparece en la landing como cualquier proyecto público.

---

## Referencia técnica

**URLs públicas** (sin login, sólo proyectos con `is_public`):

| URL | Contenido |
|---|---|
| `/inicio/` | Landing (`projects.public_views.landing`) |
| `/proyectos/<slug>/` | Página del proyecto con el plano |
| `/proyectos/<slug>/mapa.json` | Datos de los lotes para el plano (cache 60 s, ETag) |
| `/proyectos/<slug>/plano.svg` | El SVG limpio, como imagen (miniatura de la tarjeta) |

La página de un proyecto acepta parámetros para enlazar directo: `?lote=a-l3` abre ese lote,
y `?price_min=&price_max=&size=s1..s4&available=1` precargan los filtros.

**Qué datos salen del servidor**: shape ID, número, manzana, frente, fondo, superficie, precio y
moneda (sólo disponibles/reservados), estado y posición de etiqueta. Nunca notas, vendedor,
ventas, pagos ni IDs internos (`projects.lot_map.public_lot`).

**Buscador de la landing**: filtra por proyecto, superficie y precio. El rango de precio está en
USD y sólo compara lotes con precio en USD; muestra hasta 24 resultados y avisa si hay más.

**Archivos**: `projects/lot_map.py` (sanitizado, reporte, datos públicos),
`projects/public_views.py`, `projects/admin.py`, `lands/admin.py`,
`projects/templates/projects/public_detail.html`, `templates/landing.html`,
`static/js/lotmap.js`, `static/css/lotmap.css`, `static/i18n/*.json` (claves `lotmap.*`,
`projects.*`, `finder.*`).

**Tests**: `python terrenos/manage.py test` (los de esta funcionalidad están en
`projects/tests.py`).
