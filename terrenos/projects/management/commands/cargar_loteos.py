"""
Loads the four real subdivisions (Ibarguren, Las Magnolias, Los Aromos, Torres de Bragado) and their lots.

    python manage.py cargar_loteos --dry-run             ## show what would change, write nothing
    python manage.py cargar_loteos                       ## create/update projects and lots
    python manage.py cargar_loteos --borrar-sobrantes    ## also delete lots of these projects not in the data
    python manage.py cargar_loteos --proyecto "Los Aromos"

Idempotent: projects are matched by name and lots by (project, manzana, lote), so it can be re-run.
Re-running OVERWRITES size, price, status, notes and shape_id of the lots it knows about.
Existing projects keep their start_date. The data lives in _loteos_data.py.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lands.models import Land
from people_to_lands.models import PeopleToLands
from projects.models import Project
from sales.models import Sale

from ._loteos_data import PROJECTS

CENT = Decimal("0.01")


class DryRun(Exception):
    pass


def ar(value, decimals=2):
    """Formats a number the Argentine way: 18100 -> 18.100, 359.35 -> 359,35."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def lot_notes(spec, frente, area, price_key, extra):
    parts = [f"Sup. según plano: {ar(area)} m2 (frente {ar(frente)} m)."]
    if price_key is not None:
        price = spec["prices"][price_key]
        terms = spec["terms"]
        if "boleto" in price:
            terms = f"{terms}, {price['boleto']}% al boleto"
        options = [f"contado USD {ar(price['contado'], 0)}"]
        options += [f"{n} cuotas USD {ar(total, 0)}" for n, total in price["cuotas"].items()]
        parts.append(f"{terms}: " + "; ".join(options) + ".")
    if extra:
        parts.append(extra)
    return " ".join(parts)


class Command(BaseCommand):
    help = "Crea o actualiza los loteos reales (Ibarguren, Las Magnolias, Los Aromos, Torres de Bragado) y sus terrenos."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Muestra los cambios sin guardarlos.")
        parser.add_argument("--proyecto", help="Carga sólo el proyecto con este nombre.")
        parser.add_argument(
            "--borrar-sobrantes",
            action="store_true",
            help="Borra los terrenos de estos proyectos que no están en los datos (nunca si tienen ventas o personas).",
        )

    def handle(self, *args, **options):
        specs = PROJECTS
        if options["proyecto"]:
            specs = [s for s in PROJECTS if s["name"].lower() == options["proyecto"].lower()]
            if not specs:
                raise CommandError(f"Proyecto desconocido. Opciones: {', '.join(s['name'] for s in PROJECTS)}")
        try:
            with transaction.atomic():
                for spec in specs:
                    self.load_project(spec, options["borrar_sobrantes"])
                if options["dry_run"]:
                    raise DryRun
        except DryRun:
            self.stdout.write(self.style.WARNING("Dry run: no se guardó ningún cambio."))

    def load_project(self, spec, delete_extras):
        project = Project.objects.filter(name__iexact=spec["name"]).first()
        if project is None:
            project = Project.objects.create(name=spec["name"], start_date=spec["start_date"])
            self.stdout.write(self.style.SUCCESS(f"\n{project.name}: proyecto creado (id {project.pk}, slug {project.slug})"))
        else:
            self.stdout.write(f"\n{project.name}: proyecto existente (id {project.pk}), se conserva start_date {project.start_date}")

        wanted = {(block, row[0]) for block, rows in spec["blocks"].items() for row in rows}
        extras = [land for land in project.land_set.all() if (land.block, land.manual_id) not in wanted]
        if extras:
            self.handle_extras(extras, delete_extras)

        created = updated = 0
        for block, rows in spec["blocks"].items():
            for lote, frente, area, status, price_key, extra in rows:
                frente, area = Decimal(str(frente)), Decimal(str(area))
                price = spec["prices"][price_key]["contado"] if price_key is not None else None
                shape_id = f"{block.lower()}-l{lote.lower()}"
                taken = project.land_set.filter(shape_id=shape_id).exclude(block=block, manual_id=lote).first()
                if taken:
                    self.stdout.write(self.style.WARNING(f"  shape_id {shape_id} ya lo usa el terreno {taken.pk}; se deja vacío"))
                    shape_id = ""
                _, was_created = Land.objects.update_or_create(
                    project=project,
                    block=block,
                    manual_id=lote,
                    defaults=dict(
                        width=frente,
                        length=(area / frente).quantize(CENT),
                        price=Decimal(price) if price is not None else None,
                        currency="USD",
                        status=status,
                        type="commercial" if block in spec.get("commercial", ()) else "residential",
                        shape_id=shape_id,
                        notes=lot_notes(spec, frente, area, price_key, extra),
                    ),
                )
                created += was_created
                updated += not was_created

        counts = {s: project.land_set.filter(status=s).count() for s in ("available", "reserved", "sold")}
        self.stdout.write(
            f"  {created} terrenos creados, {updated} actualizados. Total {project.land_set.count()}: "
            f"{counts['available']} disponibles, {counts['reserved']} reservados, {counts['sold']} vendidos."
        )

    def handle_extras(self, extras, delete_extras):
        label = ", ".join(f"{land.manual_id}/{land.block} (id {land.pk})" for land in extras)
        if not delete_extras:
            self.stdout.write(self.style.WARNING(
                f"  {len(extras)} terrenos que no están en los datos (se dejan; usar --borrar-sobrantes): {label}"
            ))
            return
        linked = [land for land in extras
                  if Sale.objects.filter(land=land).exists() or PeopleToLands.objects.filter(land=land).exists()]
        if linked:
            raise CommandError(
                "Estos terrenos sobrantes tienen ventas o personas asociadas y no se borran: "
                + ", ".join(f"{land.manual_id}/{land.block} (id {land.pk})" for land in linked)
            )
        for land in extras:
            land.delete()
        self.stdout.write(self.style.WARNING(f"  {len(extras)} terrenos sobrantes borrados: {label}"))
