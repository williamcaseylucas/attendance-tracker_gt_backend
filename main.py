from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
import json

from pymongo import ReturnDocument
from model import Student, Attendence_Log, Teacher

from fastapi import APIRouter
from database import students_collection, teacher_collection
from schemas import students_serializer, student_serializer, teacher_serializer
from bson import ObjectId

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*']
)

class ConnectionManager:
  def __init__(self) -> None:
    self.active_connections: List[WebSocket] = []
  async def connect(self, websocket:WebSocket):
    await websocket.accept()
    self.active_connections.append(websocket)

  def disconnect(self, websocket:WebSocket):
    self.active_connections.remove(websocket)

  async def send_personal_message(self, message:str, websocket: WebSocket):
    await websocket.send_text(message)

  async def broadcast(self, message:str):
    for connection in self.active_connections:
      await connection.send_text(message)
    
manager = ConnectionManager()

# retrieve
@app.get("/")
async def get_students():
    students = students_serializer(students_collection.find())
    return students

@app.get('/register')
async def get_coords_id():
  cursor = teacher_collection.find({})[0]
  if cursor:
    return teacher_serializer(cursor)
  else:
    return HTTPException(400, 'Something weird happened...')

@app.get("/{id}")
async def get_student(id: str):
    return students_serializer(students_collection.find_one({"_id": ObjectId(id)}))

# post
@app.post("/")
async def create_todo(student: Student):
    _id = students_collection.insert_one(dict(student))
    return students_serializer(students_collection.find({"_id": _id.inserted_id}))[0]
  
  
@app.put('/register')
async def define_coords_id(data: Teacher):
  teacher_collection.update_one(filter={},update={"$set": dict(data)}, upsert=True)
  cursor = teacher_collection.find({})[0]
    
  return teacher_serializer(cursor)


"""
{
  email: str
  session_id: num,
  date: str,
  distance: num
}
"""
@app.put('/attendance')
async def log_attendance_of_student(data: Attendence_Log):
  email, date = dict(data).values() 
  # Date needs to not be within an hour of the current time
  date_db = students_serializer(list(students_collection.find(
    {'email': email},
  )))[0]
  
  if date_db:
    current_date = datetime.fromisoformat(date)
    db_date = datetime.fromisoformat(date_db['date'])
    db_date_one_hour_future = db_date + timedelta(hours=1)
    
    # Then more than one request is being made in the same hour
    if db_date <= current_date <= db_date_one_hour_future:
      return HTTPException(400, 'Cannot add to DB more than once in a session')
  else:
    return HTTPException(404, 'User does not exist with that email')
  
  # If all of these things are fine, then we can do this:
  # Email will be used to update the user in the db
  updated_student = students_collection.find_one_and_update(
    {'email': email},
    {'$inc': {'attended': 1}, '$set': {'date': date}},
    return_document=ReturnDocument.AFTER
  )
  
  if updated_student:
    return students_serializer([updated_student])[0]
  else:
    return HTTPException(404, 'no such user')


# update
@app.put("/{id}")
async def update_student(id: str, student: Student):
    updated_student = students_collection.find_one_and_update({"_id": ObjectId(id)}, {
        "$set": dict(student)
    })
    
    if updated_student:
      return students_serializer([updated_student])[0]
    else:
      return HTTPException(404, 'user does not exist')
    # return students_serializer(students_collection.find({"_id": ObjectId(id)}))[0]

# delete
@app.delete("/{id}")
async def delete_student(id: str):
    students_collection.find_one_and_delete({"_id": ObjectId(id)})
    return {"status": "ok"}

@app.websocket('/ws/{client_id}')
async def websocket_endpoint(websocket: WebSocket, client_id: int):
  await manager.connect(websocket)
  now = datetime.now()
  currency_time = now.strftime('%H:%M')

  try:
    while True:
      data = await websocket.receive_text()
      message = {'time': currency_time, 'client_id': client_id, 'message': data}
      await manager.broadcast(json.dumps(message))
  except WebSocketDisconnect:
    manager.disconnect(websocket)
    message = {'time': currency_time, 'client_id': client_id, 'message': 'Offline'}
    await manager.broadcast(json.dumps(message))