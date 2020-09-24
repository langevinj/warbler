"""Message model tests."""
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes



# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

class MessageModelTestCase(TestCase):
    """Test model for Messages."""

    def setUp(self):
        """Create test client, add sample data."""  

        db.drop_all()
        db.create_all()

        self.uid = 12345
        u = User.signup("testtest", "email@email.com", "password", None)
        u.id = self.uid 
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    ########
    #Test message creation
    ###
     
    def test_user_model(self):
        """Does basic model work?"""

        m = Message(
            text="I'm tired today",
            timestamp="2007-05-08 12:35:29.123",
            user_id=self.u.id
        )
        db.session.add(m)
        db.session.commit()

        #User should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(m.user_id, self.u.id)


    def test_too_long_message(self):
        m = Message(
            text="asdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfaddfasddfasdadfasdfasdfasdfasdfasdfasfasdasdfasdasdasdasdfasdfasdfasdfasdfasdfasdfasdfdasdfasdfasdfasdasdfasdfasdasdfasdfasdasdfasdfasdfasdfasdfasdfasdfasdfasdasdfasdfsdfsdfsadfasdfasfasdfasfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfsadfasdfasfgasdfsdfsdfsdfsdf",
            timestamp="2007-05-08 12:35:29.123",
            user_id=self.u.id
        )
        
        db.session.add(m)
        with self.assertRaises(exc.DataError) as context:
            db.session.commit()
    
    def test_no_text(self):
        m = Message(text=None, timestamp="2007-05-08 12:35:29.123", user_id=self.u.id)
        db.session.add(m)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_timestamp(self):
        mid= 5555
        m = Message(
            text="Testing testing 123",
            timestamp=None,
            user_id=self.u.id
        )
        m.id = mid

        m2 = Message(
            text="testing testing 1234",
            timestamp="12 34 45",
            user_id=self.u.id 
        )      

        db.session.add(m)
        db.session.commit()
        find_m = Message.query.get(m.id)
        self.assertEqual(m, find_m)

        db.session.add(m2)
        with self.assertRaises(exc.DataError) as context:
            db.session.commit()
        
    def test_message_user_relationship(self):
        m = Message(
            text="Im tired today",
            timestamp="2007-05-08 12:35:29.123",
            user_id=self.u.id
        )

        mid = 123456
        m.id = mid 
        db.session.add(m)
        db.session.commit()

        message = Message.query.get(mid)

        self.assertEqual(message.user_id, self.u.id)
        self.assertEqual(message.user, self.u)
  
    
