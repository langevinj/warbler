"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc 

from models import db, User, Message, Follows


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test model for Users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "fake@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1 

        u2 = User.signup("test2", "fake2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2 

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1 
        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
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

    ################################################
    
    def test_user__repr__(self):
        """Does __repr__ method work?"""
        self.assertEqual(f"{self.u1}", f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")

#########Following Tests###############

    def test_is_following(self):
        """Tests detection of user1 following user2"""
        self.u1.following.append(self.u2)
        db.session.commit()
        
        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u1.followers), 0)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_is_followed_by(self):
        """Tests detection of user 2 being followed by user1"""
        self.u1.following.append(self.u2)
        db.session.commit()

        #test detecting of u2 being followed by u1
        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    #########
    #Test sign-ups#
    #########

    def test_user_create(self):
        """Test that User.create successfully creates a new user"""

        u = User.signup("testuser", "test@test.com", "HASHED_PASSWORD", None)
        
        uid = 4444
        u.id=uid
        db.session.commit()

        test = User.query.filter(User.username == "testuser").first()
        self.assertEqual(u, test)

    def test_invalid_email_signup(self):
        invalid = User.signup("testhello", None, "password", None)
        uid = 123456
        invalid.id = uid 
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_username_signup(self):
        invalid = User.signup(None, "fakeemail@email.com", "password", None)
        uid = 123456
        invalid.id = uid 
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testuser", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testuser", "email@email.com", None, None)

    ######
    #Authentication Tests
    #####

    def test_user_authenticate(self):
        #grab return of authentication attempt
        u = User.authenticate(f"{self.u1.username}", "password")
        self.assertEqual(u, self.u1)
    
    def test_invalid_username(self):
        u = User.authenticate("jimbob", "password")
        self.assertFalse(u)

    def test_invalid_password(self):
        u = User.authenticate(f"{self.u1.username}", "123456")
        self.assertFalse(u)
        self.assertNotEqual(u, self.u1)


        
    
        

