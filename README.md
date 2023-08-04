# Warbler

## About Warbler

Warbler is a simplified Twitter clone built using Python (Python 3.10.6) and Flask for the backend. The app utilizes PostgreSQL as the database and SQLalchemy for database modeling. All forms in the app are created using WTForms. Users can sign up to access a variety of features, including posting and deleting messages, liking other people's messages, following users, and being followed by others. For certain activities, user authorization is checked to ensure security. User passwords are securely saved using bcrypt for added protection. Additionally, the app includes comprehensive error handling and detailed documentation to enhance the user experience and provide seamless navigation.

## Download and Setup Instructions

To contribute to the project, follow these download and setup instructions:

1. Create a virtual environment using Python 3.10.6:
```shell
    python3 -m venv venv
```

2. Activate the virtual environment:
```shell
    source venv/bin/activate
```

3. Install the required packages using pip:
```shell
    (venv) $ pip install -r requirements.txt
```

4. Create a PostgreSQL database for the app:
```shell
    (venv) $ createdb warbler
```

5. Seed the database with initial data:
```shell
    (venv) $ python seed.py
```
## Testing

To run the tests for the app, follow these instructions:

1. Create a separate test database:

```shell
    (venv) $ createdb warbler-test
```

2. Run unit tests for the message and user models:
```shell
    python -m unittest test_message_model.py
    python -m unittest test_user_model.py
```

3. For Flask integration tests, set the Flask environment to production:
```shell
    FLASK_ENV=production python -m unittest test_message_views.py
    FLASK_ENV=production python -m unittest test_user_views.py
```
