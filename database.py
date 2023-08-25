from model import Student
from pymongo import MongoClient

# url = 'mongodb://localhost:27017'
url = 'mongodb://root:example@localhost:27017/?authMechanism=DEFAULT'
client = MongoClient(url)

database = client.AttendenceTracker
students_collection = database.students
teacher_collection = database.teacher