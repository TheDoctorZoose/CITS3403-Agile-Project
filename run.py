import os
import threading
import time

from flask_migrate import upgrade, migrate, init

from app import create_app

app = create_app()


def run_selenium_tests():
    time.sleep(3)
    run_selenium_tests()


def run_migrations():
    with app.app_context():
        try:
            # Create migrations folder if not exists
            if not os.path.exists("migrations"):
                init()
            migrate(message="Auto migration")
        except Exception as e:
            print(f"[Migration warning] {e}")  # Ignore "No changes detected"
        upgrade()


if __name__ == "__main__":

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        run_migrations()  # Run migrations before server starts
        threading.Thread(target=run_selenium_tests).start()

    app.run(debug=True)
