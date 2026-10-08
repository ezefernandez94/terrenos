"""
Real lot data for the four subdivisions, transcribed from the price lists and plan photos in docs/:

    Ibarguren          docs/Lista de Precios Ibarguren.xlsx (hoja "Vigente")   + docs/ibarguren.jpeg
    Las Magnolias      docs/Lista de Precios Ibarguren.xlsx (hoja "Evolución") + docs/las_magnolias.jpeg
    Los Aromos         docs/Lista de Precios Los Aromos.xlsx                   + docs/los_aromos.jpeg
    Torres de Bragado  docs/Lista de precios loteo Elizondo.xlsx               + docs/torres_de_bragado.jpeg

Conventions:
- Lots highlighted in yellow on the plan are sold; red ones are taken as reserved.
- frente/superficie come from the plan. Land has no area field, so the command stores
  width = frente and length = superficie / frente: the app's `area` then matches the survey.
- Only unsold lots get a price (the current cash price). Financing options go in the notes.
- Loaded by the `cargar_loteos` command; the leading underscore keeps Django from treating this module as a command.
"""
import datetime

SOLD, AVAILABLE, RESERVED = "sold", "available", "reserved"

## Lot tuple: (lote, frente m, superficie m2, estado, clave de precio or None, nota extra)


def lots(numbers, frente, area, status=SOLD, price=None, note=""):
    return [(str(n), frente, area, status, price, note) for n in numbers]


def mark(rows, status, price_for=None, note="", **only):
    """Sets status (and optionally the price key / an extra note) for the given lot numbers."""
    wanted = {str(n) for n in only["lotes"]}
    out = []
    for lote, frente, area, st, price, extra in rows:
        if lote in wanted:
            st = status
            price = price_for(lote) if price_for else price
            extra = note or extra
        out.append((lote, frente, area, st, price, extra))
    return out


ESTIMATED = "Superficie estimada: no se lee en la foto del plano, verificar con el plano original."

# ---------------------------------------------------------------- Ibarguren
## Lista vigente desde 03/07/2026. Precio de lista para todos los lotes (no indica disponibilidad).
IBARGUREN_PRICES = {
    "resto": dict(contado=16000, cuotas={24: 17600, 36: 18400, 48: 19400}),
    "esquina": dict(contado=16500, cuotas={24: 18100, 36: 18900, 48: 19900}),
    "pasante": dict(contado=17500, cuotas={24: 19100, 36: 19900, 48: 20900}),
}
IBARGUREN_TERMS = "Lista USD vigente desde 03/07/2026, al boleto mínimo 20%"


def ibarguren_block(corner_front, areas, sold):
    """8ae / 8ag share the layout: 14 lots, corners 1a-6-8-13, through lots 7 and 14."""
    rows = []
    for lote, area in areas.items():
        if lote in ("1a", "6", "8", "13"):
            frente, key = corner_front[lote], "esquina"
        elif lote in ("7", "14"):
            frente, key = 12, "pasante"
        else:
            frente, key = 12, "resto"
        rows.append((lote, frente, area, SOLD if lote in sold else AVAILABLE, key, ""))
    return rows


IBARGUREN = dict(
    name="Ibarguren",
    start_date=datetime.date(2025, 7, 29),
    prices=IBARGUREN_PRICES,
    terms=IBARGUREN_TERMS,
    blocks={
        "8ae": ibarguren_block(
            {"1a": 13.20, "6": 13.20, "8": 13.19, "13": 13.19},
            {"1a": 358.60, "2": 329.51, "3": 329.06, "4": 328.61, "5": 328.16, "6": 356.07, "7": 435.87,
             "8": 355.46, "9": 327.89, "10": 328.34, "11": 328.79, "12": 329.25, "13": 358.08, "14": 435.95},
            sold={"1a", "2", "14"},
        ),
        "8ag": ibarguren_block(
            {"1a": 13.14, "6": 13.14, "8": 13.13, "13": 13.13},
            {"1a": 358.35, "2": 330.93, "3": 330.94, "4": 330.94, "5": 330.95, "6": 358.38, "7": 434.92,
             "8": 357.23, "9": 330.95, "10": 330.94, "11": 330.94, "12": 330.93, "13": 357.18, "14": 434.92},
            sold={"7"},
        ),
        ## The price list writes lots 1l and 1o as "11" and "10"; the plan letters run 1k, 1l, 1m, 1n, 1o
        "8ac": [
            ("1c", 13.05, 386.81, AVAILABLE, "esquina", ""),
            ("1d", 12, 359.35, AVAILABLE, "esquina", ""),
            ("1e", 12, 359.37, AVAILABLE, "esquina", ""),
            ("1f", 12, 359.39, AVAILABLE, "esquina", ""),
            ("1g", 12, 359.41, AVAILABLE, "esquina", ""),
            ("1k", 13.05, 386.92, AVAILABLE, "esquina", ""),
            ("1l", 12, 433.86, SOLD, "pasante", ""),
            ("1m", 12, 433.76, AVAILABLE, "pasante", ""),
            ("1n", 12, 433.68, SOLD, "pasante", ""),
            ("1o", 12, 433.78, SOLD, "pasante", ""),
        ],
    },
)

