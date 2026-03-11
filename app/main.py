import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader

from api.routes import router, get_api_key
from services.supabase import p_get_teacher_classrooms, p_get_student_classrooms, \
    p_get_student_assignments_by_classroom, p_get_classroom_students, p_get_classroom_teachers, p_get_assigned_students, \
    p_get_student_completed_assignments_by_classroom

app = FastAPI(title="Oral Exam Backend")

api_key_header = APIKeyHeader(name="API_KEY", auto_error=True)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)


@app.get("/api/supabase", dependencies=[Depends(api_key_header)])
async def get_teacher_classrooms(teacher_email: str):
    p_get_teacher_classrooms(teacher_email)


@app.get("/api/supabase", dependencies=[Depends(get_api_key)])
async def get_student_classrooms(student_email: str):
    p_get_student_classrooms(student_email)


@app.get("/api/supabase", dependencies=[Depends(get_api_key)])
async def get_student_assignments_by_classroom(student_email: str, classroom_id: str):
    p_get_student_assignments_by_classroom(student_email, classroom_id)


@app.get("/api/supabase", dependencies=[Depends(get_api_key)])
async def get_classroom_students(classroom_id: str):
    p_get_classroom_students(classroom_id)


@app.get("/api/supabase", dependencies=[Depends(get_api_key)])
async def get_classroom_teachers(classroom_id: str):
    p_get_classroom_teachers(classroom_id)


@app.get("/api/supabase", dependencies=[Depends(get_api_key)])
async def get_assigned_students(assignment_id: str):
    p_get_assigned_students(assignment_id)


@app.get("/api/supabase", dependencies=[Depends(get_api_key)])
async def get_student_completed_assignments_by_classroom(student_email: str, assignment_id: str):
    p_get_student_completed_assignments_by_classroom(student_email, assignment_id)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def create_classroom(classroom_name: str, teacher_email: str):
    p_create_classroom(classroom_name, teacher_email)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def create_student(student_email: str, student_name: str):
    p_create_student(student_email, student_name)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def create_assignment(assignment_id: str, classroom_id: str, title: str, due_date: str, questions: dict[str, str]):
    p_create_assignment(assignment_id, classroom_id, title, due_date, questions)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def add_student_to_classroom(student_email: str, classroom_id: str):
    p_add_student_to_classroom(student_email, classroom_id)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def assign_assignment_to_student(assignment_id: str, student_email: str):
    p_assign_assignment_to_student(assignment_id, student_email)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def submit_assignment(student_email: str, assignment_id: str):
    p_submit_assignment(student_email, assignment_id)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def rename_classroom(classroom_id: str, new_name: str):
    p_rename_classroom(classroom_id, new_name)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def rename_assignment(assignment_id: str, new_title: str):
    p_rename_assignment(assignment_id, new_title)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def rename_student(student_email: str, new_name: str):
    p_rename_student(student_email, new_name)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def delete_classroom(classroom_id: str):
    p_delete_classroom(classroom_id)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def delete_assignment(assignment_id: str):
    p_delete_assignment(assignment_id)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def delete_student(student_email: str):
    p_delete_student(student_email)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def remove_student_from_classroom(student_email: str, classroom_id: str):
    p_remove_student_from_classroom(student_email, classroom_id)

@app.post("/api/supabase", dependencies=[Depends(get_api_key)])
async def remove_
