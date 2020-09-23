"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


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

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

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

            
    def test_add_message_form(self):
        """Can you access the add a message form?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
            resp = c.get("/messages/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-outline-success btn-block">Add my message!</button>', html)


    def test_messages_show(self):
        """Test showing a message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        m = Message(
            text="Im tired today",
            timestamp="2007-05-08 12:35:29.123",
            user_id=self.testuser.id 
        )
        db.session.add(m)
        db.session.commit()

        resp = c.get(f"/messages/{m.id}")
        html = resp.get_data(as_text=True)

        #Make sure the correct message is displayed
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Im tired today", html)
    
    def test_messages_destroy(self):
        """Test deleting a message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        m = Message(
            text="Im tired today",
            timestamp="2007-05-08 12:35:29.123",
            user_id=self.testuser.id
        )
        #add message to session
        db.session.add(m)
        db.session.commit()

        #attempt to delete
        resp = c.post(f"/messages/{m.id}/delete")
        html = resp.get_data(as_text=True)

        #grab all current messages
        messages = Message.query.all()

        #test redirection
        self.assertEqual(resp.status_code, 302)
        #test the message is deleted
        self.assertNotIn(m, messages)
