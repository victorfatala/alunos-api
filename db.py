import sqlite3


class SQLQueries:
    def __init__(self, filepath):
        self._queries = {}
        self._load_queries(filepath)

    def _load_queries(self, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            sql = file.read()
            for block in sql.split("--"):
                lines = block.strip().split("\n", 1)
                if len(lines) == 2:
                    name, query = lines
                    self._queries[name.strip()] = query.strip()

    def __getattr__(self, name):
        if name in self._queries:
            return self._queries[name]
        raise AttributeError(f"Query '{name}' not found in SQL file.")


# Load queries from the .sql files
STUDENT_QUERIES = SQLQueries("queries/students.sql")
COURSE_QUERIES = SQLQueries("queries/courses.sql")


# Connect to the database
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
