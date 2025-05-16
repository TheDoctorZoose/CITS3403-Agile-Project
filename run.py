import os
import threading
import time

from flask_migrate import upgrade, migrate, init

from app import create_app

app = create_app()


def run_selenium_tests():
    time.sleep(3)
    from tests.selenium_tests import selenium_test

    selenium_test.run_selenium_tests()


def run_migrations():
    with app.app_context():
        try:
            if not os.path.exists("migrations"):
                init()
            migrate(message="Auto migration")
        except Exception as e:
            print(f"[Migration warning] {e}")
        upgrade()


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        run_migrations()
        threading.Thread(target=run_selenium_tests).start()

    app.run(debug=True, port=6969)