# ------------------------------------------------------------ Las Magnolias
## Prices: column 02/01/2026 of the "Evolución" sheet (stored inside the Ibarguren file). No financing data.
MAGNOLIAS_PRICES = {p: dict(contado=p, cuotas={}) for p in (16500, 17000, 17500, 19000)}
MAGNOLIAS_TERMS = "Lista USD del 02/01/2026"

_y = (lots([1], 13.50, 333) + lots(range(2, 7), 12, 306) + lots([7], 13.50, 333) + lots([8, 9], 12, 300)
      + lots([10], 13.50, 333) + lots(range(11, 16), 12, 306) + lots([16], 13.50, 333) + lots([17, 18], 12, 300))
_y = mark(_y, AVAILABLE, lambda n: {"8": 16500, "15": 17500}.get(n, 17000), lotes=[6, 8, 15, 17])
_y = mark(_y, RESERVED, lambda n: 17000, note="Marcado en rojo en el plano: se cargó como reservado, confirmar.", lotes=[4])
_y = mark(_y, AVAILABLE, lambda n: 17000, note="En el plano tiene un parche blanco sobre el amarillo: se cargó como disponible, confirmar.", lotes=[6])

_t = (lots([1], 12, 295.50) + lots(range(2, 7), 12, 360) + lots([7], 12, 295.50) + lots(range(8, 11), 12, 300)
      + lots([11], 12, 295.50) + lots(range(12, 17), 12, 360) + lots([17], 12, 295.50) + lots(range(18, 21), 12, 300))
_t = mark(_t, AVAILABLE, lambda n: {"19": 16500}.get(n, 17000), lotes=[17, 19])
_t = mark(_t, RESERVED, lambda n: 17000, note="Marcado en rojo en el plano: se cargó como reservado, confirmar.", lotes=[7])

_n = (lots([9], 13.36, 312.60) + lots([10], 13.36, 308.10)
      + lots([11], 12, 320.64, note="La lista de precios le asigna 416 m2; el plano dice 320,64 m2.")
      + lots(range(12, 15), 12, 320.64))

MAGNOLIAS = dict(
    name="Las Magnolias",
    start_date=datetime.date(2018, 1, 1),
    prices=MAGNOLIAS_PRICES,
    terms=MAGNOLIAS_TERMS,
    blocks={"179y": _y, "179t": _t, "179n": _n},
)

# --------------------------------------------------------------- Los Aromos
## Mechita, acceso José Hernández. Every lot is 50,00 x 48,13 m and the plan gives 2400 m2.
AROMOS_PRICES = {
    30000: dict(contado=30000, cuotas={24: 33000, 36: 35000, 48: 37000}),
    22000: dict(contado=22000, cuotas={24: 24000, 36: 25000, 48: 26000}),
    20000: dict(contado=20000, cuotas={24: 22000, 36: 23000, 48: 24000}),
}
AROMOS_TERMS = "Lista USD (sin fecha), al boleto mínimo 20%"
_SOLD_AFTER_LIST = "La lista de precios lo da disponible, pero en el plano figura vendido."


def aromos_block(price_for, sold, note_sold=()):
    rows = []
    for n in range(1, 9):
        if n in sold:
            rows.append((str(n), 50, 2400, SOLD, None, _SOLD_AFTER_LIST if n in note_sold else ""))
        else:
            rows.append((str(n), 50, 2400, AVAILABLE, price_for(n), ""))
    return rows


AROMOS = dict(
    name="Los Aromos",
    start_date=datetime.date(2026, 1, 1),  ## A CONFIRMAR: no surge de los archivos
    prices=AROMOS_PRICES,
    terms=AROMOS_TERMS,
    ## Block = fracción of Chacra 1 (the list calls them Manzana 1-4 = Fracción 2, 4, 6, 8)
    blocks={
        "F2": aromos_block(lambda n: 30000 if n <= 4 else 22000, sold={6}, note_sold={6}),
        "F4": aromos_block(lambda n: 20000, sold=set()),
        "F6": aromos_block(lambda n: 20000, sold={4}, note_sold={4}),
        "F8": aromos_block(lambda n: 20000, sold={1, 2, 4, 5, 7, 8}),
    },
)

