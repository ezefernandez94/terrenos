"""
Public interactive lot map: SVG sanitizing, SVG/lot consistency report, and the
public payload served to the map frontend.

SVG drawing conventions are documented in docs/mapa-interactivo.md.
"""
import re
import xml.etree.ElementTree as ET

from defusedxml import DefusedXmlException
from defusedxml.ElementTree import fromstring

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)

MAX_SVG_BYTES = 3 * 1024 * 1024

## Group ids the owner uses when drawing (see docs/mapa-interactivo.md)
LOTS_GROUP_ID = "lotes"
TRACE_GROUP_ID = "calco"
## Elements under #lotes that count as a lot when they carry an id. <g> sub-groups
## (e.g. one per manzana) are only for organizing and are never lots themselves.
LOT_SHAPE_ELEMENTS = {"path", "rect", "polygon", "polyline", "circle", "ellipse"}

## Every id in the stored SVG gets this prefix so the inlined map can never collide
## with ids already present in the host page. Lot shapes keep their original id in
## data-shape-id, which is what the frontend and the consistency report use.
ID_PREFIX = "plano-"

ALLOWED_ELEMENTS = {
    "svg", "g", "defs", "symbol", "use", "title", "desc",
    "path", "rect", "circle", "ellipse", "line", "polyline", "polygon",
    "text", "tspan",
    "pattern", "linearGradient", "radialGradient", "stop", "clipPath", "mask", "marker",
}

ALLOWED_ATTRIBUTES = {
    "id", "class", "style", "transform", "viewBox", "preserveAspectRatio", "version",
    "x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry", "width", "height",
    "d", "points", "pathLength", "dx", "dy", "rotate", "textLength", "lengthAdjust",
    "fill", "fill-opacity", "fill-rule", "stroke", "stroke-width", "stroke-opacity",
    "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "stroke-dashoffset",
    "stroke-miterlimit", "opacity", "vector-effect", "paint-order", "visibility", "display",
    "font-family", "font-size", "font-weight", "font-style", "letter-spacing",
    "text-anchor", "dominant-baseline", "alignment-baseline",
    "offset", "stop-color", "stop-opacity", "gradientUnits", "gradientTransform",
    "fx", "fy", "spreadMethod",
    "patternUnits", "patternContentUnits", "patternTransform",
    "clip-path", "clip-rule", "clipPathUnits", "mask", "maskUnits", "maskContentUnits",
    "marker-start", "marker-mid", "marker-end", "markerWidth", "markerHeight",
    "markerUnits", "refX", "refY", "orient",
    "href",
}

## url(...) is only allowed when it points inside the document: url(#id)
_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]*)\1\s*\)", re.IGNORECASE)
_DANGEROUS_RE = re.compile(r"javascript:|vbscript:|data:|expression\s*\(|@import|\\", re.IGNORECASE)


class SvgError(ValueError):
    """The uploaded file is not an SVG that can be published."""


def _local(tag):
    """Split '{ns}name' into (ns, name)."""
    if tag.startswith("{"):
        ns, _, name = tag[1:].partition("}")
        return ns, name
    return "", tag


def _safe_value(value):
    """Return True when an attribute value can not load or run anything external."""
    if _DANGEROUS_RE.search(value):
        return False
    for _, target in _URL_RE.findall(value):
        if not target.strip().startswith("#"):
            return False
    return True


def _rewrite_refs(value):
    """Prefix internal url(#id) references so they follow the renamed ids."""
    return _URL_RE.sub(lambda m: f"url(#{ID_PREFIX}{m.group(2).strip()[1:]})", value)


def _parse_length(value):
    match = re.match(r"^\s*([0-9.]+)\s*(px)?\s*$", value or "")
    return float(match.group(1)) if match else None


