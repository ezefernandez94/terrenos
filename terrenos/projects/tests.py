from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.test import RequestFactory, TestCase
from django.urls import NoReverseMatch, reverse

from lands.models import Land
from sales.models import Sale

from faqs.models import Faq
from projects.forms import ProjectForm
from projects.models import Project


class InstallmentPlansTests(TestCase):
    def test_form_saves_sorted_plans(self):
        form = ProjectForm({"name": "Loteo", "status": "in_progress", "start_date": "2026-01-01", "installment_plans": ["36", "12"]})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().installment_plans, [12, 36])

    def test_form_rejects_non_multiple_of_12(self):
        form = ProjectForm({"name": "Loteo", "status": "in_progress", "start_date": "2026-01-01", "installment_plans": ["18"]})
        self.assertFalse(form.is_valid())


class PublicPagesTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Loteo", start_date="2026-01-01", is_public=True,
                                              installment_plans=[12, 24, 36])

    def test_landing_card_shows_plans_and_general_faqs(self):
        Faq.objects.create(question="¿Pregunta general?", answer="Respuesta", question_en="General?", answer_en="Answer")
        Faq.objects.create(question="¿Del proyecto?", answer="No va en la landing", project=self.project)
        Faq.objects.create(question="¿Borrador?", answer="No publicada", is_published=False)

        response = self.client.get(reverse("landing"))

        self.assertContains(response, "Tenemos planes de financiación en 12, 24 y 36 cuotas")
        self.assertContains(response, '{"list": [12, 24, 36]}')
        self.assertContains(response, "¿Pregunta general?")
        self.assertContains(response, 'data-faq-en="General?"')
        self.assertNotContains(response, "¿Del proyecto?")
        self.assertNotContains(response, "¿Borrador?")
        self.assertContains(response, 'href="#preguntas"')

    def test_project_page_shows_plans_and_its_faqs(self):
        Faq.objects.create(question="¿Tiene gas?", answer="</script><b>sí</b>", project=self.project)

        response = self.client.get(reverse("public_projects:detail", args=[self.project.slug]))

        self.assertContains(response, "Tenemos planes de financiación en 12, 24 y 36 cuotas")
        self.assertContains(response, "¿Tiene gas?")
        self.assertContains(response, '"@type": "FAQPage"')
        ## User text cannot break out of the JSON-LD <script>
        self.assertNotContains(response, "</script><b>")

    def test_no_plans_no_faqs_renders_nothing_extra(self):
        self.project.installment_plans = []
        self.project.save()
        response = self.client.get(reverse("public_projects:detail", args=[self.project.slug]))
        self.assertNotContains(response, "planes de financiación en")
        self.assertNotContains(response, 'id="preguntas"')


class ProjectLifecycleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("admin")
        self.client.force_login(self.user)
        self.active = Project.objects.create(name="Activo", start_date="2026-01-01")
        self.finished = Project.objects.create(name="Cerrado", start_date="2025-01-01", status=Project.FINISHED)
        self.active_land = Land.objects.create(manual_id="1", block="A", length=10, width=30, project=self.active)
        self.finished_land = Land.objects.create(manual_id="9", block="Z", length=10, width=30, project=self.finished,
                                                 status="sold")

    def test_projects_cannot_be_deleted(self):
        with self.assertRaises(NoReverseMatch):
            reverse("projects:delete", args=[self.active.id])
        request = RequestFactory().get("/")
        request.user = self.user
        self.assertFalse(admin.site._registry[Project].has_delete_permission(request, self.active))
        ## Backstop for the shell: the lands are protected
        with self.assertRaises(ProtectedError):
            self.active.delete()

    def test_new_projects_default_to_in_progress(self):
        self.assertEqual(self.active.status, Project.IN_PROGRESS)

    def test_lands_index_hides_finished_projects(self):
        response = self.client.get(reverse("lands:index"))
        self.assertEqual([g["project"] for g in response.context["groups"]], [self.active])
        self.assertContains(response, "?finalizados=1")

        response = self.client.get(reverse("lands:index"), {"finalizados": "1"})
        self.assertEqual([g["project"] for g in response.context["groups"]], [self.finished, self.active])

    def test_sales_index_hides_finished_projects(self):
        Sale.objects.create(land=self.active_land, sale_date="2026-01-01", sale_price=100)
        Sale.objects.create(land=self.finished_land, sale_date="2025-01-01", sale_price=100)

        response = self.client.get(reverse("sales:index"))
        self.assertEqual([s.land for s in response.context["sales"]], [self.active_land])

        response = self.client.get(reverse("sales:index"), {"finalizados": "1"})
        self.assertEqual(len(response.context["sales"]), 2)


class CreatePagesRequireLoginTests(TestCase):
    def test_every_create_page_redirects_to_login(self):
        ## Regression: the CreateView classes had no login check
        for app in ["expense_type_details", "expense_types", "expenses", "faqs", "investments", "lands", "payers",
                    "payment_receivers", "people", "projects", "sales", "sales_summary", "sellers"]:
            with self.subTest(app=app):
                response = self.client.get(reverse(f"{app}:create"))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login"), response["Location"])


class PublicStatusTests(TestCase):
    def setUp(self):
        def project(name, status, start):
            p = Project.objects.create(name=name, start_date=start, is_public=True, status=status,
                                       installment_plans=[12])
            Land.objects.create(manual_id="1", block="A", length=10, width=30, project=p, price=1000)
            return p
        self.finished = project("Terminado", Project.FINISHED, "2024-01-01")
        self.active = project("En venta", Project.IN_PROGRESS, "2026-01-01")
        self.soon = project("Futuro", Project.COMING_SOON, "2027-01-01")

    def test_landing_groups_projects_by_status(self):
        response = self.client.get(reverse("landing"))
        ctx = response.context
        ## On sale first, then finished; coming soon only in "Próximos"
        self.assertEqual([c["project"] for c in ctx["project_cards"]], [self.active, self.finished])
        self.assertEqual([c["project"] for c in ctx["upcoming_cards"]], [self.soon])
        self.assertEqual(ctx["finder_projects"], [self.active])
        self.assertEqual({lot["project"] for lot in ctx["finder_lots"]}, {self.active.slug})

        self.assertContains(response, "Finalizado</span>")
        self.assertContains(response, reverse("public_projects:detail", args=[self.active.slug]))
        self.assertNotContains(response, reverse("public_projects:detail", args=[self.finished.slug]))
        self.assertNotContains(response, reverse("public_projects:detail", args=[self.soon.slug]))
        self.assertContains(response, "Quiero que me avisen")
        ## The old hardcoded sample projects are gone
        self.assertNotContains(response, "Ribera Norte")

    def test_finished_and_coming_soon_pages_are_blocked(self):
        for project in (self.finished, self.soon):
            with self.subTest(project=project.name):
                self.assertEqual(self.client.get(reverse("public_projects:detail", args=[project.slug])).status_code, 404)
                self.assertEqual(self.client.get(reverse("public_projects:map_data", args=[project.slug])).status_code, 404)
        self.assertEqual(self.client.get(reverse("public_projects:detail", args=[self.active.slug])).status_code, 200)

    def test_upcoming_section_hidden_without_coming_soon_projects(self):
        self.soon.status = Project.IN_PROGRESS
        self.soon.save()
        response = self.client.get(reverse("landing"))
        self.assertNotContains(response, 'id="proximos"')
        self.assertNotContains(response, 'href="#proximos"')
