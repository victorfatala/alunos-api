from flask import Blueprint, request
import uuid
from datetime import datetime, timezone, timedelta
from db import STUDENT_QUERIES, COURSE_QUERIES, get_db_connection
from messages import (
    GeneralErrorMessages,
    CourseErrorMessages,
    StudentSuccessMessages,
    StudentErrorMessages,
)

student_routes = Blueprint("student_routes", __name__)


def validate_fields(data, allowed_fields):
    """Valida se existem campos inesperados no payload."""
    unexpected_fields = set(data.keys()) - allowed_fields
    if unexpected_fields:
        return {
            "error": GeneralErrorMessages.UNEXPECTED_FIELDS.value,
            "unexpected_fields": list(unexpected_fields),
        }, 400
    return None


@student_routes.get("/api/students")
def get_all_students():
    """Endpoint para listar todos os alunos"""
    conn = get_db_connection()
    students = conn.execute(STUDENT_QUERIES.GET_ALL_STUDENTS).fetchall()
    conn.close()

    return [
        {
            "id": student["id"],
            "name": student["name"],
            "age": student["age"],
            "course_enrolled": student["course_enrolled"],
            "created_at": student["created_at"],
        }
        for student in students
    ], 200


@student_routes.get("/api/student/<string:id>")
def get_student(id):
    """Endpoint para retornar um aluno específico"""
    conn = get_db_connection()
    student = conn.execute(STUDENT_QUERIES.GET_STUDENT, (id,)).fetchone()
    conn.close()

    if student:
        return {
            "id": student["id"],
            "name": student["name"],
            "age": student["age"],
            "course_enrolled": student["course_enrolled"],
            "created_at": student["created_at"],
        }, 200
    else:
        return {"message": StudentErrorMessages.STUDENT_NOT_FOUND.value}, 404


@student_routes.put("/api/student/<string:id>")
def update_student(id):
    """Endpoint para atualizar um aluno"""
    connection = get_db_connection()
    data = request.get_json()

    student = connection.execute(STUDENT_QUERIES.GET_STUDENT, (id,)).fetchone()

    # Se o aluno não existir, retorna 404
    if not student:
        return {"message": StudentErrorMessages.STUDENT_NOT_FOUND.value}, 404

    # Define the allowed fields
    allowed_fields = {"name", "age", "course_enrolled"}

    # Validate fields
    validation_error = validate_fields(data, allowed_fields)
    if validation_error:
        return validation_error

    # Se algum campo não for passado, mantém o valor atual
    name = data.get("name") if "name" in data else student["name"]
    age = data.get("age") if "age" in data else student["age"]
    course_enrolled = (
        data.get("course_enrolled")
        if "course_enrolled" in data
        else student["course_enrolled"]
    )

    if course_enrolled:
        # Verifica se o curso existe
        course = connection.execute(
            COURSE_QUERIES.GET_COURSE, (course_enrolled,)
        ).fetchone()
        if not course:
            return {"message": CourseErrorMessages.COURSE_NOT_FOUND.value}, 404

        # Verifica se o número máximo de estudantes foi atingido
        if course["max_students"] <= course["enrolled_students"]:
            return {
                "message": CourseErrorMessages.MAX_STUDENTS_REACHED.value,
                "course_id": course["id"],
            }, 400

        # Atualiza o número de estudantes matriculados no curso
        cursor = connection.cursor()
        cursor.execute(
            COURSE_QUERIES.UPDATE_ENROLLED_STUDENTS,
            (course["enrolled_students"] + 1, course["id"]),
        )
        connection.commit()

    elif student["course_enrolled"] != course_enrolled:
        # Se o aluno não estiver mais matriculado em nenhum curso, atualiza o número de estudantes matriculados no curso
        cursor = connection.cursor()
        cursor.execute(
            COURSE_QUERIES.UPDATE_ENROLLED_STUDENTS,
            (course["enrolled_students"] - 1, student["course_enrolled"]),
        )
        connection.commit()

    cursor = connection.cursor()
    cursor.execute(STUDENT_QUERIES.UPDATE_STUDENT, (name, age, course_enrolled, id))
    connection.commit()
    cursor.close()
    connection.close()

    return {"message": StudentSuccessMessages.STUDENT_UPDATED.value}, 200


@student_routes.post("/api/student")
def create_student():
    """Endpoint para criar um aluno"""
    connection = get_db_connection()
    data = request.get_json()

    # Define the allowed fields
    allowed_fields = {"name", "age", "course_enrolled"}

    # Validate fields
    validation_error = validate_fields(data, allowed_fields)
    if validation_error:
        return validation_error

    if "name" not in data or "age" not in data:
        return {"error": StudentErrorMessages.MISSING_NAME_OR_AGE.value}, 400

    id = str(uuid.uuid4())
    name = data["name"]
    age = data["age"]
    course_enrolled = data.get("course_enrolled", None)
    date = (
        datetime.now(timezone.utc)
        .astimezone(timezone(timedelta(hours=-3)))
        .strftime("%Y-%m-%d %H:%M:%S")
    )

    if course_enrolled:
        # Verifica se o curso existe
        course = connection.execute(
            COURSE_QUERIES.GET_COURSE, (course_enrolled,)
        ).fetchone()
        if not course:
            return {"message": CourseErrorMessages.COURSE_NOT_FOUND.value}, 404

        # Verifica se o número máximo de estudantes foi atingido
        if course["max_students"] <= course["enrolled_students"]:
            return {
                "message": CourseErrorMessages.MAX_STUDENTS_REACHED.value,
                "course_id": course["id"],
            }, 400

        # Atualiza o número de estudantes matriculados no curso
        cursor = connection.cursor()
        cursor.execute(
            COURSE_QUERIES.UPDATE_ENROLLED_STUDENTS,
            (course["enrolled_students"] + 1, course["id"]),
        )
        connection.commit()

    try:
        cursor = connection.cursor()
        cursor.execute(STUDENT_QUERIES.CREATE_STUDENTS_TABLE)
        cursor.execute(
            STUDENT_QUERIES.INSERT_STUDENT, (id, name, age, course_enrolled, date)
        )
        student_id = cursor.fetchone()[0]
        connection.commit()
        return {
            "id": student_id,
            "message": StudentSuccessMessages.STUDENT_CREATED.value,
        }, 201
    finally:
        cursor.close()
        connection.close()


@student_routes.delete("/api/student/<string:id>")
def delete_student(id):
    """Endpoint para excluir um aluno"""
    connection = get_db_connection()
    cursor = connection.cursor()

    student = connection.execute(STUDENT_QUERIES.GET_STUDENT, (id,)).fetchone()
    if not student:
        return {"message": StudentErrorMessages.STUDENT_NOT_FOUND.value}, 404

    # Remove o aluno do curso, se estiver matriculado
    if student["course_enrolled"]:
        course = connection.execute(
            COURSE_QUERIES.GET_COURSE, (student["course_enrolled"],)
        ).fetchone()
        cursor.execute(
            COURSE_QUERIES.UPDATE_ENROLLED_STUDENTS,
            (course["enrolled_students"] - 1, student["course_enrolled"]),
        )
        connection.commit()

    cursor.execute(STUDENT_QUERIES.DELETE_STUDENT, (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return {"message": StudentSuccessMessages.STUDENT_DELETED.value}, 200
