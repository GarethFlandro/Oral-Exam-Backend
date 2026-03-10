from supabase import create_client, Client

from config.api_keys import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_teacher_classrooms(teacher_id: str) -> list[dict]:
    try:
        # Get classrooms for the specified teacher from Supabase
        response = supabase.table('classroom_teachers') \
            .select('*') \
            .eq('teacher_id', teacher_id) \
            .execute()

        return response.data

    except Exception as e:
        raise Exception(f"Error fetching teacher classrooms: {str(e)}")

def get_student_classrooms(student_id: str) -> list[dict]:
    try:
        # Get classrooms for the specified student from Supabase
        response = supabase.table('classroom_students') \
            .select('*') \
            .eq('student_id', student_id) \
            .execute()

        return response.data

    except Exception as e:
        raise Exception(f"Error fetching student classrooms: {str(e)}")

def get_student_assignments_by_classroom(student_id: str, classroom_id: str) -> list[dict]:
    try:
        # Get assignments for the specified student and classroom from Supabase
        response = supabase.table('assignment_assigned_students') \
            .select('*') \
            .eq('student_id', student_id) \
            .eq('classroom_id', classroom_id) \
            .execute()

        return response.data

    except Exception as e:
        raise Exception(f"Error fetching student assignments: {str(e)}")

def get_classroom_students(classroom_id: str) -> list[dict]:
    try:
        # Get students for the specified classroom from Supabase
        response = supabase.table('classroom_students') \
            .select('*') \
            .eq('classroom_id', classroom_id) \
            .execute()

        return response.data

    except Exception as e:
        raise Exception(f"Error fetching classroom students: {str(e)}")

def get_classroom_teachers(classroom_id: str) -> list[dict]:
    try:
        # Get teachers for the specified classroom from Supabase
        response = supabase.table('classroom_teachers') \
            .select('*') \
            .eq('classroom_id', classroom_id) \
            .execute()

        return response.data

    except Exception as e:
        raise Exception(f"Error fetching classroom teachers: {str(e)}")

def get_assigned_students(assignment_id: str) -> list[dict]:
    try:
        # Get assigned students for the specified assignment from Supabase
        response = supabase.table('assignment_assigned_students') \
            .select('*') \
            .eq('assignment_id', assignment_id) \
            .execute()

        return response.data

    except Exception as e:
        raise Exception(f"Error fetching assigned students: {str(e)}")

def get_student_completed_assignments_by_classroom(student_id: str, classroom_id: str) -> list[dict]:
    try:
        # Get completed assignments for the specified student and classroom from Supabase
        response = supabase.table('assignments') \
            .select('*') \
            .eq('student_id', student_id) \
            .eq('classroom_id', classroom_id) \
            .eq('status', 'true') \
            .execute()

        return response.data

    except Exception as e:
        raise Exception(f"Error fetching completed assignments: {str(e)}")