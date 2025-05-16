# 🎲 Board Game Central - CITS3403 Group Project

## 🧩 About

Board Game Central is a full-stack data analytics web application that allows users to track, analyze, and share their board game sessions. This project was developed as part of the **CITS3403 Agile Web Development** unit at the **University of Western Australia (UWA)**.

## 👥 Team

| Student Number | Name              | GitHub Username |
| -------------- | ----------------- | --------------- |
| 23962159       | Diarmuid O'Connor | tirednightowl   |
| 23201541       | Pengyu Lu         | MasterLu0309    |
| 21953544       | Peter Denby       | TheDoctorZoose  |
| 24242657       | Zayn Chen         | ChenZhez        |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/TheDoctorZoose/CITS3403-Agile-Project.git
cd CITS3403-Agile-Project
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
# For macOS/Linux:
source venv/bin/activate
# For Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

```bash
flask db init
flask db migrate
flask db upgrade
```

### 5. Run the Application

```bash
flask run
```

Visit the app at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧪 Testing the Application

### 🔹 Unit Tests

```bash
python -m unittest discover -s tests/unit
```

### 🔹 Selenium Tests (Simulated User Behavior)

To **run Selenium tests in sync with the Flask server**, simply use the following command:

```bash
python run.py
```

This script ensures Flask and Selenium are started together in the correct order, preventing race conditions and connection errors.

---

## 📊 Features

### 🔄 Upload Data
- Manually input board game session data.
- Batch upload via CSV or JSON files.

### 👥 Forum Page
- Share entries publicly or with selected friends.
- Like, favorite, and comment on others’ posts.
- Sort posts by timestamp.

### 🧑‍💼 Profile Page
- View your own posts, liked entries, and favorites.
- Add or accept friends.
- Edit your signature to customize your profile.
- Real-time chat with friends.

### 📈 Analytics Page
- Summarizes game history with:
  - Win rates
  - First-time plays
  - Game frequency
- Visualized with pie charts, bar graphs, and timelines.

---

## 🎨 UI & Design Highlights

- **Navbar Design**: Defined in `base.html` to avoid repetition.
- **Landing Page**: Features a thematic animation and intro text to grab attention.
- **Forum Page**: Interactive entries with visibility controls, comments, and real-time updates.
- **Profile Page**: Rich user information including bio, friends, and actions.
- **Responsive Design**: All pages adapt to desktop and mobile sizes.

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, Bootstrap, JavaScript, jQuery
- **Backend**: Flask, Flask-Login, Flask-Mail, Flask-SQLAlchemy, Flask-Migrate, Flask-Sock
- **Database**: SQLite (via SQLAlchemy)
- **Testing**: `unittest`, `selenium`
- **Deployment Mode**: Flask development server (`run.py` auto-syncs test environment)

---

## ⚠️ Notes

- Make sure ChromeDriver is installed and matches your Chrome version for Selenium.
- This project is intended for development purposes. Do not use in production without configuring WSGI & security.
- **Environment Variables**: To ensure security and completeness, we use a `.env` file to store all sensitive information such as mail server credentials and secret keys. This avoids hardcoding passwords or private tokens directly in the source code.

---

## 📧 Contact

For issues or collaboration, reach out via GitHub or directly in our UWA team group.
