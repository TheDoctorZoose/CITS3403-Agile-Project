import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class FlaskSeleniumTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        self.base_url = "http://localhost:5000"

    def test_register_login_profile(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register")

        username = "testuser123"
        email = "testuser123@example.com"
        password = "test1234"

        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "confirm_password").send_keys(password + Keys.RETURN)

        time.sleep(1)

        driver.get(f"{self.base_url}/login")
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)

        time.sleep(1)

        driver.get(f"{self.base_url}/profile/1")
        time.sleep(1)

        self.assertIn("Signature", driver.page_source)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()


def run_selenium_tests():
    import unittest
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FlaskSeleniumTest)
    runner = unittest.TextTestRunner()
    runner.run(suite)
