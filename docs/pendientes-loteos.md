# Datos a confirmar de los loteos

Al cargar los loteos desde las listas de precios y las fotos de los planos quedaron algunos datos
que no se pudieron leer o que no figuran en ningún archivo. Se cargaron con un valor provisorio
(cada terreno lo dice en sus notas) y hay que confirmarlos con el plano original.

Una vez completados: corregir los valores en
`terrenos/projects/management/commands/_loteos_data.py` y volver a correr
`python terrenos/manage.py cargar_loteos` (local y producción).

---

## 1. Torres de Bragado: superficies que no se leen en la foto

Todos estos lotes están vendidos. Hace falta la superficie (y el frente si no es el indicado) de
cada lote.

**Manzanas 10bz y 10ca** (16 lotes cada una, frente 12 m). La foto es ilegible: se cargó
355,50 m² para los lotes 1, 5, 9 y 13, y 360 m² para el resto.

| Lote | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10bz m² | | | | | | | | | | | | | | | | |
| 10ca m² | | | | | | | | | | | | | | | | |

**Manzana 10cb** (14 lotes). La foto es ilegible. Se cargó lo siguiente:
- lotes 1 a 4 y 8 a 11: frente 14,63 m y 380 m²;
- lotes 5 a 7 y 12 a 14: 12 × 29,29 = 351,48 m².

| Lote | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| m² | | | | | | | | | | | | | | |

**Manzanas 10ch y 10cm**: se leen a medias. Están cargados los valores de abajo; verificar.

| Lote | 1 | 2 | 3 | 4 | 5 | 9 | 10 | 11 | 12 | 13 | resto |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10ch m² (frente 12,50 en 1-4 y 9-12) | 297,50 | 300 | 300 | 297,50 | 301,01 | 297,53 | 300 | 300 | 297,53 | 301,02 | ≈ 301 |
| 10cm m² (frente 12) | 313,35 | 319,02 | 318,44 | 317,86 | 312,77 | 312,79 | 317,87 | 318,45 | 319,03 | 313,11 | 360 |

## 2. Torres de Bragado: manzana 10cr (plaza), lotes 4 y 5

Ambos disponibles. En el plano no se lee la superficie: se cargó **311 m²** (dato de la lista) y
frente 12 m para los dos.

- [ ] Lote 4: ______ m², frente ______ m
- [ ] Lote 5: ______ m², frente ______ m

## 3. Torres de Bragado: lotes comerciales (hoja "Lotes grandes")

Los 25 lotes figuran como vendidos. La lista sólo da la superficie, así que se cargaron con
**frente y fondo provisorios** (como si fueran cuadrados). Hace falta frente y fondo de cada uno.

| Manzana | Lotes | Superficie (lista) | Frente | Fondo |
|---|---|---|---|---|
| ce | 1 y 4 | 2100 m² | | |
| ce | 2a y 2b | 1000 m² | | |
| ce | 6 y 10 | 2400 m² | | |
| ct | 4, 6, 8 y 10 | 2400 m² | | |
| df | 10, 11 y 12 | 1600 m² | | |
| df | 1, 2 y 4 | 2200 m² | | |
| cf | 1, 2, 6 y 8 | 2000 m² | | |
| cw | 1 y 2 | 2000 m² | | |

Además:

- [ ] **Lote 5**: la lista no dice manzana ni superficie. Se cargó en la **manzana ce** con
      **2000 m²**. Manzana: ______ Superficie: ______ m²
- [ ] **Lotes 23 y 24** (3000 m²): la lista no dice la manzana. Se cargaron en una manzana
      provisoria **"SM"** (sin manzana). Manzana: ______
- [ ] Las manzanas se cargaron con el prefijo de la Chacra 10 (10ce, 10ct, …), igual que el
      resto del loteo. ¿Es correcto para las fracciones II y III? ______

## 4. Las Magnolias: manzana 179N, lote 11

- [ ] El plano dice **320,64 m²** (12 × 26,72), pero la lista de precios dice **416 m²**. Se
      cargó 320,64 m². Superficie correcta: ______ m²
