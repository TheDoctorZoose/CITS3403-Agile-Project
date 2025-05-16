from app import create_app
import threading
import time
import os

app = create_app()

def run_selenium_tests():
    time.sleep(3)
    import app.selenium_test
    app.selenium_test.run_selenium_tests()

if __name__ == "__main__":
   
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=run_selenium_tests).start()
    
    app.run(debug=True)