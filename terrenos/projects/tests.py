import datetime
import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from lands.models import Land
from projects.lot_map import (
    SvgError,
    consistency_report,
    public_lot,
    public_status,
    sanitize_svg,
    svg_shape_ids,
)
from projects.models import Project

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">
  <g id="plano"><text x="1" y="1">Calle</text></g>
  <g id="lotes">
    <g id="manzana-a">
      <rect id="a-l1" x="0" y="0" width="10" height="10"/>
      <rect id="a-l2" x="10" y="0" width="10" height="10"/>
    </g>
    <rect id="a-l9" x="20" y="0" width="10" height="10"/>
  </g>
</svg>"""


def make_project(**kwargs):
    defaults = {"name": "Proyecto Test", "start_date": datetime.date(2026, 1, 1)}
    defaults.update(kwargs)
    return Project.objects.create(**defaults)


def make_land(project, **kwargs):
    defaults = {
        "manual_id": "1", "block": "A", "length": Decimal("30"), "width": Decimal("12"),
        "price": Decimal("15000"), "currency": "USD", "status": "available",
    }
    defaults.update(kwargs)
    return Land.objects.create(project=project, **defaults)


class SanitizeSvgTests(TestCase):
    def test_strips_scripts_handlers_and_external_content(self):
        dirty = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
                        viewBox="0 0 10 10" onload="alert(1)">
          <script>alert(1)</script>
          <style>@import url(http://evil.example/x.css);</style>
          <foreignObject><div xmlns="http://www.w3.org/1999/xhtml">x</div></foreignObject>
          <image href="http://evil.example/a.png"/>
          <a href="javascript:alert(1)"><rect width="1" height="1"/></a>
          <animate attributeName="x" to="1"/>
          <rect width="1" height="1" onclick="alert(1)" style="fill:url(http://evil.example/p)"
                fill="url(https://evil.example/#p)"/>
          <use xlink:href="http://evil.example/sprite.svg#x"/>
          <use href="data:image/svg+xml;base64,AAAA"/>
        </svg>"""
        clean = sanitize_svg(dirty)
        lowered = clean.lower()
        for needle in ("script", "onload", "onclick", "foreignobject", "<image", "<a ", "animate",
                       "javascript", "evil.example", "@import", "data:", "<style"):
            self.assertNotIn(needle, lowered)
        self.assertIn("<rect", clean)

    def test_removes_tracing_group_and_editor_metadata(self):
        dirty = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
                        viewBox="0 0 10 10">
          <g id="calco"><rect width="10" height="10"/></g>
          <inkscape:grid/>
          <rect width="1" height="1" inkscape:label="lote"/>
        </svg>"""
        clean = sanitize_svg(dirty)
        self.assertNotIn("calco", clean)
        self.assertNotIn("inkscape", clean)

    def test_rejects_entities_and_non_svg(self):
        bomb = '<!DOCTYPE svg [<!ENTITY a "aaaa">]><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1">&a;</svg>'
        for bad in (bomb, "<html></html>", "not xml at all", b"\x00\x01"):
            with self.assertRaises(SvgError):
                sanitize_svg(bad)

    def test_requires_a_size(self):
        with self.assertRaises(SvgError):
            sanitize_svg('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>')
        clean = sanitize_svg('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100px"/>')
        self.assertIn('viewBox="0 0 200 100"', clean)
        self.assertNotIn('width="200"', clean)

    def test_prefixes_ids_and_keeps_internal_references(self):
        clean = sanitize_svg("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">
          <defs><pattern id="p"/></defs><rect id="r" fill="url(#p)"/><use href="#r"/></svg>""")
        self.assertIn('id="plano-p"', clean)
        self.assertIn('fill="url(#plano-p)"', clean)
        self.assertIn('href="#plano-r"', clean)

    def test_lot_shapes_are_marked_including_nested_ones(self):
        clean = sanitize_svg(SVG)
        self.assertEqual(svg_shape_ids(clean), ["a-l1", "a-l2", "a-l9"])
        ## Groups inside #lotes and shapes outside it are never lots
        self.assertNotIn('data-shape-id="manzana-a"', clean)

    def test_sample_svg_is_valid(self):
        from projects.management.commands.mapa_demo import SVG_PATH
        self.assertEqual(len(svg_shape_ids(sanitize_svg(SVG_PATH.read_bytes()))), 24)


class ConsistencyReportTests(TestCase):
    def test_reports_orphan_shapes_and_lands_without_shape(self):
        project = make_project(map_svg=sanitize_svg(SVG))
        make_land(project, manual_id="1", shape_id="a-l1")
        make_land(project, manual_id="2", shape_id="a-l2")
        no_shape = make_land(project, manual_id="3", shape_id="")
        wrong_shape = make_land(project, manual_id="4", shape_id="a-l4")

        report = consistency_report(project)

        self.assertTrue(report["has_lots_group"])
        self.assertEqual(report["shape_count"], 3)
        self.assertEqual(report["orphan_shapes"], ["a-l9"])
        self.assertEqual({land.pk for land in report["lands_without_shape"]}, {no_shape.pk, wrong_shape.pk})

    def test_project_without_svg(self):
        project = make_project()
        make_land(project)
        report = consistency_report(project)
        self.assertFalse(report["has_svg"])
        self.assertEqual(report["orphan_shapes"], [])


