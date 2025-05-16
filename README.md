# (Name of App) - CITS3403 Group Project

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
TBA

## Application Tests

Before running tests, make sure you have the requirements installed:

```sh
pip install -r requirements.txt
```

To run the unit test suit:

```sh
python -m unittest discover -s tests/unit
```

To test simulated user behaviour using selenium, activate the Flask app and run

```sh
# Start the server in one terminal
flask run

# Then, in a new terminal:
python -m unittest discover -s tests/selenium
```





## Features
### Upload Data
- Use the interface to manually enter in relevant board game data
- Batch import CSV or JSON data

### Visualise Data
- View your statistics in the form of summaries and charts
- View other user's statistics that have been shared with you

### Share Data
- Search for other users you know and share specific visualisations and statistics with them
