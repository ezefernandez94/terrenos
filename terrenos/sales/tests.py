from decimal import Decimal
from unittest import mock

import requests

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from lands.models import Land
from people.models import People
from projects.models import Project
from sales.models import Sale
from sales_summary.models import SaleSummary

PREFIX = "peopletolands_set"


def management(total):
    return {f"{PREFIX}-TOTAL_FORMS": str(total), f"{PREFIX}-INITIAL_FORMS": "0",
            f"{PREFIX}-MIN_NUM_FORMS": "0", f"{PREFIX}-MAX_NUM_FORMS": "1000"}


## SaleSummary.save() fetches an exchange rate; tests never touch the network
@mock.patch("sales_summary.models.requests.get", side_effect=requests.ConnectionError("no network in tests"))
class SellLandTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user("tester"))
        self.project = Project.objects.create(name="Loteo", start_date="2026-01-01")
        self.land = Land.objects.create(manual_id="1", block="A", length=10, width=30, project=self.project)
        self.url = reverse("sales:sell_land", args=[self.land.id])

    def sale_data(self, **overrides):
        data = {"land": self.land.id, "sale_date": "2026-10-01", "sale_price": "10000", "n_payments": "24",
                "notes": "", "down_payment": "", "down_payment_option": "", "down_payment_date": ""}
        data.update(overrides)
        return data

    def new_buyer(self, index, name="Juan", phone="", **extra):
        row = {f"{PREFIX}-{index}-create_new_person": "on", f"{PREFIX}-{index}-new_name": name,
               f"{PREFIX}-{index}-new_phone": phone, f"{PREFIX}-{index}-notes": "nota"}
        row.update({f"{PREFIX}-{index}-{k}": v for k, v in extra.items()})
        return row

    def test_new_buyer_without_phone_creates_one_person(self, _get):
        ## Regression: the phone was required but the error (about a "documento") was never shown
        response = self.client.post(self.url, {**self.sale_data(), **management(1), **self.new_buyer(0)})

        sale = Sale.objects.get(land=self.land)
        self.assertRedirects(response, reverse("sales:detail", args=[sale.id]))
        ## Regression: clean() and save() each created the person
        self.assertEqual(People.objects.filter(name="Juan").count(), 1)
        self.assertEqual(self.land.peopletolands_set.get().person.name, "Juan")
        self.land.refresh_from_db()
        self.assertTrue(self.land.is_sold)

    def test_row_errors_are_shown(self, _get):
        response = self.client.post(self.url, {**self.sale_data(), **management(1), **self.new_buyer(0, name="")})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ingresá el nombre de la nueva persona.")
        self.assertFalse(Sale.objects.exists())
        self.assertFalse(People.objects.exists())

    def test_removed_and_blank_rows_are_ignored(self, _get):
        existing = People.objects.create(name="Existente")
        data = {**self.sale_data(), **management(3),
                f"{PREFIX}-0-person": str(existing.id),
                **self.new_buyer(1, name="Borrado", DELETE="on"),
                f"{PREFIX}-2-person": "", f"{PREFIX}-2-notes": ""}

        self.client.post(self.url, data)

        self.assertEqual([o.person for o in self.land.peopletolands_set.all()], [existing])
        self.assertFalse(People.objects.filter(name="Borrado").exists())

    def test_down_payment_creates_initial_payment_summary(self, _get):
        data = {**self.sale_data(down_payment="2000", down_payment_option="usd"), **management(1), **self.new_buyer(0)}
        self.client.post(self.url, data)

        sale = Sale.objects.get(land=self.land)
        self.assertEqual(sale.financed_amount, Decimal("8000"))
        self.assertEqual(sale.installment_amount, Decimal("333.33"))
        summary = sale.salesummary_set.get()
        self.assertEqual((summary.type, summary.amount, summary.payment_option), ("initial_payment", Decimal("2000"), "usd"))
        self.assertEqual(str(summary.date), "2026-10-01")
        ## The exchange-rate API failed: the payment is still saved, with the fallback rate
        self.assertEqual(summary.exchange_rate, Decimal("1"))

    def test_down_payment_must_be_less_than_price(self, _get):
        data = {**self.sale_data(down_payment="10000", down_payment_option="usd"), **management(1), **self.new_buyer(0)}
        response = self.client.post(self.url, data)

        self.assertContains(response, "El anticipo debe ser menor al precio de venta.")
        self.assertFalse(Sale.objects.exists())

    def test_down_payment_requires_payment_option(self, _get):
        data = {**self.sale_data(down_payment="1000"), **management(1), **self.new_buyer(0)}
        response = self.client.post(self.url, data)

        self.assertContains(response, "Indicá cómo se pagó el anticipo.")

    def test_edit_updates_the_existing_summary(self, _get):
        self.client.post(self.url, {**self.sale_data(down_payment="2000", down_payment_option="usd"),
                                    **management(1), **self.new_buyer(0)})
        sale = Sale.objects.get(land=self.land)

        response = self.client.post(reverse("sales:edit", args=[sale.id]),
                                    self.sale_data(down_payment="3000", down_payment_option="pesos",
                                                   down_payment_date="2026-10-05"))

        self.assertRedirects(response, reverse("sales:detail", args=[sale.id]))
        summary = sale.salesummary_set.get()
        self.assertEqual((summary.amount, summary.payment_option, str(summary.date)), (Decimal("3000"), "pesos", "2026-10-05"))

    def test_sell_page_has_same_date_link(self, _get):
        response = self.client.get(self.url)
        self.assertContains(response, "Usar la misma fecha de venta")

    def test_detail_and_summary_str(self, _get):
        self.client.post(self.url, {**self.sale_data(down_payment="2000", down_payment_option="usd"),
                                    **management(1), **self.new_buyer(0)})
        sale = Sale.objects.get(land=self.land)
        ## Regression: SaleSummary.__str__ read a non-existent self.land
        self.assertIn("Summary for", str(sale.salesummary_set.get()))
        response = self.client.get(reverse("sales:detail", args=[sale.id]))
        self.assertContains(response, "Pago Inicial")
        self.assertContains(response, "Juan")