class PublicStatusTests(TestCase):
    def test_status_mapping(self):
        self.assertEqual(public_status("available"), "available")
        self.assertEqual(public_status("reserved"), "reserved")
        self.assertEqual(public_status("under_contract"), "reserved")
        self.assertEqual(public_status("sold"), "sold")
        self.assertEqual(public_status("not_available"), "unavailable")
        self.assertEqual(public_status("something_new"), "unavailable")

    def test_price_hidden_for_sold_and_unavailable(self):
        project = make_project()
        self.assertEqual(public_lot(make_land(project, status="available"))["price"], 15000.0)
        self.assertEqual(public_lot(make_land(project, manual_id="2", status="under_contract"))["price"], 15000.0)
        for n, status in enumerate(("sold", "not_available"), start=3):
            lot = public_lot(make_land(project, manual_id=str(n), status=status))
            self.assertIsNone(lot["price"])
            self.assertIsNone(lot["currency"])


class PublicEndpointTests(TestCase):
    def setUp(self):
        self.project = make_project(name="Público", is_public=True, map_svg=sanitize_svg(SVG))
        make_land(self.project, manual_id="10", shape_id="a-l1", notes="NOTA PRIVADA", label_x=5, label_y=6)
        make_land(self.project, manual_id="2", shape_id="a-l2", status="sold", price=Decimal("99999"))

    def test_returns_only_public_fields(self):
        response = self.client.get(reverse("public_projects:map_data", args=[self.project.slug]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["project"], {"name": "Público", "slug": self.project.slug})
        allowed = {"shape_id", "number", "block", "width", "length", "area", "price", "currency", "status", "label"}
        for lot in data["lots"]:
            self.assertEqual(set(lot), allowed)
        body = response.content.decode()
        for secret in ("NOTA PRIVADA", "notes", "seller", "99999", '"id"', "map_svg"):
            self.assertNotIn(secret, body)
        ## Natural order: lot 2 before lot 10
        self.assertEqual([lot["number"] for lot in data["lots"]], ["2", "10"])
        self.assertEqual(data["lots"][1]["label"], {"x": 5.0, "y": 6.0})

    def test_hides_non_public_and_unknown_projects(self):
        hidden = make_project(name="Privado", is_public=False, map_svg=sanitize_svg(SVG))
        make_land(hidden)
        for slug in (hidden.slug, "no-existe"):
            self.assertEqual(self.client.get(reverse("public_projects:map_data", args=[slug])).status_code, 404)
            self.assertEqual(self.client.get(reverse("public_projects:detail", args=[slug])).status_code, 404)

    def test_caching_headers_and_conditional_get(self):
        url = reverse("public_projects:map_data", args=[self.project.slug])
        response = self.client.get(url)
        self.assertIn("max-age=60", response["Cache-Control"])
        self.assertIn("public", response["Cache-Control"])
        again = self.client.get(url, HTTP_IF_NONE_MATCH=response["ETag"])
        self.assertEqual(again.status_code, 304)

        ## A status change in the admin changes the payload, so the ETag no longer matches
        Land.objects.filter(manual_id="10").update(status="sold")
        changed = self.client.get(url, HTTP_IF_NONE_MATCH=response["ETag"])
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(changed.json()["lots"][1]["status"], "sold")

    def test_read_only(self):
        url = reverse("public_projects:map_data", args=[self.project.slug])
        self.assertEqual(self.client.post(url).status_code, 405)


class PublicPageTests(TestCase):
    @override_settings(PUBLIC_WHATSAPP_NUMBER="5492342123456")
    def test_page_with_map(self):
        project = make_project(is_public=True, map_svg=sanitize_svg(SVG))
        make_land(project, shape_id="a-l1", notes="NOTA PRIVADA")
        response = self.client.get(reverse("public_projects:detail", args=[project.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-shape-id="a-l1"')
        self.assertContains(response, 'data-whatsapp="5492342123456"')
        self.assertContains(response, 'data-has-map="1"')
        self.assertNotContains(response, "NOTA PRIVADA")

    def test_page_without_svg_falls_back_to_list(self):
        project = make_project(is_public=True)
        make_land(project)
        response = self.client.get(reverse("public_projects:detail", args=[project.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-has-map="0"')
        self.assertContains(response, "lotmap.no_map")
        self.assertNotContains(response, "lotmap__viewport")


class ProjectSlugTests(TestCase):
    def test_slug_generated_and_unique(self):
        first = make_project(name="Las Magnolias")
        second = make_project(name="Las magnolias!")
        self.assertEqual(first.slug, "las-magnolias")
        self.assertEqual(second.slug, "las-magnolias-2")


class ProjectAdminTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("admin", "admin@example.com", "x")
        self.client.force_login(self.user)
        self.project = make_project()
        make_land(self.project, shape_id="a-l1")
        make_land(self.project, manual_id="7", shape_id="")

    def post_svg(self, content, name="plano.svg"):
        url = reverse("admin:projects_project_change", args=[self.project.pk])
        return self.client.post(url, {
            "name": self.project.name, "start_date": "2026-01-01", "slug": self.project.slug,
            "is_public": "on", "map_svg_file": SimpleUploadedFile(name, content.encode(), "image/svg+xml"),
        }, follow=True)

    def test_upload_sanitizes_and_warns_without_blocking(self):
        response = self.post_svg(SVG.replace("<g id=\"plano\">", "<script>alert(1)</script><g id=\"plano\">"))
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertIn('data-shape-id="a-l1"', self.project.map_svg)
        self.assertNotIn("script", self.project.map_svg)
        messages = [str(m) for m in response.context["messages"]]
        self.assertTrue(any("advertencias" in m for m in messages))

    def test_invalid_upload_is_rejected(self):
        response = self.post_svg("<html></html>")
        self.assertContains(response, "El elemento raíz del archivo debe ser")
        self.project.refresh_from_db()
        self.assertEqual(self.project.map_svg, "")

    def test_change_page_shows_report(self):
        self.project.map_svg = sanitize_svg(SVG)
        self.project.save()
        response = self.client.get(reverse("admin:projects_project_change", args=[self.project.pk]))
        self.assertContains(response, "Formas sin terreno asociado")
        self.assertContains(response, "a-l2")
        self.assertContains(response, "Terrenos sin forma en el plano")


class LandAdminTests(TestCase):
    def test_changelist_edits_shape_id_and_rejects_duplicates(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "x")
        self.client.force_login(user)
        project = make_project()
        first = make_land(project, manual_id="1", shape_id="a-l1")
        second = make_land(project, manual_id="2")
        url = reverse("admin:lands_land_changelist")
        self.assertEqual(self.client.get(url).status_code, 200)

        def post(shape_id):
            return self.client.post(url, {
                "form-TOTAL_FORMS": "2", "form-INITIAL_FORMS": "2",
                "form-0-id": first.pk, "form-0-shape_id": "a-l1",
                "form-1-id": second.pk, "form-1-shape_id": shape_id,
                "_save": "Guardar",
            })

        post("a-l1")
        second.refresh_from_db()
        self.assertEqual(second.shape_id, "")
        post("a-l2")
        second.refresh_from_db()
        self.assertEqual(second.shape_id, "a-l2")

        ## The same new id typed in two rows of one save
        self.client.post(url, {
            "form-TOTAL_FORMS": "2", "form-INITIAL_FORMS": "2",
            "form-0-id": first.pk, "form-0-shape_id": "x-1",
            "form-1-id": second.pk, "form-1-shape_id": "x-1",
            "_save": "Guardar",
        })
        first.refresh_from_db()
        self.assertEqual(first.shape_id, "a-l1")


class LandingTests(TestCase):
    def setUp(self):
        self.public = make_project(name="Público", is_public=True, map_svg=sanitize_svg(SVG))
        make_land(self.public, manual_id="1", shape_id="a-l1", notes="NOTA PRIVADA")
        make_land(self.public, manual_id="2", status="reserved", price=Decimal("12000"))
        make_land(self.public, manual_id="3", status="sold", price=Decimal("77777"))
        make_land(self.public, manual_id="4", status="not_available", price=Decimal("88888"))
        self.private = make_project(name="Privado Oculto", is_public=False)
        make_land(self.private, manual_id="9", price=Decimal("55555"))

    def test_lists_only_public_projects(self):
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("public_projects:detail", args=[self.public.slug]))
        self.assertContains(response, reverse("public_projects:plan_svg", args=[self.public.slug]))
        self.assertNotContains(response, "Privado Oculto")
        card = response.context["project_cards"][0]
        self.assertEqual((card["total_lots"], card["available_lots"], card["min_price"]), (4, 1, 15000.0))

    def test_finder_has_only_available_and_reserved_public_lots(self):
        response = self.client.get(reverse("landing"))
        lots = response.context["finder_lots"]
        self.assertEqual(sorted(lot["number"] for lot in lots), ["1", "2"])
        self.assertEqual({lot["project"] for lot in lots}, {self.public.slug})
        body = response.content.decode()
        for secret in ("NOTA PRIVADA", "77777", "88888", "55555"):
            self.assertNotIn(secret, body)

    def test_empty_state_without_public_projects(self):
        Project.objects.update(is_public=False)
        response = self.client.get(reverse("landing"))
        self.assertContains(response, "projects.empty")
        self.assertEqual(response.context["finder_lots"], [])

    def test_plan_image(self):
        url = reverse("public_projects:plan_svg", args=[self.public.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/svg+xml; charset=utf-8")
        self.assertIn("default-src 'none'", response["Content-Security-Policy"])
        self.assertEqual(self.client.get(reverse("public_projects:plan_svg", args=[self.private.slug])).status_code, 404)
        self.public.map_svg = ""
        self.public.save()
        self.assertEqual(self.client.get(url).status_code, 404)
