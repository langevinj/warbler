"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from models import db, User, Message, Follows


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for Messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        m = Message(
            text="I'm tired today",
            timestamp="2007-05-08 12:35:29.123",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        #User should have 1 message
        self.assertEqual(len(u.messages), 1)

    def test_message_create_failure(self):
        """Test Message.create fail to creates a message when invliad credentials are given"""

        #before creating user?

        #incorrect user id

        #no give a mandatory creendtial

        #given a string that is too long

    def test_message_user_relationship(self):
        """Test that the relationship between Message and User is active"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        m = Message(
            text="I'm tired today",
            timestamp="2007-05-08 12:35:29.123",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.user, u)

    