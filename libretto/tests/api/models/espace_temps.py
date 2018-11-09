from django.test import TestCase
from django.test.utils import override_settings
from django.utils.encoding import force_text
from libretto.api import build_ancrage
from libretto.models import Evenement


@override_settings(CACHALOT_ENABLED=False)
class BuildAncrageTestCase(TestCase):
    cleans_up_after_itself = True

    def setUp(self):
        self.evenement = Evenement()
        self.ancrage = self.evenement.debut

    def test_lieu_with_parent_and_date_approx(self):
        txt = 'Paris, Concert Spirituel, ca. 1852'
        out = 'Concert Spirituel, ca. 1852'

        with self.assertNumQueries(12):
            build_ancrage(self.ancrage, txt, commit=False)
        self.assertEqual(force_text(self.ancrage), out)

    def test_lieu_and_date(self):
        txt = 'Concert Spirituel, 5/7/1852'
        out = 'Concert Spirituel, 5 juillet 1852'

        with self.assertNumQueries(9):
            build_ancrage(self.ancrage, txt, commit=False)
        self.assertEqual(force_text(self.ancrage), out)

        with self.assertNumQueries(17):
            build_ancrage(self.ancrage, txt)
        self.assertEqual(force_text(self.ancrage), out)

    def test_lieu_and_date_iso(self):
        txt = 'Concert Spirituel, 1852-7-5'
        out = 'Concert Spirituel, 5 juillet 1852'

        with self.assertNumQueries(9):
            build_ancrage(self.ancrage, txt, commit=False)
        self.assertEqual(force_text(self.ancrage), out)

        with self.assertNumQueries(17):
            build_ancrage(self.ancrage, txt)
        self.assertEqual(force_text(self.ancrage), out)

    def test_lieu_and_date_fr(self):
        txt = 'Concert Spirituel, 5 juillet 1852'

        with self.assertNumQueries(9):
            build_ancrage(self.ancrage, txt, commit=False)
        self.assertEqual(force_text(self.ancrage), txt)

        with self.assertNumQueries(17):
            build_ancrage(self.ancrage, txt)
        self.assertEqual(force_text(self.ancrage), txt)

    def test_date_only(self):
        with self.assertNumQueries(0):
            build_ancrage(self.ancrage, '5/7/1852', commit=False)
        self.assertEqual(force_text(self.ancrage), '5 juillet 1852')

        with self.assertNumQueries(1):
            build_ancrage(self.ancrage, '5/7/1852')
        self.assertEqual(force_text(self.ancrage), '5 juillet 1852')

    def test_date_approx_only(self):
        with self.assertNumQueries(0):
            build_ancrage(self.ancrage, '18..', commit=False)
        self.assertEqual(force_text(self.ancrage), '18..')
