from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
from model import Student

from fastapi import APIRouter
from database import collection
from schemas import students_serializer, student_serializer
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
    students = students_serializer(collection.find())
    return students

@app.get("/{id}")
async def get_student(id: str):
    return students_serializer(collection.find_one({"_id": ObjectId(id)}))


# post
@app.post("/")
async def create_todo(student: Student):
    _id = collection.insert_one(dict(student))
    return students_serializer(collection.find({"_id": _id.inserted_id}))[0]


# update
@app.put("/{id}")
async def update_student(id: str, student: Student):
    collection.find_one_and_update({"_id": ObjectId(id)}, {
        "$set": dict(student)
    })
    return students_serializer(collection.find({"_id": ObjectId(id)}))

# delete
@app.delete("/{id}")
async def delete_student(id: str):
    collection.find_one_and_delete({"_id": ObjectId(id)})
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