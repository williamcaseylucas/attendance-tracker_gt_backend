from pydantic import BaseModel, Field
from datetime import date as date_type
from typing import List

class Student(BaseModel):
  name: str
  email: str
  attended: int
  missed: int
  # present: bool
  date: str | None # optional
  
class Attendence_Log(BaseModel):
  email: str
  date: str
  
class Teacher(BaseModel):
  id: int
  coords: List[float] | None