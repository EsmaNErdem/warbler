"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Likes

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


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['TESTING'] = True
        self.client = app.test_client()
        db.drop_all()
        db.create_all()

        u = User.signup('testuser', "testing@test.com", "password", None)
        db.session.commit()

        self.u = User.query.filter_by(username='testuser').one()

    def tearDown(self):
        """Runs after every test"""
        # super().tearDown() calls the tearDown() method defined in the parent class (unittest.TestCase). This allows the parent class to perform any necessary teardown steps before the tearDown() method defined in the subclass is executed.
        res = super().tearDown()
        db.session.rollback()
        return res  

    def test_message_model(self):
        """Does basic model work?"""      
        user_id = self.u.id
        msg = Message(
            text="Testing my warbles, marbles at this point! ",
            user_id= user_id
        )
        
        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "Testing my warbles, marbles at this point! ")
    

    def test_message_likes(self):
        """Tests if model Like foreign key connected to messages works"""

        user_id = self.u.id
        msg = Message(
            text="Testing my warbles, marbles at this point! ",
            user_id= user_id
        )

        u2 = User.signup('testuser2', "testing2@test.com", "password", None)
        db.session.add_all([msg, u2])
        db.session.commit()

        u2.likes.append(msg)
        likes = Likes.query.filter(Likes.user_id == u2.id).all()
        
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].user_id, u2.id)
        self.assertEqual(likes[0].message_id, msg.id)


        # import pdb
        # pdb.set_trace()