import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request

CREATE_STUDENTS_TABLE = (
    "CREATE TABLE IF NOT EXISTS students (id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, age INTEGER NOT NULL);"
)

GET_ALL_STUNDETS = (
    "SELECT * FROM students;"
)

GET_STUDENT = (
    "SELECT * FROM students WHERE id = ?;"
)

UPDATE_STUDENT = (
    "UPDATE students SET name = ?, age = ? WHERE id = ?;"
)

INSERT_STUDENT = (
    "INSERT INTO students (id, name, age, created_at) VALUES (?, ?, ?, ?) RETURNING id;"
)

DELETE_STUDENT = (
    "DELETE FROM students WHERE id = ?;"
)



app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/api")
def index():
    """Endpoint para mensagem de boas-vindas"""
    return {"message": "Olá, bem-vindo à Alunos API!"}, 200


@app.route("/api/students", methods=["GET"])
def get_all_students():
    """Endpoint para listar todos os alunos"""
    conn = get_db_connection()
    students = conn.execute(GET_ALL_STUNDETS).fetchall()
    conn.close()

    return [
        {"id": student["id"], "name": student["name"], "age": student["age"], "created_at": student["created_at"]}
        for student in students
    ], 200


@app.get("/api/student/<string:id>")
def get_student(id):
    """Endpoint para retornar um aluno específico"""
    conn = get_db_connection()
    student = conn.execute(GET_STUDENT, (id,)).fetchone()
    conn.close()

    if student:
        return {
            "id": student["id"],
            "name": student["name"],
            "age": student["age"],
            "created_at": student["created_at"]
        }, 200
    else:
        return {"message": "Aluno não encontrado."}, 404
    

@app.put("/api/student/<string:id>")
def update_student(id):
    """Endpoint para atualizar um aluno"""
    connection = get_db_connection()
    data = request.get_json()

    # Se o aluno não existir, retorna 404
    student = connection.execute(GET_STUDENT, (id,)).fetchone()
    if not student:
        return {"message": "Aluno não encontrado."}, 404

    # Se algum campo não for passado, mantém o valor atual
    name = data.get("name") if "name" in data else student["name"]
    age = data.get("age") if "age" in data else student["age"]

    cursor = connection.cursor()
    cursor.execute(
        UPDATE_STUDENT,
        (name, age, id)
    )
    connection.commit()
    cursor.close()
    connection.close()

    return {"message": f"Aluno(a) {name} atualizado com sucesso."}, 200


@app.post("/api/student")
def create_student():
    """Endpoint para criar um aluno"""
    connection = get_db_connection()
    data = request.get_json()

    if "name" not in data or "age" not in data:
        return {"error": "Faltando nome ou idade"}, 400

    id = str(uuid.uuid4())
    name = data["name"]
    age = data["age"]
    date = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor = connection.cursor()
        cursor.execute(CREATE_STUDENTS_TABLE)
        cursor.execute(INSERT_STUDENT, (id, name, age, date))
        student_id = cursor.fetchone()[0]
        connection.commit()
        return {"id": student_id, "message": f"Aluno(a) {name} criado."}, 201
    finally:
        cursor.close()
        connection.close()


@app.delete("/api/student/<string:id>")
def delete_student(id):
    """Endpoint para excluir um aluno"""
    connection = get_db_connection()
    cursor = connection.cursor()

    student = connection.execute(GET_STUDENT, (id,)).fetchone()
    if not student:
        return {"message": "Aluno não encontrado."}, 404
    
    cursor.execute(DELETE_STUDENT, (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return {"message": f"Aluno(a) {student['name']} foi excluído(a) com sucesso."}, 200

