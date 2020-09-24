"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError

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

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_user___repr__(self):
        """Does __repr__ method work?"""
        
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        #unsure if this is breaking the rules 
        self.assertEqual(f"{u}", f"<User #{u.id}: {u.username}, {u.email}>")


    def test_is_following(self):
        """Tests detection of user1 following user2"""

        u1 = User(
             email="test1@test.com",
             username="testuser1",
             password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()


        u2= User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u2)
        db.session.commit()

        #test that u1 is not following u2
        self.assertFalse(u1.is_following(u2))
        
        new_follow = Follows(user_being_followed_id=u2.id, user_following_id=u1.id)
        db.session.add(new_follow)
        db.session.commit() 

        #test detecting of u1 following u2
        self.assertTrue(u1.is_following(u2))

    def test_is_followed_by(self):
        """Tests detection of user 2 being followed by user1"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )


        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        #test that u1 is not following u2
        self.assertFalse(u2.is_followed_by(u1))

        new_follow = Follows(user_being_followed_id=u2.id,
                             user_following_id=u1.id)
        db.session.add(new_follow)
        db.session.commit()

        #test detecting of u2 being followed by u1
        self.assertTrue(u2.is_followed_by(u1))

    def test_user_create(self):
        """Test that User.create successfully creates a new user"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        #make sure that there is an instance of the new User
        test = User.query.filter(User.username == "testuser").first()

        self.assertEqual(u, test)

    # def test_user_create_fail(self):
    #     """Tests that a user is not created when given invalid credentials"""
        
    #     u = User.signup(
    #         email="test@test.com",
    #         password="HASHED_PASSWORD"
    #     )

    #     with self.assertRaises(IntegrityError):
    #         db.session.commit()
    

    def test_user_authenticate(self):
        """Test that a user is returned with a valid username and password"""

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="123456",
            image_url="www.wiki.com"
        )
        db.session.add(u)
        db.session.commit()

        #grab return of authentication attempt
        test = User.authenticate(f"{u.username}", "123456")

        self.assertEqual(test, u)

    def test_user_authenticate_fail(self):
        """Test that authentication failes when an invalid username or password is used"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="123456",
            image_url="www.wiki.com"
        )
        db.session.add(u)
        db.session.commit()

        #should return false with an incorrect username
        self.assertFalse(User.authenticate("jimbob", "123456"))

        #should return false with an incorrect password
        self.assertFalse(User.authenticate("testuser", "78910"))


        
    
        

