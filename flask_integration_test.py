import unittest
from flask_app import create_app
from utils.db import init_db

class TestFlaskIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_routes(self):
        # We just want to ensure 200 or 302 (redirect to login)
        routes = [
            '/',
            '/auth/login',
            '/auth/signup',
            '/dashboard/',
            '/meetings/',
            '/documents/',
            '/assistant/',
            '/reports/',
            '/analytics/',
            '/profile/',
            '/email/',
            '/risk/',
            '/tasks/',
            '/insights/',
            '/weekly/',
            '/about/',
            '/executive/'
        ]
        
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertIn(response.status_code, [200, 302])

if __name__ == '__main__':
    unittest.main()
