"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

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


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        

        self.u1 = User.signup("testing1", "test1@test.com", "password", None)
        self.u2 = User.signup("testing2", "test2@test.com", "password", None)
        self.u3 = User.signup("testing3", "test3@test.com", "password", None)
        self.u4 = User.signup("testing4", "test4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp
    
    def test_users_view(self):
        """Test  view full list of users"""
        with self.client as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testuser.username, str(resp.data))
            self.assertIn(self.u1.username, str(resp.data))
            self.assertIn(self.u2.username, str(resp.data))
            self.assertIn(self.u3.username, str(resp.data))
            self.assertIn(self.u4.username, str(resp.data))

           
    def test_users_search(self):
        """Test view when username is search"""
        with self.client as c:
            resp = c.get("/users?q=testing")
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(self.testuser.username, str(resp.data))
            self.assertIn(self.u1.username, str(resp.data))
            self.assertIn(self.u2.username, str(resp.data))
            self.assertIn(self.u3.username, str(resp.data))
            self.assertIn(self.u4.username, str(resp.data))

    def test_user_profile(self):
        """Test individual user profil view """

        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn(self.testuser.username, html)
            # import pdb
            # pdb.set_trace()

    def setup_likes(self):
        """Setting up user likes to test like message related views"""

        m1 = Message(text="testuser's own warble1", user_id=self.testuser.id)
        m2 = Message(text="testuser's own warble2", user_id=self.testuser.id)
        m3 = Message(text="likable warble", user_id=self.u1.id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        like_warble = Likes(user_id=self.testuser.id, message_id=m3.id)
        db.session.add(like_warble)
        db.session.commit()

    
    def setup_followers(self):
        """Setting up user followers to test follower/following views"""

        f1 = Follows(user_being_followed_id=self.u1.id, user_following_id= self.testuser.id)
        f2 = Follows(user_being_followed_id=self.u2.id, user_following_id= self.testuser.id)
        f3 = Follows(user_being_followed_id=self.testuser.id, user_following_id= self.u3.id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()
    
    def test_user_profile_features(self):
        """Test individual user profil view with likes, messages and follower/following"""
        self.setup_likes()
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f"/users/{self.testuser.id}")
            # import pdb
            # pdb.set_trace()
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn(self.testuser.username, html)
            # messages, following, followers, likes count accordingly
            self.assertIn(f'<a href="/users/{self.testuser.id}">2</a>', html)
            self.assertIn(f'<a href="/users/{self.testuser.id}/following">2</a>', html)
            self.assertIn(f'<a href="/users/{self.testuser.id}/followers">1</a>', html)
            self.assertIn(f'<a href="/users/{self.testuser.id}/likes">1</a>', html)
    
    def test_show_following(self):
        """Testing user's list of following user view"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f"/users/{self.testuser.id}/following")
            # import pdb
            # pdb.set_trace()
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn(self.u1.username, html)
            self.assertIn(self.u2.username, html)
            self.assertNotIn(self.u3.username, html)

    def test_show_followers(self):
        """Testing user's list of following user view"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f"/users/{self.testuser.id}/followers")
            # import pdb
            # pdb.set_trace()
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertNotIn(self.u1.username, html)
            self.assertNotIn(self.u2.username, html)
            self.assertIn(self.u3.username, html)
    
    def test_show_following_unauthenticated(self):
        """Testing user's list of following user view fail without loggedin user"""
        self.setup_followers()
        with self.client as c:
            
            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', str(resp.data))    

    def test_show_followers_unauthenticated(self):
        """Testing user's list of following user view fail without loggedin user"""
        self.setup_followers()
        with self.client as c:
            
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', str(resp.data))    

    def test_follow_user(self):
        """Testing user's list of following user view"""
        
        self.setup_followers()        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            resp = c.post(f"/users/follow/{self.u4.id}", follow_redirects=True)
            # import pdb
            # pdb.set_trace()
           
            self.assertEqual(resp.status_code, 200)
            new_following = Follows.query.filter(Follows.user_following_id  == self.testuser.id).all()
            self.assertEqual(len(new_following), 3)
    
    def test_follow_user_unauthenticated(self):
        """Testing user's list of following user view"""
              
        with self.client as c:
            
            resp = c.post(f"/users/follow/{self.u4.id}", follow_redirects=True)
            # import pdb
            # pdb.set_trace()
           
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', str(resp.data))    
