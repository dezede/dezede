from django.test import TestCase
from django.urls import reverse

__all__ = ('EvenementListDatesTestCase',)


class EvenementListDatesTestCase(TestCase):
    def test_out_of_range_years_are_ignored(self):
        url = reverse('evenements')
        for dates in ((1, 715528579), (5, 900), (0, 2000), (-5, 2000)):
            response = self.client.get(
                url, {'dates_0': dates[0], 'dates_1': dates[1]})
            self.assertEqual(response.status_code, 200, dates)
