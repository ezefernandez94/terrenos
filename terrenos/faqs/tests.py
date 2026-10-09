from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from faqs.models import Faq
from projects.models import Project


class FaqViewsTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user("tester"))
        self.project = Project.objects.create(name="Loteo", start_date="2026-01-01")

    def test_create_with_only_spanish(self):
        response = self.client.post(reverse("faqs:create"), {
            "project": self.project.id, "question": "¿Tiene luz?", "answer": "Sí.", "order": 0, "is_published": "on",
        })
        self.assertRedirects(response, reverse("faqs:index"))
        self.assertEqual(Faq.objects.get().project, self.project)

    def test_half_translation_is_rejected(self):
        response = self.client.post(reverse("faqs:create"), {
            "question": "¿Escritura?", "answer": "Sí.", "question_en": "Deed?", "order": 0,
        })
        self.assertContains(response, "Completá la respuesta en inglés")
        self.assertFalse(Faq.objects.exists())

    def test_index_edit_and_delete(self):
        faq = Faq.objects.create(question="¿General?", answer="Sí.")
        self.assertContains(self.client.get(reverse("faqs:index")), "¿General?")

        self.client.post(reverse("faqs:edit", args=[faq.id]), {"question": "¿Editada?", "answer": "Sí.", "order": 1})
        faq.refresh_from_db()
        self.assertEqual(faq.question, "¿Editada?")

        self.assertRedirects(self.client.post(reverse("faqs:delete", args=[faq.id])), reverse("faqs:index"))
        self.assertFalse(Faq.objects.exists())

    def test_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("faqs:create")).status_code, 302)
        self.assertEqual(self.client.get(reverse("faqs:index")).status_code, 302)
