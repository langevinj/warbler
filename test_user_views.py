"""User View tests."""

from app import app, CURR_USER_KEY, do_logout, IntegrityError
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app


# Create our tables

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

        self.testuser_id = 9999
        self.testuser.id = self.testuser_id

        db.session.commit()
    
    def test_show_following(self):
        u2 = User.signup("testuser2", "test2@test.com", password="password", image_url=None)
        u2.id = 123456
        db.session.add(u2)
        db.session.commit()

        test_user = User.query.get(123456)
        test_user.following.append(self.testuser)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/users/123456/following")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", str(resp.data))
            self.assertTrue(test_user.is_following(self.testuser))
    
    def test_users_followers(self):
        u2 = User.signup("testuser2", "test2@test.com",
                         password="password", image_url=None)
        u2.id = 123456
        db.session.add(u2)
        db.session.commit()

        test_user = User.query.get(123456)
        test_user.followers.append(self.testuser)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/users/123456/followers")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", str(resp.data))
            self.assertTrue(test_user.is_followed_by(self.testuser))
    
    def test_users(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", str(resp.data))

    def test_users_show(self):
        """Show a users profile"""
        with self.client as c:
            resp = c.get(f"/users/9999")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", str(resp.data))
            self.assertIn("Likes", str(resp.data))

    #Following/follower tests
    ######
    def test_logged_out_view_following(self):
        u2 = User.signup("testuser2", "test2@test.com",
                         password="password", image_url=None)
        u2.id = 123456
        db.session.add(u2)
        db.session.commit()

        test_user = User.query.get(123456)
        test_user.followers.append(self.testuser)

        with self.client as c:
            resp = c.get("/users/123456/following", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_logged_out_view_followers(self):
        u2 = User.signup("testuser2", "test2@test.com",
                         password="password", image_url=None)
        u2.id = 123456
        db.session.add(u2)
        db.session.commit()

        test_user = User.query.get(123456)
        test_user.following.append(self.testuser)

        with self.client as c:
            resp = c.get("/users/123456/followers", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    


        


    



    
