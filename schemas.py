def student_serializer(student) -> dict:
    return {
        "id": str(student["_id"]),
        "name": str(student["name"]),
        "email": str(student["email"]),
        "attended": int(student["attended"]),
        "missed": int(student["missed"]),
        "present": student["present"]
        # "date": [str(date) for date in student["date"]],
    }

def students_serializer(students) -> list:
    return [student_serializer(student) for student in students]