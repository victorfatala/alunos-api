from flask import request, Blueprint
import uuid
from datetime import datetime, timezone, timedelta
from db import COURSE_QUERIES, STUDENT_QUERIES, get_db_connection
from messages import GeneralErrorMessages, CourseSuccessMessages, CourseErrorMessages
from utils import find_students_by_course_id

course_routes = Blueprint("course_routes", __name__)


def validate_fields(data, allowed_fields):
    """Valida se existem campos inesperados no payload."""
    unexpected_fields = set(data.keys()) - allowed_fields
    if unexpected_fields:
        return {
            "error": GeneralErrorMessages.UNEXPECTED_FIELDS.value,
            "unexpected_fields": list(unexpected_fields),
        }, 400
    return None


@course_routes.get("/api/courses")
def get_all_courses():
    """Endpoint para listar todos os cursos"""
    conn = get_db_connection()
    courses = conn.execute(COURSE_QUERIES.GET_ALL_COURSES).fetchall()
    conn.close()

    return [
        {
            "id": course["id"],
            "name": course["name"],
            "enrolled_students": course["enrolled_students"],
            "max_students": course["max_students"],
            "created_at": course["created_at"],
        }
        for course in courses
    ], 200


@course_routes.get("/api/course/<string:id>")
def get_course(id):
    """Endpoint para retornar um curso específico"""
    conn = get_db_connection()
    course = conn.execute(COURSE_QUERIES.GET_COURSE, (id,)).fetchone()
    conn.close()

    if course:
        return {
            "id": course["id"],
            "name": course["name"],
            "enrolled_students": course["enrolled_students"],
            "max_students": course["max_students"],
            "created_at": course["created_at"],
        }, 200
    else:
        return {"message": CourseErrorMessages.COURSE_NOT_FOUND.value}, 404


@course_routes.put("/api/course/<string:id>")
def update_course(id):
    """Endpoint para atualizar um curso"""
    connection = get_db_connection()
    data = request.get_json()

    course = connection.execute(COURSE_QUERIES.GET_COURSE, (id,)).fetchone()

    # Se o curso não existir, retorna 404
    if not course:
        return {"message": CourseErrorMessages.COURSE_NOT_FOUND.value}, 404

    # Define the allowed fields
    allowed_fields = {"name", "max_students", "enrolled_students"}

    # Validate fields
    validation_error = validate_fields(data, allowed_fields)
    if validation_error:
        return validation_error

    # Se algum campo não for passado, mantém o valor atual
    name = data.get("name") if "name" in data else course["name"]
    max_students = (
        data.get("max_students") if "max_students" in data else course["max_students"]
    )
    enrolled_students = (
        data.get("enrolled_students")
        if "enrolled_students" in data
        else course["enrolled_students"]
    )

    # Se o número máximo de estudantes for menor que o número de estudantes
    # matrículados no momento, retorna 400
    if max_students < enrolled_students:
        return {
            "message": CourseErrorMessages.MAX_STUDENTS_LESS_THAN_ENROLLED.value
        }, 400

    cursor = connection.cursor()
    cursor.execute(
        COURSE_QUERIES.UPDATE_COURSE, (name, max_students, enrolled_students, id)
    )
    connection.commit()
    cursor.close()
    connection.close()

    return {"message": CourseSuccessMessages.COURSE_UPDATED.value}, 200


@course_routes.post("/api/course")
def create_course():
    """Endpoint para criar um curso"""
    connection = get_db_connection()
    data = request.get_json()

    # Define the allowed fields
    allowed_fields = {"name", "max_students", "enrolled_students"}

    # Validate fields
    validation_error = validate_fields(data, allowed_fields)
    if validation_error:
        return validation_error

    if "name" not in data or "max_students" not in data:
        return {"error": CourseErrorMessages.MISSING_NAME_OR_MAX_STUDENTS.value}, 400

    id = str(uuid.uuid4())
    name = data["name"]
    max_students = data["max_students"]
    date = (
        datetime.now(timezone.utc)
        .astimezone(timezone(timedelta(hours=-3)))
        .strftime("%Y-%m-%d %H:%M:%S")
    )

    try:
        cursor = connection.cursor()
        cursor.execute(COURSE_QUERIES.CREATE_COURSES_TABLE)
        cursor.execute(COURSE_QUERIES.INSERT_COURSE, (id, name, max_students, date))
        course_id = cursor.fetchone()[0]
        connection.commit()
        return {
            "id": course_id,
            "message": CourseSuccessMessages.COURSE_CREATED.value,
        }, 201
    finally:
        cursor.close()
        connection.close()


@course_routes.delete("/api/course/<string:id>")
def delete_course(id):
    """Endpoint para excluir um curso"""
    connection = get_db_connection()
    cursor = connection.cursor()

    course = connection.execute(COURSE_QUERIES.GET_COURSE, (id,)).fetchone()

    if not course:
        return {"message": CourseErrorMessages.COURSE_NOT_FOUND.value}, 404

    # Remove todos os alunos matriculados no curso
    enrolled_students = course["enrolled_students"]
    if enrolled_students > 0:
        students = find_students_by_course_id(id)
        for student in students:
            cursor.execute(
                STUDENT_QUERIES.UPDATE_STUDENT,
                (student["name"], student["age"], None, student["id"]),
            )
        connection.commit()

    cursor.execute(COURSE_QUERIES.DELETE_COURSE, (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return {"message": CourseSuccessMessages.COURSE_DELETED.value}, 200
