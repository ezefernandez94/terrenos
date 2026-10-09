from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from lands.models import Land
from projects.models import Project
from sellers.models import Seller


class SellerDeleteTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user("tester"))
        self.seller = Seller.objects.create(name="Vendedor")
        project = Project.objects.create(name="Loteo", start_date="2026-01-01")
        self.land = Land.objects.create(manual_id="1", block="A", length=10, width=30, project=project, seller=self.seller)

    def test_warns_about_the_lands_that_lose_their_seller(self):
        response = self.client.get(reverse("sellers:delete", args=[self.seller.id]))
        self.assertContains(response, "Estos terrenos van a perder el registro de quien los vendió")
        self.assertContains(response, "1 - A (Loteo)")

    def test_delete_keeps_the_lands(self):
        ## Regression: Land.seller was CASCADE, so deleting a seller deleted every land they sold
        response = self.client.post(reverse("sellers:delete", args=[self.seller.id]))
        self.assertRedirects(response, reverse("sellers:index"))
        self.land.refresh_from_db()
        self.assertIsNone(self.land.seller)
