from pydantic import BaseModel, Field
from datetime import date as date_type
from typing import List

class Student(BaseModel):
  name: str
  email: str
  attended: int
  missed: int
  present: bool