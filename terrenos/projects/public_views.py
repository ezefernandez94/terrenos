"""
Public (unauthenticated) views for the lot map. Everything here only exposes projects
with is_public=True, and only the land fields built by lot_map.public_lot().
"""
import hashlib
import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404, HttpResponse, HttpResponseNotModified
from django.shortcuts import get_object_or_404, render
from django.utils.cache import patch_cache_control
from django.views.decorators.http import require_safe

from faqs.models import Faq

from .lot_map import lot_sort_key, public_lot, public_payload, svg_shape_ids
from .models import Project

## Short enough that a status change in the admin shows up within a minute
PUBLIC_MAX_AGE = 60


## Statuses the landing's lot finder lists (sold/unavailable lots are only shown on each map)
FINDER_STATUSES = {"available", "reserved"}


def public_project_or_404(slug):
    """Project pages and map data: only public projects that are on sale (not coming soon, not finished)."""
    return get_object_or_404(Project, slug=slug, is_public=True, status=Project.IN_PROGRESS)


def published_faqs(project=None):
    """Published FAQs of a project, or the general ones (no project) when project is None."""
    return list(Faq.objects.filter(project=project, is_published=True))


def faq_jsonld(faqs):
    """schema.org FAQPage markup (Spanish) so search engines can show the questions as rich results."""
    if not faqs:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": faq.question, "acceptedAnswer": {"@type": "Answer", "text": faq.answer}}
            for faq in faqs
        ],
    }
    ## Escaped so user text can never close the <script> tag it is embedded in
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def project_summary(project, lots):
    """Header/card figures for a public project, from its public lot dicts."""
    available = [lot for lot in lots if lot["status"] == "available"]
    currencies = {lot["currency"] for lot in available if lot["currency"]}
    prices = [lot["price"] for lot in available if lot["price"] is not None]
    single_currency = len(currencies) == 1
    return {
        "has_map": bool(project.map_svg) and bool(svg_shape_ids(project.map_svg)),
        "total_lots": len(lots),
        "available_lots": len(available),
        ## A "from" price only makes sense when every available lot shares one currency
        "min_price": min(prices) if prices and single_currency else None,
        "price_currency": next(iter(currencies)) if single_currency else "",
    }


@require_safe
def map_data(request, slug):
    """GET /proyectos/<slug>/mapa.json — lot data for the interactive map."""
    project = public_project_or_404(slug)
    body = json.dumps(public_payload(project), cls=DjangoJSONEncoder, ensure_ascii=False)
    etag = '"' + hashlib.sha256(body.encode("utf-8")).hexdigest()[:32] + '"'

    if etag in request.headers.get("If-None-Match", ""):
        response = HttpResponseNotModified()
    else:
        response = HttpResponse(body, content_type="application/json; charset=utf-8")
    response["ETag"] = etag
    response["X-Robots-Tag"] = "noindex"
    patch_cache_control(response, public=True, max_age=PUBLIC_MAX_AGE)
    return response


@require_safe
def detail(request, slug):
    """GET /proyectos/<slug>/ — public project page with the interactive lot map."""
    project = public_project_or_404(slug)
    lots = public_payload(project)["lots"]
    faqs = published_faqs(project)
    return render(request, "projects/public_detail.html", {
        "project": project,
        **project_summary(project, lots),
        "whatsapp_number": settings.PUBLIC_WHATSAPP_NUMBER,
        "faqs": faqs,
        "faq_jsonld": faq_jsonld(faqs),
    })


@require_safe
def plan_svg(request, slug):
    """GET /proyectos/<slug>/plano.svg — the sanitized plan as an image (landing card thumbnails).
    Served for every public project, since finished and coming-soon cards show it too."""
    project = get_object_or_404(Project, slug=slug, is_public=True)
    if not project.map_svg:
        raise Http404("El proyecto no tiene plano")
    response = HttpResponse(project.map_svg, content_type="image/svg+xml; charset=utf-8")
    ## Already sanitized; these headers are a second line of defense if opened directly
    response["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'"
    response["X-Content-Type-Options"] = "nosniff"
    patch_cache_control(response, public=True, max_age=300)
    return response


@require_safe
def landing(request):
    """GET /inicio/ — public landing, with projects and the lot finder fed from the DB."""
    projects = Project.objects.filter(is_public=True).prefetch_related("land_set").order_by("start_date", "name")
    ## "Proyectos": on sale first, then finished (shown with a label, not clickable).
    ## "Próximos": coming soon only. The finder only lists lots of projects on sale.
    cards, upcoming_cards, finder_lots = [], [], []
    for index, project in enumerate(projects):
        lands = sorted(project.land_set.all(), key=lot_sort_key)
        lots = [public_lot(land) for land in lands]
        card = {
            "project": project,
            **project_summary(project, lots),
            ## Projects without a plan reuse the landing's placeholder illustrations
            "placeholder": f"img/parcela-{index % 9 + 1}.svg",
        }
        if project.status == Project.COMING_SOON:
            upcoming_cards.append(card)
            continue
        cards.append(card)
        if project.status == Project.IN_PROGRESS:
            for lot in lots:
                if lot["status"] in FINDER_STATUSES:
                    finder_lots.append({**lot, "project": project.slug, "project_name": project.name})
    ## Stable sort: keeps start_date order inside each group
    cards.sort(key=lambda card: card["project"].status == Project.FINISHED)
    faqs = published_faqs()
    return render(request, "landing.html", {
        "project_cards": cards,
        "upcoming_cards": upcoming_cards,
        ## Projects offered in the finder's dropdown
        "finder_projects": [card["project"] for card in cards if card["project"].status == Project.IN_PROGRESS],
        "finder_lots": finder_lots,
        "faqs": faqs,
        "faq_jsonld": faq_jsonld(faqs),
    })
