"""Message View tests."""

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY, do_logout, IntegrityError

# Create our tables 

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
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
            
    def test_add_message_logged_out(self):
        """Is someone prevented from adding a message when logged out"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "This thing on?"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 4444444444444 #doesn't exist
            resp = c.post("/messages/new", data = {"text": "This thing on?"}, follow_redirects = True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_message_show(self):
        m = Message(id=1234, text="a test message", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            message = Message.query.get(1234)

            resp = c.get(f'/messages/{message.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("a test message", str(resp.data))
            
    def test_message_destroy(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(id=1234, text="a test message",
                        user_id=self.testuser.id)
            db.session.add(m)
            db.session.commit()

            resp = c.post(f"/messages/{m.id}/delete")
            all_messages = Message.query.all()

            self.assertEqual(resp.status_code, 302)
            self.assertNotIn(m, all_messages)
    
    def test_messages_destroy_logged_out(self):
        u2 = User.signup(username="unauthorized", email="testfake@test.com", password="password", image_url=None)

        u2.id = 456789
        
        m = Message(id=1234, text="a test message",
                            user_id=self.testuser.id)

        db.session.add_all([u2, m])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 456789

            resp = c.post(f"/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(1234)
            self.assertIsNotNone(m)


    def test_messages_delete_no_authentication(self):
        m = Message(id=1234, text="a test message",
                    user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            resp = c.post("/messages/1234/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))


