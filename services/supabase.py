from supabase import create_client, Client

from config.api_keys import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def p_get_teacher_classrooms(teacher_email: str) -> list[str]:
    try:
        # Get classrooms for the specified teacher from Supabase
        response = supabase.table('classroom_teachers') \
            .select('classroom_name') \
            .eq('teacher_email', teacher_email) \
            .execute()

        if not response.data:
            return []

        # return list[str] instead of list[dict]
        return [item.get("classroom_name") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching teacher classrooms: {str(e)}")


def p_get_student_classrooms(student_email: str) -> list[str]:
    try:
        # Get classrooms for the specified student from Supabase
        response = supabase.table('classroom_students') \
            .select('classroom_name') \
            .eq('student_email', student_email) \
            .execute()

        if not response.data:
            return []

        return [item.get("classroom_name") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching student classrooms: {str(e)}")


def p_get_student_assignments_by_classroom(student_email: str, classroom_name: str) -> list[str]:
    try:
        # Get assignments for the specified student and classroom from Supabase
        response = supabase.table('assignment_assigned_students') \
            .select('assignments_id') \
            .eq('student_email', student_email) \
            .eq('classroom_name', classroom_name) \
            .execute()

        if not response.data:
            return []

        return [item.get("assignment_id") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching student assignments: {str(e)}")


def p_get_classroom_students(classroom_name: str) -> list[str]:
    try:
        # Get students for the specified classroom from Supabase
        response = supabase.table('classroom_students') \
            .select('student_email') \
            .eq('classroom_name', classroom_name) \
            .execute()

        if not response.data:
            return []

        return [item.get("student_email") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching classroom students: {str(e)}")


def p_get_classroom_teachers(classroom_name: str) -> list[str]:
    try:
        # Get teachers for the specified classroom from Supabase
        response = supabase.table('classroom_teachers') \
            .select('teacher_email') \
            .eq('classroom_name', classroom_name) \
            .execute()

        if not response.data:
            return []

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

        if not response.data:
            return []

        return [item.get("student_email") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching assigned students: {str(e)}")


def p_get_student_completed_assignments_by_classroom(student_email: str, classroom_name:str) -> list[str]:
    try:
        # Get completed assignments for the specified student and classroom from Supabase
        response = supabase.table('assignments_completed_students') \
            .select('assignment_id') \
            .eq('student_email', student_email) \
            .eq('classroom_name', classroom_name) \
            .execute()

        if not response.data:
            return []

        return [item.get("assignment_id") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching completed assignments: {str(e)}")


def p_get_assignments_by_classroom(classroom_name: str) -> list[str]:
    try:
        # Get assignments for the specified classroom from Supabase
        response = supabase.table('assignments') \
            .select('assignment_id') \
            .eq('classroom_name', classroom_name) \
            .execute()

        if not response.data:
            return []

        return [item.get("assignment_id") for item in response.data]

    except Exception as e:
        raise Exception(f"Error fetching classroom assignments: {str(e)}")

# classroom CRUD
def p_create_classroom(classroom_name: str, teacher_email: str):
    try:
        classrooms = supabase.table('classrooms') \
            .select('classroom_name') \
            .eq('classroom_name', classroom_name) \
            .execute()

        if classrooms.data:
            raise Exception(f"Classroom with name '{classroom_name}' already exists.")

        # Create a new classroom in Supabase
        supabase.table('classrooms') \
            .insert({'name': classroom_name}) \
            .execute()

        supabase.table('classroom_teachers') \
            .insert({'classroom_name': classroom_name, 'teacher_email': teacher_email}) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating classroom: {str(e)}")


def p_rename_classroom(classroom_name: str, new_name: str):
    try:
        classrooms = supabase.table('classrooms') \
            .select('classroom_name') \
            .eq('classroom_name', classroom_name) \
            .execute()

        if not classrooms.data:
            raise Exception(f"Classroom with name '{classroom_name}' does not exist.")

        classrooms = supabase.table('classrooms') \
            .select('classroom_name') \
            .eq('classroom_name', new_name) \
            .execute()

        if classrooms.data:
            raise Exception(f"Classroom with name '{new_name}' already exists.")

        # Rename the specified classroom in Supabase
        supabase.table('classrooms') \
            .update({'classroom_name': new_name}) \
            .eq('classroom_name', classroom_name) \
            .execute()

    except Exception as e:
        raise Exception(f"Error renaming classroom: {str(e)}")


def p_delete_classroom(classroom_name: str):
    try:
        classrooms = supabase.table('classrooms') \
            .select('classroom_name') \
            .eq('classroom_name', classroom_name) \
            .execute()

        if not classrooms.data:
            raise Exception(f"Classroom with name '{classroom_name}' does not exist.")

        # Delete the specified classroom from Supabase
        supabase.table('classrooms') \
            .delete() \
            .eq('classroom_name', classroom_name) \
            .execute()

    except Exception as e:
        raise Exception(f"Error deleting classroom: {str(e)}")


# student CRUD
def p_create_student(student_email: str, student_name: str):
    try:
        students = supabase.table('students') \
            .select('student_email') \
            .eq('student_email', student_email) \
            .execute()

        if students.data:
            raise Exception(f"Student with email '{student_email}' already exists.")

        # Create a new student in Supabase
        supabase.table('students') \
            .insert({'student_email': student_email, 'student_name': student_name}) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_rename_student(student_email: str, new_name: str):
    try:
        students = supabase.table('students') \
            .select('student_email') \
            .eq('student_email', student_email) \
            .execute()

        if students.data:
            raise Exception(f"Student with email '{student_email}' already exists.")

        students = supabase.table('students') \
            .select('student_name') \
            .eq('student_name', new_name) \
            .execute()

        if students.data:
            raise Exception(f"Student with new name '{new_name}' already exists.")

        # Rename the specified student in Supabase
        supabase.table('students') \
            .update({'name': new_name}) \
            .eq('email', student_email) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_delete_student(student_email: str):
    try:
        students = supabase.table('students') \
            .select('student_email') \
            .eq('student_email', student_email) \
            .execute()

        if students.data:
            raise Exception(f"Student with email '{student_email}' does not exist.")

        # Delete the specified student from Supabase
        supabase.table('students') \
            .delete() \
            .eq('email', student_email) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


# student - classroom mapping
def p_add_student_to_classroom(student_email: str, classroom_name: str):
    try:
        students = supabase.table('students') \
            .select('student_email') \
            .eq('student_email', student_email) \
            .execute()

        if not students.data:
            raise Exception(f"Student with email '{student_email}' does not exist.")

        classrooms = supabase.table('classrooms') \
            .select('classroom_name') \
            .eq('classroom_name', classroom_name) \
            .execute()

        if not classrooms.data:
            raise Exception(f"Classroom with name '{classroom_name}' does not exist.")

        # Add the specified student to the specified classroom in Supabase
        supabase.table('classroom_students') \
            .insert({'student_email': student_email, 'classroom_name': classroom_name}) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_remove_student_from_classroom(student_email: str, classroom_name: str):
    try:
        students = supabase.table('students') \
            .select('student_email') \
            .eq('student_email', student_email) \
            .execute()

        if not students.data:
            raise Exception(f"Student with email '{student_email}' does not exist.")

        classrooms = supabase.table('classrooms') \
            .select('classroom_name') \
            .eq('classroom_name', classroom_name) \
            .execute()

        if not classrooms.data:
            raise Exception(f"Classroom with name '{classroom_name}' does not exist.")

        # Remove the specified student from the specified classroom in Supabase
        supabase.table('classroom_students') \
            .delete() \
            .eq('student_email', student_email) \
            .eq('classroom_name', classroom_name) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


# assignment CRUD
def p_create_assignment(assignment_id: str, classroom_name: str, title: str, due_date: str):
    try:
        classrooms = supabase.table('classrooms') \
            .select('classroom_name') \
            .eq('classroom_name', classroom_name) \
            .execute()

        if not classrooms.data:
            raise Exception(f"Classroom with name '{classroom_name}' does not exist.")

        assignments = supabase.table('assignments') \
            .select('assignment_id') \
            .eq('assignment_id', assignment_id) \
            .eq('classroom_name', classroom_name) \
            .execute()

        if assignments.data:
            raise Exception(f"Assignment with id '{assignment_id}' already exists in classroom '{classroom_name}'.")

        # Create a new assignment in Supabase
        supabase.table('assignments') \
            .insert({
            'assignment_id': assignment_id,
            'classroom_name': classroom_name,
            'title': title,
            'due_date': due_date
        }) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_rename_assignment(assignment_id: str, new_title: str):
    try:
        assignments = supabase.table('assignments') \
            .select('assignment_id') \
            .eq('assignment_id', assignment_id) \
            .execute()

        if not assignments.data:
            raise Exception(f"Assignment with id '{assignment_id}' does not exist.")

        # Rename the specified assignment in Supabase
        supabase.table('assignments') \
            .update({'title': new_title}) \
            .eq('assignment_id', assignment_id) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_delete_assignment(assignment_id: str):
    try:
        assignments = supabase.table('assignments') \
            .select('assignment_id') \
            .eq('assignment_id', assignment_id) \
            .execute()

        if not assignments.data:
            raise Exception(f"Assignment with id '{assignment_id}' does not exist.")

        # Delete the specified assignment from Supabase
        supabase.table('assignments') \
            .delete() \
            .eq('assignment_id', assignment_id) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


# assignment - student mapping
def p_assign_assignment_to_student(classroom_name: str, assignment_id: str, student_email: str):
    try:
        assignments = supabase.table('assignments') \
            .select('assignment_id') \
            .eq('assignment_id', assignment_id) \
            .execute()

        if not assignments.data:
            raise Exception(f"Assignment with id '{assignment_id}' does not exist.")

        students = supabase.table('students') \
            .select('student_email') \
            .eq('student_email', student_email) \
            .execute()

        if not students.data:
            raise Exception(f"Student with email '{student_email}' does not exist.")

        # Assign the specified assignment to the specified student in Supabase
        supabase.table('assignment_assigned_students') \
            .insert({'classroom_name': classroom_name, 'assignment_id': assignment_id, 'student_email': student_email}) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_remove_assignment_from_student(assignment_id: str, student_email: str):
    try:
        assignments = supabase.table('assignments') \
            .select('assignment_id') \
            .eq('assignment_id', assignment_id) \
            .execute()

        if not assignments.data:
            raise Exception(f"Assignment with id '{assignment_id}' does not exist.")

        students = supabase.table('students') \
            .select('student_email') \
            .eq('student_email', student_email) \
            .execute()

        if not students.data:
            raise Exception(f"Student with email '{student_email}' does not exist.")

        # Remove the specified assignment from the specified student in Supabase
        supabase.table('assignment_assigned_students') \
            .delete() \
            .eq('assignment_id', assignment_id) \
            .eq('student_email', student_email) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")

# assignment submission
def p_mark_assignment_as_completed(student_email: str, assignment_id: str):
    try:
        assignments = supabase.table('assignments') \
            .select('assignment_id') \
            .eq('assignment_id', assignment_id) \
            .execute()

        if not assignments.data:
            raise Exception(f"Assignment with id '{assignment_id}' does not exist.")

        students = supabase.table('students') \
            .select('student_email') \
            .eq('student_email', student_email) \
            .execute()

        if not students.data:
            raise Exception(f"Student with email '{student_email}' does not exist.")

        # Mark the specified assignment as completed for the specified student in Supabase
        supabase.table('assignment_submissions') \
            .update({'status': 'completed'}) \
            .eq('assignment_id', assignment_id) \
            .eq('student_email', student_email) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")


def p_upload_assignment_submission(student_email: str, assignment_id: str, files: list[bytes], score: int):
    try:
        students = supabase.table('students') \
            .select('student_email') \
            .eq('student_email', student_email) \
            .execute()

        if not students.data:
            raise Exception(f"Student with email '{student_email}' does not exist.")

        assignments = supabase.table('assignments') \
            .select('assignment_id') \
            .eq('assignment_id', assignment_id) \
            .execute()

        if not assignments.data:
            raise Exception(f"Assignment with id '{assignment_id}' does not exist.")

        # Upload the specified files for the specified assignment and student in Supabase
        supabase.table('assignment_submissions') \
            .update({'files': files, 'score': score}) \
            .eq('assignment_id', assignment_id) \
            .eq('student_email', student_email) \
            .execute()

    except Exception as e:
        raise Exception(f"Error creating student: {str(e)}")