# -------------------------------------------------------- Torres de Bragado
## "Loteo Elizondo" in the price list. Chacra 10. List valid from 17/01/2026.
ELIZONDO_PRICES = {
    "cr": dict(contado=17000, cuotas={24: 18500, 36: 19500}, boleto=25),
    "cs-a": dict(contado=18500, cuotas={24: 20000, 36: 21000}, boleto=25),
    "cs-b": dict(contado=17500, cuotas={24: 19000, 36: 20000}, boleto=25),
    "da": dict(contado=16000, cuotas={24: 17500, 36: 18500}, boleto=25),
    "dc": dict(contado=17000, cuotas={24: 18500, 36: 19500}, boleto=25),
    "dd-a": dict(contado=17500, cuotas={24: 19000, 36: 20000}, boleto=30),
    "dd-b": dict(contado=17000, cuotas={24: 18500, 36: 19500}, boleto=30),
    "de-a": dict(contado=17500, cuotas={24: 19000, 36: 20000}, boleto=30),
    "de-b": dict(contado=17000, cuotas={24: 18500, 36: 19500}, boleto=30),
}
ELIZONDO_TERMS = "Lista USD vigente desde 17/01/2026"


def standard_block(corner_area, edge_areas=None, note=""):
    """16-lot manzana: 1-5 and 9-13 front 12 m (1, 5, 9, 13 chamfered), 6-8 and 14-16 are 12 x 30."""
    edge_areas = edge_areas or {}
    rows = []
    for n in range(1, 17):
        if n in (6, 7, 8, 14, 15, 16):
            area = 360
        else:
            area = edge_areas.get(n, corner_area if n in (1, 5, 9, 13) else 360)
        rows.append((str(n), 12, area, SOLD, None, note))
    return rows


def ch_da_block(areas, note=""):
    """16-lot manzana: 1-4 and 9-12 front 12,50 (corners chamfered), 5-8 and 13-16 front 12."""
    return [(str(n), 12.50 if n in (1, 2, 3, 4, 9, 10, 11, 12) else 12, areas[n], SOLD, None, note) for n in range(1, 17)]


def wide_block(front, areas, note=""):
    """16-lot manzana: 1-4 and 9-12 front `front`, 5-8 and 13-16 front 12."""
    return [(str(n), front if n in (1, 2, 3, 4, 9, 10, 11, 12) else 12, areas[n], SOLD, None, note) for n in range(1, 17)]


_cb = [(str(n), 14.63 if n in (1, 2, 3, 4, 8, 9, 10, 11) else 12, 380 if n in (1, 2, 3, 4, 8, 9, 10, 11) else 351.48,
        SOLD, None, ESTIMATED) for n in range(1, 15)]

_ch = ch_da_block({1: 297.50, 2: 300, 3: 300, 4: 297.50, 5: 301.01, 6: 301.01, 7: 301.01, 8: 301.02,
                   9: 297.53, 10: 300, 11: 300, 12: 297.53, 13: 301.02, 14: 301.03, 15: 301.03, 16: 301.03},
                  note="Superficies aproximadas: la foto del plano se lee con dificultad.")

_cm = standard_block(313, {1: 313.35, 2: 319.02, 3: 318.44, 4: 317.86, 5: 312.77,
                           9: 312.79, 10: 317.87, 11: 318.45, 12: 319.03, 13: 313.11},
                     note="Superficies aproximadas: la foto del plano se lee con dificultad.")

_cn = standard_block(351.88, {1: 351.88, 2: 355.40, 3: 354.82, 4: 354.24, 5: 349.17,
                              9: 349.17, 10: 354.24, 11: 354.82, 12: 355.40, 13: 351.88})

## Lots 1 (equipamiento comunitario) and 6 (plaza) are not for sale and are not loaded
_cr = [("4", 12, 311, AVAILABLE, "cr", "Superficie tomada de la lista (311 m2); en el plano no se lee bien."),
       ("5", 12, 311, AVAILABLE, "cr", "Superficie tomada de la lista (311 m2); en el plano no se lee bien.")]

