import uuid

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from api.routes import router, get_api_key
from services.supabase import (
    # classroom CRUD
    p_create_classroom, p_rename_classroom, p_delete_classroom,
    p_get_classroom_students, p_get_classroom_teachers,
    # student CRUD
    p_create_student, p_rename_student, p_delete_student,
    p_get_student_classrooms,
    # student - classroom membership
    p_add_student_to_classroom, p_remove_student_from_classroom,
    # teacher queries
    p_get_teacher_classrooms,
    # assignment CRUD
    p_create_assignment, p_rename_assignment, p_delete_assignment,
    # assignment - student mapping
    p_assign_assignment_to_student, p_remove_assignment_from_student,
    p_get_assigned_students, p_get_student_assignments_by_classroom,
    # assignment submission n' completion
    p_mark_assignment_as_completed,
    p_upload_assignment_submission, p_get_student_completed_assignments_by_classroom,
)

app = FastAPI(title="Oral Exam Backend")

api_key_header = APIKeyHeader(name="API_KEY", auto_error=True)

app.include_router(router)

origins = [
    "http://localhost:63340"
    "http://localhost:63341"
    "http://localhost:63342"
    "http://localhost:63343"
    "http://localhost:63344",
    "http://localhost:63345"
    "http://localhost:63346"
    "http://localhost:63347"
    "http://localhost:63348"
    "http://localhost:63349"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# classroom CRUD
class CreateClassroomModel(BaseModel):
    classroom_name: str
    teacher_email: str


@app.post("/supabase/create_classroom", dependencies=[Depends(get_api_key)])
async def create_classroom(model: CreateClassroomModel):
    p_create_classroom(model.classroom_name, model.teacher_email)


class RenameClassroomModel(BaseModel):
    classroom_name: str
    new_name: str


@app.post("/supabase/rename_classroom", dependencies=[Depends(get_api_key)])
async def rename_classroom(model: RenameClassroomModel):
    p_rename_classroom(model.classroom_name, model.new_name)


class DeleteClassroomModel(BaseModel):
    classroom_name: str


@app.post("/supabase/delete_classroom", dependencies=[Depends(get_api_key)])
async def delete_classroom(model: DeleteClassroomModel):
    p_delete_classroom(model.classroom_name)


@app.get("/supabase/get_classroom_students", dependencies=[Depends(get_api_key)])
async def get_classroom_students(classroom_name: str):
    p_get_classroom_students(classroom_name)


@app.get("/supabase/get_classroom_teachers", dependencies=[Depends(get_api_key)])
async def get_classroom_teachers(classroom_name: str):
    p_get_classroom_teachers(classroom_name)


# student CRUD
class CreateStudentModel(BaseModel):
    student_email: str
    student_name: str


@app.post("/supabase/create_student", dependencies=[Depends(get_api_key)])
async def create_student(model: CreateStudentModel):
    p_create_student(model.student_email, model.student_name)


class RenameStudentModel(BaseModel):
    student_email: str
    new_name: str


@app.post("/supabase/rename_student", dependencies=[Depends(get_api_key)])
async def rename_student(model: RenameStudentModel):
    p_rename_student(model.student_email, model.new_name)


class DeleteStudentModel(BaseModel):
    student_email: str


@app.post("/supabase/delete_student", dependencies=[Depends(get_api_key)])
async def delete_student(model: DeleteStudentModel):
    p_delete_student(model.student_email)


@app.get("/supabase/get_student_classrooms", dependencies=[Depends(get_api_key)])
async def get_student_classrooms(student_email: str):
    p_get_student_classrooms(student_email)


# student - classroom mapping
class AddStudentToClassroomModel(BaseModel):
    student_email: str
    classroom_name: str


@app.post("/supabase/add_student_to_classroom", dependencies=[Depends(get_api_key)])
async def add_student_to_classroom(model: AddStudentToClassroomModel):
    p_add_student_to_classroom(model.student_email, model.classroom_name)


class RemoveStudentFromClassroomModel(BaseModel):
    student_email: str
    classroom_name: str


@app.post("/supabase/remove_student_from_classroom", dependencies=[Depends(get_api_key)])
async def remove_student_from_classroom(model: RemoveStudentFromClassroomModel):
    p_remove_student_from_classroom(model.student_email, model.classroom_name)


# teachers
@app.get("/supabase/get_teacher_classrooms", dependencies=[Depends(api_key_header)])
async def get_teacher_classrooms(teacher_email: str):
    p_get_teacher_classrooms(teacher_email)


# assignment CRUD
class CreateAssignmentModel(BaseModel):
    classroom_name: str
    title: str
    due_date: str
    questions: dict[str, str]
    assignment_id: str = ""


@app.post("/supabase/create_assignment", dependencies=[Depends(get_api_key)])
async def create_assignment(model: CreateAssignmentModel):
    if not model.assignment_id:
        model.assignment_id = str(uuid.uuid4())

    p_create_assignment(model.assignment_id, model.classroom_name, model.title, model.due_date, model.questions)


class RenameAssignmentModel(BaseModel):
    assignment_id: str
    new_title: str


@app.post("/supabase/rename_assignment", dependencies=[Depends(get_api_key)])
async def rename_assignment(model: RenameAssignmentModel):
    p_rename_assignment(model.assignment_id, model.new_title)


class DeleteAssignmentModel(BaseModel):
    assignment_id: str


@app.post("/supabase/delete_assignment", dependencies=[Depends(get_api_key)])
async def delete_assignment(model: DeleteAssignmentModel):
    p_delete_assignment(model.assignment_id)


# assignment - student mapping
class AssignAssignmentToStudentModel(BaseModel):
    classroom_name: str
    assignment_id: str
    student_email: str


@app.post("/supabase/assign_assignment_to_student", dependencies=[Depends(get_api_key)])
async def assign_assignment_to_student(model: AssignAssignmentToStudentModel):
    p_assign_assignment_to_student(model.classroom_name, model.assignment_id, model.student_email)


class RemoveAssignmentFromStudentModel(BaseModel):
    assignment_id: str
    student_email: str


@app.post("/supabase/remove_assignment_from_student", dependencies=[Depends(get_api_key)])
async def remove_assignment_from_student(model: RemoveAssignmentFromStudentModel):
    p_remove_assignment_from_student(model.assignment_id, model.student_email)


@app.get("/supabase/get_assigned_students", dependencies=[Depends(get_api_key)])
async def get_assigned_students(assignment_id: str):
    p_get_assigned_students(assignment_id)


@app.get("/supabase/get_student_assignments_by_classroom", dependencies=[Depends(get_api_key)])
async def get_student_assignments_by_classroom(student_email: str, classroom_name: str):
    p_get_student_assignments_by_classroom(student_email, classroom_name)


# assignment submission
class MarkAssignmentAsCompletedModel(BaseModel):
    student_email: str
    assignment_id: str


@app.post("/supabase/mark_assignment_as_completed", dependencies=[Depends(get_api_key)])
async def mark_assignment_as_completed(model: MarkAssignmentAsCompletedModel):
    p_mark_assignment_as_completed(model.student_email, model.assignment_id)


class UploadAssignmentFilesModel(BaseModel):
    student_email: str
    assignment_id: str
    files: list[bytes]
    score: int


@app.post("/supabase/upload_assignment_files", dependencies=[Depends(get_api_key)])
async def upload_assignment_files(model: UploadAssignmentFilesModel):
    p_upload_assignment_submission(model.student_email, model.assignment_id, model.files, model.score)


@app.get("/supabase/get_student_completed_assignments_by_classroom", dependencies=[Depends(get_api_key)])
async def get_student_completed_assignments_by_classroom(student_email: str, assignment_id: str):
    p_get_student_completed_assignments_by_classroom(student_email, assignment_id)


# entry point

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
