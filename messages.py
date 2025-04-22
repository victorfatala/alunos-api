from enum import Enum


class GeneralErrorMessages(Enum):
    UNEXPECTED_FIELDS = "Campos inesperados encontrados."


class StudentSuccessMessages(Enum):
    STUDENT_CREATED = "Aluno(a) criado com sucesso."
    STUDENT_UPDATED = "Aluno(a) atualizado com sucesso."
    STUDENT_DELETED = "Aluno(a) deletado com sucesso."


class StudentErrorMessages(Enum):
    STUDENT_NOT_FOUND = "Aluno não encontrado."
    MISSING_NAME_OR_AGE = "Faltando nome ou idade."


class CourseSuccessMessages(Enum):
    COURSE_CREATED = "Curso criado com sucesso."
    COURSE_UPDATED = "Curso atualizado com sucesso."
    COURSE_DELETED = "Curso deletado com sucesso."


class CourseErrorMessages(Enum):
    COURSE_NOT_FOUND = "Curso não encontrado."
    MAX_STUDENTS_LESS_THAN_ENROLLED = "Número máximo de alunos não pode ser menor que o número de alunos matriculados."
    MISSING_NAME_OR_MAX_STUDENTS = "Faltando nome ou número máximo de alunos."
    MAX_STUDENTS_REACHED = "Número máximo de alunos atingido neste curso."