def sanitize_svg(raw):
    """
    Parse an uploaded SVG and return a cleaned SVG string safe to inline in a public page.

    Drops scripts, event handlers, foreignObject, images, links, animations, <style>,
    external references, non-SVG namespaces (Inkscape/Illustrator metadata) and the
    tracing group (id="calco"). Raises SvgError if the file is not a usable SVG.
    """
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if len(raw) > MAX_SVG_BYTES:
        raise SvgError(f"El SVG supera el tamaño máximo ({MAX_SVG_BYTES // (1024 * 1024)} MB).")
    try:
        root = fromstring(raw, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    except (ET.ParseError, DefusedXmlException) as exc:
        raise SvgError(f"El archivo no es un SVG/XML válido: {exc}") from exc

    ns, name = _local(root.tag)
    if name != "svg" or ns not in (SVG_NS, ""):
        raise SvgError("El elemento raíz del archivo debe ser <svg>.")

    _clean_element(root)

    ## A viewBox is required so the map can scale; derive it from width/height if missing
    if not root.get("viewBox"):
        width, height = _parse_length(root.get("width")), _parse_length(root.get("height"))
        if not (width and height):
            raise SvgError("El SVG debe tener un atributo viewBox (o width y height numéricos).")
        root.set("viewBox", f"0 0 {width:g} {height:g}")
    ## Size is controlled by the page, not the file
    root.attrib.pop("width", None)
    root.attrib.pop("height", None)

    lots_group = _find_by_original_id(root, LOTS_GROUP_ID)
    if lots_group is not None:
        for element in lots_group.iter():
            original = element.get("data-shape-id-pending")
            if original and _local(element.tag)[1] in LOT_SHAPE_ELEMENTS:
                element.set("data-shape-id", original)
    for element in root.iter():
        element.attrib.pop("data-shape-id-pending", None)

    return ET.tostring(root, encoding="unicode")


def _find_by_original_id(root, original_id):
    for element in root.iter():
        if element.get("id") == ID_PREFIX + original_id:
            return element
    return None


def _clean_element(element):
    ## Children first: drop disallowed elements entirely (with their whole subtree)
    for child in list(element):
        if not isinstance(child.tag, str):
            element.remove(child)
            continue
        ns, name = _local(child.tag)
        if ns not in (SVG_NS, "") or name not in ALLOWED_ELEMENTS or child.get("id") == TRACE_GROUP_ID:
            element.remove(child)
            continue
        _clean_element(child)
        ## A <use> whose reference was external has nothing left to show
        if name == "use" and not child.get("href"):
            element.remove(child)

    ns, name = _local(element.tag)
    element.tag = f"{{{SVG_NS}}}{name}"

    for attr, value in list(element.attrib.items()):
        attr_ns, attr_name = _local(attr)
        del element.attrib[attr]
        if attr_ns == XLINK_NS and attr_name == "href":
            attr_ns = ""
        if attr_ns or attr_name not in ALLOWED_ATTRIBUTES or not _safe_value(value):
            continue
        if attr_name == "href":
            ## <use> may only reference elements inside this same document
            if not value.startswith("#"):
                continue
            value = "#" + ID_PREFIX + value[1:]
        elif attr_name == "id":
            element.set("data-shape-id-pending", value)
            value = ID_PREFIX + value
        else:
            value = _rewrite_refs(value)
        element.set(attr_name, value)


def svg_shape_ids(svg):
    """Return the lot shape ids (as drawn by the owner) found in a sanitized SVG, in order."""
    if not svg:
        return []
    root = fromstring(svg.encode("utf-8"))
    lots_group = _find_by_original_id(root, LOTS_GROUP_ID)
    if lots_group is None:
        return []
    return [el.get("data-shape-id") for el in lots_group.iter() if el.get("data-shape-id")]


def consistency_report(project):
    """
    Compare a project's SVG with its lands. Warnings only; nothing here blocks saving.

    Returns a dict with:
      has_svg, has_lots_group,
      orphan_shapes: shape ids drawn in the SVG with no land using them,
      lands_without_shape: lands with no shape_id, or whose shape_id is not in the SVG,
      duplicate_shapes: shape ids drawn more than once.
    """
    svg = project.map_svg or ""
    shape_ids = svg_shape_ids(svg)
    drawn = set(shape_ids)
    duplicates = sorted({sid for sid in shape_ids if shape_ids.count(sid) > 1})

    lands = sorted(project.land_set.all(), key=lot_sort_key)
    assigned = {land.shape_id for land in lands if land.shape_id}

    return {
        "has_svg": bool(svg),
        "has_lots_group": bool(svg) and f'id="{ID_PREFIX}{LOTS_GROUP_ID}"' in svg,
        "shape_count": len(drawn),
        "orphan_shapes": sorted(drawn - assigned),
        "lands_without_shape": [land for land in lands if not land.shape_id or land.shape_id not in drawn],
        "duplicate_shapes": duplicates,
    }


## Land.status -> what the public map shows. Statuses not listed here never reach the public.
PUBLIC_STATUS = {
    "available": "available",
    "reserved": "reserved",
    "under_contract": "reserved",
    "sold": "sold",
    "not_available": "unavailable",
}

## Only these public statuses expose a price
PRICED_STATUSES = {"available", "reserved"}


def natural_key(text):
    """Sort key so that lot "2" comes before lot "10"."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", text or "")]


def lot_sort_key(land):
    return (natural_key(land.block), natural_key(land.manual_id))


def public_status(status):
    return PUBLIC_STATUS.get(status, "unavailable")


def public_lot(land):
    """The only land data that may leave the server on public pages. No notes, seller, sale or ids."""
    status = public_status(land.status)
    has_label = land.label_x is not None and land.label_y is not None
    return {
        "shape_id": land.shape_id or None,
        "number": land.manual_id,
        "block": land.block,
        "width": float(land.width),
        "length": float(land.length),
        "area": float(land.area),
        "price": float(land.price) if status in PRICED_STATUSES and land.price is not None else None,
        "currency": land.currency.upper() if status in PRICED_STATUSES and land.price is not None else None,
        "status": status,
        "label": {"x": land.label_x, "y": land.label_y} if has_label else None,
    }


def public_payload(project):
    lands = sorted(project.land_set.all(), key=lot_sort_key)
    return {
        "project": {"name": project.name, "slug": project.slug},
        "has_map": bool(project.map_svg),
        "lots": [public_lot(land) for land in lands],
    }
