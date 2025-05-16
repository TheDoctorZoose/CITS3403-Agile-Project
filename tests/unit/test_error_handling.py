import unittest

from tests.unit.conftest import TestBase


class TestErrorHandling(TestBase):

    def test_404_error(self, _, client):
        """Test handling of 404 Not Found error"""
        response  = client.get('/nonexistent-route')
        self.assertEqual(404, response.status_code)
        self.assertIn(b'404 Not Found', response.data)

    def test_403_error(self, _, client):
        """Test handling of 403 Forbidden error"""
        response = client.get('/profile/9999')
        self.assertEqual(403, response.status_code)
        self.assertIn(b'403 Forbidden', response.data)

if __name__ == '__main__':
    unittest.main()
