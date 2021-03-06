import json
import unittest
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../services/cu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
  user_id = db.Column(db.String(120), primary_key=True)
  name = db.Column(db.String(120),nullable=False)
  last_active = db.Column(db.String,nullable=False)

def get_users():
  response_object = dict()
  users = Users.query.all()
  for user in users:
    response_object[user.user_id] = {
      'id': user.user_id,
      'name': user.name,
      'last_active': user.last_active
    }
  return response_object


def fillsqlitetable():
  users = Users.query.all()
  for user in users:
    db.session.delete(user)
  db.session.commit()
  jsondb = json.load(open('../database/users.json','r'))
  for key in jsondb.keys():
    user = Users(user_id=key,name=jsondb[key]['name'],last_active=jsondb[key]['last_active'])
    db.session.add(user)
  db.session.commit()


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.url = "http://127.0.0.1:5000/users"

    def test_user_records(self):
        fillsqlitetable()
        for username, expected in GOOD_RESPONSES.iteritems():
            actual_reply = requests.get("{}/{}".format(self.url, username))
            actual_reply = actual_reply.json()

            self.assertEqual(actual_reply, expected,
                             "Got {} user record but expected {}".format(
                                 actual_reply, expected
                             ))

    def test_user_not_found(self):
        """ Test /users/<username> for non-existent user"""
        fillsqlitetable()
        invalid_user = "jim_the_duck_guy"
        actual_reply = requests.get("{}/{}".format(self.url, invalid_user))
        self.assertEqual(actual_reply.status_code, 404,
                         "Got {} but expected 404".format(
                             actual_reply.status_code))

    def test_add_user(self):
        fillsqlitetable()
        user_data = {
            "id": "tom_cruzer",
            "name": "Tom Cruzer"
        }
        actual_reply = requests.post("{}/add".format(self.url),data = user_data)
        actual_reply = actual_reply.json()
        self.assertEqual(actual_reply['id'],user_data['id'])
        self.assertEqual(actual_reply['name'],user_data['name'])

    def test_view_user_booking(self):
      fillsqlitetable()
      user_id = "chris_rivers"
      item = {
                "20151201": [
                  {
                    "rating": 8.8,
                    "title": "Creed",
                    "uri": "/movies/267eedb8-0f5d-42d5-8f43-72426b9fb3e6"
                  }
                ]
             }
      actual_reply = requests.get("{}/{}/bookings".format(self.url,user_id))
      actual_reply = actual_reply.json()

      self.assertTrue(item["20151201"] <= actual_reply["20151201"])

    def test_user_suggested(self):
      fillsqlitetable()
      user_id = 'chris_rivers'
      item = {
              "movies": [
                {
                  "director": "Ryan Coogler",
                  "id": "267eedb8-0f5d-42d5-8f43-72426b9fb3e6",
                  "rating": 8.8,
                  "title": "Creed"
                },
                {
                  "director": "Ridley Scott",
                  "id": "a8034f44-aee4-44cf-b32c-74cf452aaaae",
                  "rating": 8.2,
                  "title": "The Martian"
                },
                {
                  "director": "Peter Sohn",
                  "id": "720d006c-3a57-4b6a-b18f-9b713b073f3c",
                  "rating": 7.4,
                  "title": "The Good Dinosaur"
                }
              ]
            }
      actual_reply = requests.get("{}/{}/suggested".format(self.url,user_id))
      actual_reply = actual_reply.json()
      self.assertTrue(item!=actual_reply)

    def test_book_movie(self):
      fillsqlitetable()
      payload = {
          'movie_id': "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab",
          'showtime_id': "20151205",
          'user_id': "chris_rivers"
        }
      actual_reply = requests.post("{}/order".format(self.url),data=payload)
      actual_reply = actual_reply.json()
      self.assertTrue(payload['movie_id'] in actual_reply[payload['user_id']][payload['showtime_id']])


GOOD_RESPONSES = {
  "chris_rivers" : {
    "id": "chris_rivers",
    "name": "Chris Rivers",
    "last_active":1360031010
  },
  "peter_curley" : {
    "id": "peter_curley",
    "name": "Peter Curley",
    "last_active": 1360031222
  },
  "garret_heaton" : {
    "id": "garret_heaton",
    "name": "Garret Heaton",
    "last_active": 1360031425
  },
  "michael_scott" : {
    "id": "michael_scott",
    "name": "Michael Scott",
    "last_active": 1360031625
  },
  "jim_halpert" : {
    "id": "jim_halpert",
    "name": "Jim Halpert",
    "last_active": 1360031325
  },
  "pam_beesly" : {
    "id": "pam_beesly",
    "name": "Pam Beesly",
    "last_active": 1360031225
  },
  "dwight_schrute" : {
    "id": "dwight_schrute",
    "name": "Dwight Schrute",
    "last_active": 1360031202
  }
}
# GOOD_RESPONSES = json.loads(json.dumps(GOOD_RESPONSES))

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))