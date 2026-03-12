from supabase import create_client, Client

from config.api_keys import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def p_get_teacher_classrooms(teacher_email: str) -> list[str]:
    try:
        # Get classrooms for the specified teacher from Supabase
        response = supabase.table('classroom_teachers') \
            .select('classroom_id') \
            .eq('teacher_email', teacher_email) \
            .execute()

        # return list[str] instead of list[dict]
        return [item.get("classroom_id") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching teacher classrooms: {str(e)}")


def p_get_student_classrooms(student_email: str) -> list[str]:
    try:
        # Get classrooms for the specified student from Supabase
        response = supabase.table('classroom_students') \
            .select('classroom_id') \
            .eq('student_email', student_email) \
            .execute()

        return [item.get("classroom_id") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching student classrooms: {str(e)}")


def p_get_student_assignments_by_classroom(student_email: str, classroom_id: str) -> list[str]:
    try:
        # Get assignments for the specified student and classroom from Supabase
        response = supabase.table('assignment_assigned_students') \
            .select('assignments_id') \
            .eq('student_email', student_email) \
            .eq('classroom_id', classroom_id) \
            .execute()

        return [item.get("assignment_id") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching student assignments: {str(e)}")


def p_get_classroom_students(classroom_id: str) -> list[str]:
    try:
        # Get students for the specified classroom from Supabase
        response = supabase.table('classroom_students') \
            .select('student_email') \
            .eq('classroom_id', classroom_id) \
            .execute()

        return [item.get("student_email") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching classroom students: {str(e)}")


def p_get_classroom_teachers(classroom_id: str) -> list[str]:
    try:
        # Get teachers for the specified classroom from Supabase
        response = supabase.table('classroom_teachers') \
            .select('teacher_email') \
            .eq('classroom_id', classroom_id) \
            .execute()

        return [item.get("teacher_email") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching classroom teachers: {str(e)}")


def p_get_assigned_students(assignment_id: str) -> list[str]:
    try:
        # Get assigned students for the specified assignment from Supabase
        response = supabase.table('assignment_assigned_students') \
            .select('student_email') \
            .eq('assignment_id', assignment_id) \
            .execute()

        return [item.get("student_email") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching assigned students: {str(e)}")


def p_get_student_completed_assignments(student_email: str) -> list[str]:
    try:
        # Get completed assignments for the specified student and classroom from Supabase
        response = supabase.table('assignments_completed_students') \
            .select('assignment_id') \
            .eq('student_email', student_email) \
            .execute()

        return [item.get("assignment_id") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching completed assignments: {str(e)}")


# classroom CRUD
def p_create_classroom(classroom_name: str, teacher_email: str):
    try:
        # Create a new classroom in Supabase
        supabase.table('classrooms') \
            .insert({'name': classroom_name, 'teacher_email': teacher_email}) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating classroom: {str(e)}")


def p_rename_classroom(classroom_id: str, new_name: str):
    try:
        # Rename the specified classroom in Supabase
        supabase.table('classrooms') \
            .update({'name': new_name}) \
            .eq('classroom_id', classroom_id) \
            .execute()

    except Exception as e:
        raise Exception(f"Error renaming classroom: {str(e)}")


def p_delete_classroom(classroom_id: str):
    try:
        # Delete the specified classroom from Supabase
        supabase.table('classrooms') \
            .delete() \
            .eq('classroom_id', classroom_id) \
            .execute()

    except Exception as e:
        raise Exception(f"Error deleting classroom: {str(e)}")


# student CRUD
def p_create_student(student_email: str, student_name: str):
    try:
        # Create a new student in Supabase
        supabase.table('students') \
            .insert({'email': student_email, 'name': student_name}) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_rename_student(student_email: str, new_name: str):
    try:
        # Rename the specified student in Supabase
        supabase.table('students') \
            .update({'name': new_name}) \
            .eq('email', student_email) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_delete_student(student_email: str):
    try:
        # Delete the specified student from Supabase
        supabase.table('students') \
            .delete() \
            .eq('email', student_email) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


# student - classroom mapping
def p_add_student_to_classroom(student_email: str, classroom_id: str):
    try:
        # Add the specified student to the specified classroom in Supabase
        supabase.table('classroom_students') \
            .insert({'student_email': student_email, 'classroom_id': classroom_id}) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_remove_student_from_classroom(student_email: str, classroom_id: str):
    try:
        # Remove the specified student from the specified classroom in Supabase
        supabase.table('classroom_students') \
            .delete() \
            .eq('student_email', student_email) \
            .eq('classroom_id', classroom_id) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


# assignment CRUD
def p_create_assignment(assignment_id: str, classroom_id: str, title: str, due_date: str, questions: dict[str, str]):
    try:
        # Create a new assignment in Supabase
        supabase.table('assignments') \
            .insert({
            'assignment_id': assignment_id,
            'classroom_id': classroom_id,
            'title': title,
            'due_date': due_date,
            'questions': questions
        }) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_rename_assignment(assignment_id: str, new_title: str):
    try:
        # Rename the specified assignment in Supabase
        supabase.table('assignments') \
            .update({'title': new_title}) \
            .eq('assignment_id', assignment_id) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_delete_assignment(assignment_id: str):
    try:
        # Delete the specified assignment from Supabase
        supabase.table('assignments') \
            .delete() \
            .eq('assignment_id', assignment_id) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


# assignment - student mapping
def p_assign_assignment_to_student(assignment_id: str, student_email: str):
    try:
        # Assign the specified assignment to the specified student in Supabase
        supabase.table('assignment_assigned_students') \
            .insert({'assignment_id': assignment_id, 'student_email': student_email}) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_remove_assignment_from_student(assignment_id: str, student_email: str):
    try:
        # Remove the specified assignment from the specified student in Supabase
        supabase.table('assignment_assigned_students') \
            .delete() \
            .eq('assignment_id', assignment_id) \
            .eq('student_email', student_email) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


# assignment submission and grading
def p_submit_assignment(student_email: str, assignment_id: str):
    try:
        # Mark the specified assignment as completed for the specified student in Supabase
        supabase.table('assignment_submissions') \
            .insert({'assignment_id': assignment_id, 'student_email': student_email, 'status': 'completed'}) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_mark_assignment_as_completed(student_email: str, assignment_id: str):
    try:
        # Mark the specified assignment as completed for the specified student in Supabase
        supabase.table('assignment_submissions') \
            .update({'status': 'completed'}) \
            .eq('assignment_id', assignment_id) \
            .eq('student_email', student_email) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_upload_assignment_files(student_email: str, assignment_id: str, files: list[bytes], score: int):
    try:
        # Upload the specified files for the specified assignment and student in Supabase
        supabase.table('assignment_submissions') \
            .update({'files': files, 'score': score}) \
            .eq('assignment_id', assignment_id) \
            .eq('student_email', student_email) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")
