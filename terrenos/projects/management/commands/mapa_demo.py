"""
Loads (or removes) SAMPLE data to demo the public interactive lot map end to end.

    python manage.py mapa_demo            ## create/refresh "Loteo Demo (muestra)"
    python manage.py mapa_demo --borrar   ## delete it and all its lands

Only touches the project whose slug is DEMO_SLUG; real projects are never modified.
"""
import datetime
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from lands.models import Land
from projects.lot_map import consistency_report, sanitize_svg
from projects.models import Project

DEMO_SLUG = "loteo-demo-muestra"
DEMO_NAME = "Loteo Demo (muestra)"
SVG_PATH = Path(__file__).resolve().parents[2] / "sample_data" / "plano-demo.svg"

## (shape_id, manzana, lote, frente m, fondo m, precio USD, estado)
WIDTHS = [16, 12, 12, 12, 12, 16]
STATUS = {
    "a-l3": "reserved", "a-l4": "sold", "a-l7": "sold", "a-l9": "under_contract",
    "b-l2": "sold", "b-l5": "not_available", "b-l6": "sold", "b-l10": "reserved",
}


def demo_lands():
    rows = []
    for block in ("a", "b"):
        for n in range(1, 13):
            shape_id = f"{block}-l{n}"
            if shape_id == "b-l12":
                continue  ## drawn but intentionally without a land: shows up in the consistency report
            width = WIDTHS[(n - 1) % 6]
            price = None if shape_id == "a-l1" else Decimal(11000 + width * 400 + n * 150)
            rows.append((shape_id, block.upper(), str(n), width, 30, price, STATUS.get(shape_id, "available")))
    ## A land with no shape on the plan: appears only in the list view
    rows.append(("", "B", "13", 12, 30, Decimal(15200), "available"))
    return rows


class Command(BaseCommand):
    help = "Crea o borra el proyecto de MUESTRA 'Loteo Demo (muestra)' con su plano interactivo."

    def add_arguments(self, parser):
        parser.add_argument("--borrar", action="store_true", help="Borra el proyecto de muestra y sus terrenos.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["borrar"]:
            deleted, _ = Project.objects.filter(slug=DEMO_SLUG).delete()
            self.stdout.write(self.style.SUCCESS(f"Muestra borrada ({deleted} registros)."))
            return

        project, _ = Project.objects.update_or_create(
            slug=DEMO_SLUG,
            defaults={
                "name": DEMO_NAME,
                "start_date": datetime.date.today(),
                "is_public": True,
                "map_svg": sanitize_svg(SVG_PATH.read_bytes()),
            },
        )
        project.land_set.all().delete()
        Land.objects.bulk_create([
            Land(
                project=project, shape_id=shape_id, block=block, manual_id=number,
                width=width, length=length, price=price, currency="USD", status=status,
                notes="DATO DE MUESTRA — no es un terreno real",
                ## The chamfered corner lot gets an explicit label position
                label_x=82 if shape_id == "a-l1" else None,
                label_y=155 if shape_id == "a-l1" else None,
            )
            for shape_id, block, number, width, length, price, status in demo_lands()
        ])

        report = consistency_report(project)
        self.stdout.write(self.style.SUCCESS(
            f"Muestra lista: /proyectos/{DEMO_SLUG}/ — {project.land_set.count()} terrenos, "
            f"{report['shape_count']} formas en el plano."
        ))
        self.stdout.write(
            f"Reporte: formas sin terreno={report['orphan_shapes']}, "
            f"terrenos sin forma={[str(land) for land in report['lands_without_shape']]}"
        )
        self.stdout.write("Para quitarla: python manage.py mapa_demo --borrar")
