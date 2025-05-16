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

This project uses `pytest` for all testing.

### Run all tests

```shell
pytest
```

### Tun a specific suite

```shell
pytest tests/unit/
```

### Selenium (end-to-end) tests

> make sure the Flask server is running before running these tests

```shell
pytest tests/selenium/
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
