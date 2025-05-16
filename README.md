# Board Game Central - CITS3403 Group Project

## About
This is a data analytics web application that allows for tracking, automated analysis, and sharing of board game play data with other users of the platform.
This project was completed for the CITS3403 Agile Web Development unit at the University of Western Australia (UWA).

### Group
| Student Number | Name              | GitHub Username |
| -------------- | ----------------- | --------------- |
| 23962159       | Diarmuid O'Connor | tirednightowl   |
| 23201541       | Pengyu Lu         | MasterLu0309    |
| 21953544       | Peter Denby       | TheDoctorZoose  |
| 24242657       | Zayn Chen         | ChenZhez        |

## Usage
1. **Clone and navigate to the repository:**
   ```bash
   git clone https://github.com/TheDoctorZoose/CITS3403-Agile-Project.git
   cd <path/to/repository/>
   ```

2. **Create and activate the Virtual Environment:**
   ```bash
   python3 -m venv venv         # or `python -m venv venv` depending on your python installation
   source venv/bin/activate
   ```

3. **Install dependencies inside the Virtual Environment:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialise the database:**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Start the application:**
   ```bash
   flask run
   ```

6. **Access the app using a browser:**<br/>
   View at `http://127.0.0.1:5000` or `http://localhost:5000`

## Application Tests
TBA

## Features
### Upload Data
- Use the interface to manually enter in relevant board game data
- Batch import CSV or JSON data

### Visualise Data
- View your statistics in the form of summaries and charts
- View other user's statistics that have been shared with you

### Share Data
- Search for other users you know and share specific visualisations and statistics with them
