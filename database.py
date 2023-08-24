from model import Student
from pymongo import MongoClient

# url = 'mongodb://localhost:27017'
url = 'mongodb://root:example@localhost:27017/?authMechanism=DEFAULT'
client = MongoClient(url)

database = client.AttendenceTracker
collection = database.students