## 14 lots: 1-4 and 8-11 front 14,25; 5-7 and 12-14 are 12 x 28,50
_cs_areas = {1: 400.64, 2: 413.21, 3: 413.99, 4: 407.19, 5: 342, 6: 342, 7: 342, 8: 407.18,
             9: 412.50, 10: 413.32, 11: 400.64, 12: 342, 13: 342, 14: 342}
_cs = [(str(n), 14.25 if n in (1, 2, 3, 4, 8, 9, 10, 11) else 12, a, SOLD, None, "") for n, a in _cs_areas.items()]
_cs = mark(_cs, AVAILABLE, lambda n: "cs-a" if n in ("9", "10") else "cs-b", lotes=[7, 9, 10, 12])

_da = ch_da_block({1: 297.67, 2: 300, 3: 300, 4: 297.42, 5: 300.97, 6: 300.98, 7: 300.99, 8: 301.01,
                   9: 297.54, 10: 300, 11: 300, 12: 297.54, 13: 301.03, 14: 301.04, 15: 301.06, 16: 301.08})
_da = mark(_da, AVAILABLE, lambda n: "da", lotes=[10])
_da = mark(_da, SOLD, note=_SOLD_AFTER_LIST, lotes=[8])

_dc = mark(standard_block(355.50), AVAILABLE, lambda n: "dc", lotes=[11])

_dd = wide_block(14.65, {1: 347.10, 2: 351.60, 3: 351.60, 4: 347.93, 5: 352.15, 6: 352.23, 7: 352.32, 8: 352.40,
                         9: 348.97, 10: 351.60, 11: 351.60, 12: 347.10, 13: 351.60, 14: 351.60, 15: 351.60, 16: 351.60})
_dd = mark(_dd, AVAILABLE, lambda n: "dd-b" if n == "11" else "dd-a", lotes=[3, 4, 7, 8, 11])

_de = wide_block(14.25, {n: (337.50 if n in (1, 4, 9, 12) else 342) for n in range(1, 17)})
_de = mark(_de, AVAILABLE, lambda n: "de-b" if n in ("9", "10", "11") else "de-a", lotes=[2, 5, 6, 7, 8, 9, 10, 11, 13, 15])

## Commercial lots (sheet "Lotes grandes"): all sold. The sheet gives only the area, so frente is a
## placeholder (side of a square of that area). Pending items are listed in docs/pendientes-loteos.md
PLACEHOLDER = "Medidas provisorias: la lista sólo da la superficie ({area} m2); frente y fondo a completar."
COMMERCIAL = [
    ## (manzana, lotes, superficie, nota extra)
    ("10ce", ["1", "4"], 2100, "Fracción II."),
    ("10ce", ["2a", "2b"], 1000, "Fracción II."),
    ("10ce", ["10", "6"], 2400, "Fracción II."),
    ("10ce", ["5"], 2000, "Fracción II. La lista no indica manzana ni superficie: se asumió manzana ce y 2000 m2."),
    ("10ct", ["4", "6", "8", "10"], 2400, "Fracción II."),
    ("10df", ["10", "11", "12"], 1600, "Fracción II."),
    ("10df", ["1", "2", "4"], 2200, "Fracción II."),
    ("10cf", ["1", "2", "6", "8"], 2000, "Fracción III."),
    ("10cw", ["1", "2"], 2000, "Fracción III."),
    ("SM", ["23", "24"], 3000, "Fracción III. La lista no indica la manzana (SM = sin manzana)."),
]


def commercial_blocks():
    blocks = {}
    for block, numbers, area, extra in COMMERCIAL:
        frente = round(area ** 0.5, 2)
        note = f"{PLACEHOLDER.format(area=area)} {extra}"
        blocks.setdefault(block, []).extend((n, frente, area, SOLD, None, note) for n in numbers)
    return blocks


TORRES = dict(
    name="Torres de Bragado",
    start_date=datetime.date(2013, 1, 1),  ## A CONFIRMAR: plano aprobado 12-22-2013
    prices=ELIZONDO_PRICES,
    terms=ELIZONDO_TERMS,
    blocks={
        "10bz": standard_block(355.50, note=ESTIMATED),
        "10ca": standard_block(355.50, note=ESTIMATED),
        "10cb": _cb,
        "10ch": _ch,
        "10cm": _cm,
        "10cn": _cn,
        "10cr": _cr,
        "10cs": _cs,
        "10da": _da,
        "10db": standard_block(355.50),
        "10dc": _dc,
        "10dd": _dd,
        "10de": _de,
        **commercial_blocks(),
    },
    commercial={block for block, *_ in COMMERCIAL},
)

PROJECTS = [IBARGUREN, MAGNOLIAS, AROMOS, TORRES]
