import mariadb


class ElectionDatabase:
    def __init__(self, host, port, username, password, database):
        self.config = {
            'host': host,
            'port': port,
            'user': username,
            'password': password,
            'database': database
        }
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = mariadb.connect(**self.config)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def prepare_database(self):
        candidates_sql = """
        -- Create candidates table
        CREATE TABLE IF NOT EXISTS candidates (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            votes INT DEFAULT 0
        );"""
        votes_sql = """
        -- Create votes table
        CREATE TABLE IF NOT EXISTS votes (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            candidate_id INT,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        );
        """

        self.cursor.execute(candidates_sql)
        self.cursor.execute(votes_sql)
        self.conn.commit()

    def candidate_exists(self, candidate):
        self.cursor.execute(
            "SELECT * FROM candidates WHERE name=%s", (candidate['name'],))
        return self.cursor.fetchone() is not None

    def voter_exists(self, voter):
        self.cursor.execute(
            "SELECT * FROM votes WHERE user_id=%s", (voter,))
        return self.cursor.fetchone() is not None

    def add_candidate(self, candidate):
        # intert name and description
        self.cursor.execute("INSERT INTO candidates (name, description) VALUES (%s, %s)",
                            (candidate['name'], candidate['description']))
        self.conn.commit()

    def add_voter(self, voter):
        self.cursor.execute(
            "INSERT INTO votes (user_id) VALUES (%s)", (voter,))
        self.conn.commit()

    def get_candidates(self):
        self.cursor.execute("SELECT * FROM candidates")
        return self.cursor.fetchall()

    def add_vote(self, voter, candidate):
        self.cursor.execute(
            "UPDATE votes SET candidate_id=%s WHERE user_id=%s", (candidate, voter))
        self.cursor.execute(
            "UPDATE candidates SET votes=votes+1 WHERE id=%s", (candidate,))
        self.conn.commit()

    def has_voted(self, voter):
        self.cursor.execute("SELECT * FROM votes WHERE user_id=%s", (voter,))
        return self.cursor.fetchone()[2] is not None

    def get_results(self):
        self.cursor.execute(
            "SELECT candidates.name, COUNT(votes.candidate_id) FROM candidates LEFT JOIN votes ON candidates.id = votes.candidate_id GROUP BY candidates.name")
        return self.cursor.fetchall()
