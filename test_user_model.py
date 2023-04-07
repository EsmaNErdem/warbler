"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['TESTING'] = True
        self.client = app.test_client()
        db.drop_all()
        db.create_all()

        user1 = User(
            email='user1@example.com',
            username='user1',
            password='password1'
        )
        user2 = User(
            email='user2@example.com',
            username='user2',
            password='password2'
        )
        # we don't know id number that are being assigned so we cannot query/call them by their id.
        # this is given solution approach
            # u1 = User.signup("test1", "email1@email.com", "password", None)
            # uid1 = 1111
            # u1.id = uid1

            # u2 = User.signup("test2", "email2@email.com", "password", None)
            # uid2 = 2222
            # u2.id = uid2

            # db.session.commit()

            # u1 = User.query.get(uid1)
            # u2 = User.query.get(uid2)

            # self.u1 = u1
            # self.uid1 = uid1

            # self.u2 = u2
            # self.uid2 = uid2

        db.session.add_all([user1, user2])
        db.session.commit()

        u1 = User.query.filter_by(username='user1').one()
        u2 = User.query.filter_by(username='user2').one()
        self.u1 = u1
        self.u2 = u2

    def tearDown(self):
        """Runs after every test"""
        # super().tearDown() calls the tearDown() method defined in the parent class (unittest.TestCase). This allows the parent class to perform any necessary teardown steps before the tearDown() method defined in the subclass is executed.
        res = super().tearDown()
        db.session.rollback()
        return res        


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

# follow tests:

    def test_user_follows(self):
        """Tests if user model's follow userfeature works"""
        # u1 follows u2
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(self.u1.followers, [])
        self.assertEqual(self.u2.following, [])

    def test_user_is_following(self):
        """Tests if user model's follow userfeature works"""
        # u1 follows u2
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_user_is_followed_by(self):
        """Tests if user model's follow userfeature works"""
        # u1 follows u2
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))
 
# Signup
    def test_user_signup(self):
        """Test users with correct credentials can sign up properly."""
        
        user1 = User.signup(username='testuser', email='testuser@example.com', password='password', image_url=None)
        db.session.add(user1)
        db.session.commit()

        user = User.query.filter_by(username='testuser').one()

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertNotEqual(user.password, 'password')
        self.assertTrue(user.password.startswith('$2b$'))

    def test_invalid_user_signup(self):
        """Test users with incorrect credentials cannot sign up properly."""
        with self.assertRaises(ValueError):
            User.signup('testuser', 'testuser@example.com', None, None)

    def test_invalid_username(self):
        """Tests users fialing to signup with an username"""

        with self.assertRaises(IntegrityError):
            User.signup(None, 'testuser@example.com', 'password', None)
            db.session.commit()

    def test_invalid_email(self):
        """Tests users faiiling to signup without an email"""
        with self.assertRaises(IntegrityError):
            User.signup(username='testuser', email=None, password='password', image_url=None)
            db.session.commit()
        
    
    def test_unique_email_error(self):
        """Test that a user with the same email cannot be added again."""
        
        user1 = User.signup(username='testuser1', email='testuser@example.com', password='password', image_url=None)
        db.session.add(user1)
        db.session.commit()
        
        user2 = User.signup(username='testuser2', email='testuser@example.com', password='password', image_url=None)
        with self.assertRaises(IntegrityError):
            db.session.add(user2)
            db.session.commit()


# Login
# -------------------hashing is not working
# ERROR: test_valid_login (test_user_model.UserModelTestCase)
# Tests if the user with correct credential can sign in
# ----------------------------------------------------------------------
# Traceback (most recent call last):
#   File "/home/esma/springboard/projects/warbler/test_user_model.py", line 192, in test_valid_login
#     u = User.authenticate(self.u1.username, 'password1')
#   File "/home/esma/springboard/projects/warbler/models.py", line 166, in authenticate
#     is_auth = bcrypt.check_password_hash(user.password, password)
#   File "/home/esma/springboard/projects/warbler/venv/lib/python3.10/site-packages/flask_bcrypt.py", line 225, in check_password_hash
#     return hmac.compare_digest(bcrypt.hashpw(password, pw_hash), pw_hash)
#   File "/home/esma/springboard/projects/warbler/venv/lib/python3.10/site-packages/bcrypt/__init__.py", line 84, in hashpw
#     return _bcrypt.hashpass(password, salt)
# ValueError: Invalid salt

    def test_valid_login(self):
        """Tests if the user with correct credential can sign in"""
        u = User.authenticate(self.u1.username, 'password1')
        # import pdb
        # pdb.set_trace()
        
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u1.id)



