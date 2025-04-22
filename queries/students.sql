-- CREATE_STUDENTS_TABLE
CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    course_enrolled TEXT DEFAULT NULL,
    created_at TEXT NOT NULL
);

-- GET_ALL_STUDENTS
SELECT * FROM students;

-- GET_STUDENT
SELECT * FROM students WHERE id = ?;

-- GET_STUDENT_BY_COURSE_ID
SELECT * FROM students WHERE course_enrolled = ?;

-- UPDATE_STUDENT
UPDATE students SET name = ?, age = ?, course_enrolled = ? WHERE id = ?;

-- INSERT_STUDENT
INSERT INTO students (id, name, age, course_enrolled, created_at) VALUES (?, ?, ?, ?, ?) RETURNING id;

-- DELETE_STUDENT
DELETE FROM students WHERE id = ?;