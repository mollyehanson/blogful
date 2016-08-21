import os
import unittest
import urllib
from urlparse import urlparse
# from urllib.parse import urlparse

from werkzeug.security import generate_password_hash

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User, Post

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)


    def simulate_login(self):
        """Simulate user login in testing"""
        with self.client.session_transaction() as http_session:
            http_session["user_id"] = str(self.user.id)
            http_session["_fresh"] = True

    def test_add_post(self):
        """Test adding post"""
        self.simulate_login()

        response = self.client.post("/post/add", data={
            "title": "Test Post",
            "content": "Test content"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        posts = session.query(Post).all()
        self.assertEqual(len(posts), 1)

        post = posts[0]
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.content, "<p>Test content</p>\n")
        self.assertEqual(post.author, self.user)

    def test_edit_post(self):
        """Test editing post"""
        self.simulate_login()

        self.client.post("/post/add", data={
            "title": "Test Post",
            "content": "Test content"
        })

        response = self.client.post("/post/1/edit", data={
            "title": "Edit Post",
            "content": "Edit content"
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        posts = session.query(Post).all()
        self.assertEqual(len(posts), 1)

        post = posts[0]
        self.assertEqual(post.title, "Edit Post")
        self.assertEqual(post.content, "<p>Edit content</p>\n")
        self.assertEqual(post.author, self.user)

    def test_delete_post(self):
        """Test deleting post"""
        self.simulate_login()

        self.client.post("/post/add", data={
            "title": "Test Post",
            "content": "Test content"
        })

        response = self.client.post("/post/1/delete")
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        posts = session.query(Post).all()
        self.assertEqual(len(posts), 0)

if __name__ == "__main__":
    unittest.main()