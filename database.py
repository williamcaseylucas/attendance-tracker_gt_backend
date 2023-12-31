from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# import certifi
# ca = certifi.where()  # Generate certification

# url = 'mongodb://localhost:27017'
# url = 'mongodb://root:example@localhost:27017/?authMechanism=DEFAULT'
url = os.environ["MONGODB_URL"]
# export MONGODB_URL="mongodb+srv://wrunyon3:<password>@cluster0.xa1ygkr.mongodb.net/"
client = MongoClient(url)

database = client.AttendenceTracker
students_collection = database.students
teacher_collection = database.teacher
