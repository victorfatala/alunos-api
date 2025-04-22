-- CREATE_COURSES_TABLE
CREATE TABLE IF NOT EXISTS courses (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    enrolled_students INTEGER NOT NULL DEFAULT 0,
    max_students INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GET_ALL_COURSES
SELECT * FROM courses;

-- GET_COURSE
SELECT * FROM courses WHERE id = ?;

-- UPDATE_COURSE
UPDATE courses SET name = ?, enrolled_students = ?, max_students = ? WHERE id = ?;

-- UPDATE_ENROLLED_STUDENTS
UPDATE courses SET enrolled_students = ? WHERE id = ?;

-- INSERT_COURSE
INSERT INTO courses (id, name, max_students, created_at) VALUES (?, ?, ?, ?) RETURNING id;

-- DELETE_COURSE
DELETE FROM courses WHERE id = ?;