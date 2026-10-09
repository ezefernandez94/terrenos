from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from lands.models import Land
from people.models import People
from people_to_lands.models import PeopleToLands
from projects.models import Project


class PeopleDeleteTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user("tester"))
        self.person = People.objects.create(name="Ana")

    def test_confirmation_page_renders(self):
        ## Regression: the template reversed people:detail with an undefined `seller.id` (500 in prod)
        response = self.client.get(reverse("people:delete", args=[self.person.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Si, eliminar")

    def test_post_deletes_and_redirects(self):
        response = self.client.post(reverse("people:delete", args=[self.person.id]))
        self.assertRedirects(response, reverse("people:index"))
        self.assertFalse(People.objects.filter(pk=self.person.pk).exists())

    def test_owner_of_a_land_cannot_be_deleted(self):
        project = Project.objects.create(name="Loteo", start_date="2026-01-01")
        land = Land.objects.create(manual_id="1", block="A", length=10, width=30, project=project)
        PeopleToLands.objects.create(person=self.person, land=land)

        response = self.client.post(reverse("people:delete", args=[self.person.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No se puede eliminar")
        self.assertTrue(People.objects.filter(pk=self.person.pk).exists())
