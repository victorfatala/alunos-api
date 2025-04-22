from db import get_db_connection, SQLQueries


def find_students_by_course_id(course_id):
    """Função auxiliar para encontrar alunos por ID do curso"""
    connection = get_db_connection()
    students = connection.execute(
        SQLQueries("queries/students.sql").GET_STUDENT_BY_COURSE_ID, (course_id,)
    ).fetchall()
    connection.close()
    return students
