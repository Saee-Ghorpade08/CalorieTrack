
import unittest
import app as calorie_app


class TestCalorieTrack(unittest.TestCase):

    def setUp(self):
        calorie_app.food_logs.clear()
        self.client = calorie_app.app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CalorieTrack", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "healthy")

    def test_add_food(self):
        response = self.client.post(
            "/add",
            data={
                "name": "Oatmeal",
                "meal": "Breakfast",
                "calories": "300",
                "protein": "10",
                "carbs": "50",
                "fat": "6"
            }
        )
        self.assertEqual(response.status_code, 302)


if __name__ == "__main__":
    unittest.main()
