"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.u1 = User.signup("testing1", "test1@test.com", "password", None)
        
        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_unauthorized(self):
        """Can a message be added without user in session?"""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hellouuuuuuuuu"}, follow_redirects=True )
            
            self.assertEqual(resp.status_code, 200)
            self     .assertIn('Access unauthorized', str(resp.data))    
        
    def test_delete_message(self):
        """Can user delete their message?"""

        msg = Message(
            text = "I am test-text",
            user_id = self.testuser.id
        )
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message.query.get(msg.id)
            self.assertEqual(m, msg)

            resp = c.post(f"/messages/{msg.id}/delete",  follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            m = Message.query.get(msg.id)
            self.assertIsNone(m)

    def test_delete_message_unauthorized(self):
        """Can a message be deleted without user in session?"""
        msg = Message(
            text = "I am test-text",
            user_id = self.testuser.id
        )
        db.session.add(msg)
        db.session.commit()
        with self.client as c:
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True )
            
            m = Message.query.get(msg.id)
            self.assertEqual(m, msg)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', str(resp.data))    
            # import pdb
            # pdb.set_trace()

    def test_message_show(self):
        """Test message show view"""

        msg = Message(
            text = "Test 1.. 2.. 3..",
            user_id = self.testuser.id
        )
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            m = Message.query.get(msg.id)
            resp = c.get(f"/messages/{msg.id}")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(m.text, str(resp.data))

    def test_message_show_fail(self):
        """Test message show view fail"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/messages/99999999')

            self.assertEqual(resp.status_code, 404)

    def test_add_like(self):
        """Tests adding likes to other user warblers"""
        
        msg = Message(
            text = "Test Add Like",
            user_id = self.testuser.id
        )
        db.session.add(msg)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post(f"/messages/{msg.id}/add-like", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            likes = Likes.query.filter(Likes.user_id == self.testuser.id).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].message_id, msg.id)
            # import pdb
            # pdb.set_trace()
    def test_remove_like(self):
        """Tests removing like from a warbler"""  

        msg = Message(
            text = "Test Add Like",
            user_id = self.testuser.id
        )
        db.session.add(msg)
        db.session.commit()   

        liked_warble = Likes(user_id=self.testuser.id, message_id=msg.id)

        db.session.add(liked_warble)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post(f"/messages/{msg.id}/add-like", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            likes = Likes.query.filter(Likes.message_id == msg.id).all()
            self.assertEqual(len(likes), 0)

    def test_add_like_unauthenticated(self):
        """Tests adding likes to other user warblers"""
        
        msg = Message(
            text = "Test Add Like",
            user_id = self.testuser.id
        )
        db.session.add(msg)
        db.session.commit()
        with self.client as c:
            
            resp = c.post(f"/messages/{msg.id}/add-like", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', str(resp.data))    
            