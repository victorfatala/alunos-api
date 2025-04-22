from flask import Flask
from db import SQLQueries
from routes.courses import course_routes
from routes.students import student_routes

app = Flask(__name__)
app.register_blueprint(course_routes)
app.register_blueprint(student_routes)


@app.route("/api")
def index():
    """Endpoint para mensagem de boas-vindas"""
    return {"message": "Olá, bem-vindo à Alunos API!"}, 200


app.run(debug=True)
