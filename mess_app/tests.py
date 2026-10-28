from django.test import TestCase

class HomePageTest(TestCase):
    def test_home_page_responds(self):
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 302])
