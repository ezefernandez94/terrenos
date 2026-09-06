# TODO

Pendientes detectados mientras se arreglaba el deploy a Heroku (commit `7ae8eda`).
Ordenados por prioridad. Ninguno bloquea el deploy actual, pero los de "Producción"
sí afectan funcionalidad visible.

---

## Producción

### 1. Los comprobantes (`Expense.receipt`) ya no se sirven

`terrenos/terrenos/urls.py` sirve `MEDIA_URL` sólo bajo `if settings.DEBUG`. Ahora que
`DEBUG=False` en Heroku, cualquier `/media/...` devuelve 404: los comprobantes subidos
no se pueden ver ni descargar.

Además el disco de Heroku es efímero — lo que se sube se pierde en el próximo restart
o deploy, así que servirlos desde el dyno no alcanza aunque se arregle la URL.

Arreglo real: mover `MEDIA_ROOT` a un storage externo (S3 vía `django-storages`, o
Cloudinary) y configurarlo en `STORAGES["default"]`.

### 2. El `Procfile` corre `runserver` en producción

```
web: python terrenos/manage.py runserver 0.0.0.0:$PORT
```

`runserver` es el servidor de desarrollo: single-threaded, sin workers, no pensado para
producción. `gunicorn` ni siquiera está en `requirements.txt`.

- Agregar `gunicorn` a `requirements.txt`.
- `Procfile`: `web: gunicorn terrenos.wsgi:app --chdir terrenos`
  (`--chdir terrenos` hace que el módulo `terrenos.wsgi` resuelva a
  `terrenos/terrenos/wsgi.py`; ese módulo ya expone `application` y `app`).
- Verificar en local antes de pushear: `gunicorn terrenos.wsgi:app --chdir terrenos`.

### 3. WhiteNoise está sirviendo los estáticos sin comprimir

`django_heroku` setea `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`,
pero ese setting **fue eliminado en Django 5.1** (reemplazado por `STORAGES`), así que
en Django 5.2.4 se ignora por completo. Resultado: los estáticos se sirven sin gzip/brotli
y sin hash en el nombre, o sea sin cache-busting ni cache de larga duración.

Arreglo:

```python
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
```

Ojo: `ManifestStaticFilesStorage` es estricto — si un template referencia un archivo que
no existe, `collectstatic` falla la build. Conviene probarlo localmente primero
(`python terrenos/manage.py collectstatic --noinput`).

### 4. Reemplazar `django-heroku`

`django-heroku` no se mantiene desde 2018 y hace cosas no obvias sobre `locals()`:
pisa `DATABASES` (forzando `sslmode=require`), `STATIC_ROOT`/`STATIC_URL`, `LOGGING`,
duplica el middleware de WhiteNoise, y setea un `ALLOWED_HOSTS = ['*']` que anula la
lista explícita del archivo. Ya está acotado a los dynos (`if os.environ.get("DYNO")`)
para que no rompa el entorno local, pero lo sano es sacarlo y escribir esas cuatro o
cinco líneas a mano — hoy `dj_database_url` y `whitenoise` ya están como dependencias
directas y hacen todo lo que hace falta.

Al sacarlo, `ALLOWED_HOSTS` pasa a ser la lista real del archivo: confirmar que incluya
todos los hosts que sirven la app (¿`terrenos.herokuapp.com` además de
`terrenos-429b9d4cf9d7.herokuapp.com`?) antes de deployar, o el sitio devuelve 400.

---

## Seguridad

### 5. Rotar la password del Postgres local

`07bc#4F5w8WFq` (usuario `ezequiel`) quedó hardcodeada en `settings.py` durante varios
commits y sigue en el historial de git, incluso después de haberla sacado del archivo.
Es una base local, así que el riesgo es bajo, pero conviene rotarla y actualizar el
`.env`. Reescribir el historial no vale la pena sólo por esto.

### 6. Verificar `DJANGO_SECRET_KEY` en Heroku

El valor de la config var arranca con `django-insec...`, que es el prefijo de la clave
que genera `django-admin startproject` — o sea, posiblemente sea la clave de ejemplo del
repo original y no una generada al azar. Con `DEBUG=False` la `SECRET_KEY` firma sesiones
y tokens CSRF, así que si es la default hay que reemplazarla:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
heroku config:set DJANGO_SECRET_KEY='<la nueva>' -a terrenos
```

Rotarla cierra todas las sesiones activas (los usuarios tienen que volver a loguearse).

---

## Deuda técnica

### 7. Migraciones comentadas en `expense_types` / `expense_type_details`

Nota que estaba en `settings.py` y se perdió al reescribir el bloque de base de datos,
copiada acá para no olvidarla:

> Para hacer las migraciones a neon, descomentar lo siguiente y correr las migraciones de
> nuevo (tuve que comentar las del key en expense_type y expense_type_detail porque sino
> tiraba error. Además tuve que reemplazar la variable de env por el string literal porque
> no lo estaba leyendo bien)

Las `operations` de `0002_*_key` y `0003_alter_*_key` siguen comentadas para esquivar un
error de migración en Neon. Mientras sigan así, `makemigrations` va a querer re-agregar el
campo `key` y el estado del esquema en Neon no coincide con el de los modelos. Hay que
reproducir el error original contra Neon y resolverlo de verdad.

(La segunda mitad de la nota ya está resuelta: la URL se lee de `DATABASE_URL` con
`dj_database_url`, sin string literal.)

### 8. Actualizar `CLAUDE.md`

Quedaron dos afirmaciones falsas después de este arreglo:

- "Postgres credentials are currently **hardcoded in `settings.py`**" — ya no; salen de
  `DATABASE_URL`.
- "`DEBUG` is read as a raw string, so any non-empty value is truthy" — ya no; se parsea
  como booleano (`1/true/yes/on`).

También conviene documentar que hace falta un `.env` con `DATABASE_URL` para correr en
local, porque ahora sin esa variable el proyecto no arranca.

### 9. La versión de Python local no coincide con la de producción

`runtime.txt` fija Python 3.11.5 (y Heroku corre 3.11), pero el virtualenv de
`terrenos/terrenos/` es Python 3.13. Es una fuente clásica de "anda en mi máquina":
conviene alinear las dos.
