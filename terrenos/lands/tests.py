from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from lands.models import Land
from projects.models import Project


class LandIndexTests(TestCase):
    def test_one_table_per_project_with_sold_flag(self):
        self.client.force_login(User.objects.create_user("tester"))
        first = Project.objects.create(name="Primero", start_date="2026-01-01")
        second = Project.objects.create(name="Segundo", start_date="2026-02-01")
        Land.objects.create(manual_id="2", block="A", length=10, width=30, project=first, status="sold")
        Land.objects.create(manual_id="10", block="A", length=10, width=30, project=first)
        Land.objects.create(manual_id="1", block="B", length=10, width=30, project=second)
        Project.objects.create(name="Vacío", start_date="2026-03-01")

        response = self.client.get(reverse("lands:index"), {"estado": "vendidos"})

        groups = response.context["groups"]
        self.assertEqual([g["project"].name for g in groups], ["Primero", "Segundo"])
        ## Natural order: 2 before 10
        self.assertEqual([land.manual_id for land in groups[0]["lands"]], ["2", "10"])
        self.assertEqual((groups[0]["sold"], groups[0]["unsold"]), (1, 1))
        self.assertEqual(response.context["status_filter"], "vendidos")
        self.assertContains(response, 'data-sold="1"', count=1)


class LandCreatePageTests(TestCase):
    def test_create_page_renders_every_form_field(self):
        ## Regression: create.html is laid out by hand and lacked the required currency field,
        ## so creating a single land failed with an error the page never showed
        from lands.forms import LandForm
        self.client.force_login(User.objects.create_user("tester"))
        response = self.client.get(reverse("lands:create"))
        for field in LandForm().fields:
            with self.subTest(field=field):
                self.assertContains(response, f'name="{field}"')
