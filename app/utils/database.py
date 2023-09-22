"""
This module provides functionalities to manage and interact with the election database.
"""

import mariadb


class ElectionDatabase:
    """
    A class to handle operations related to the election database.

    Attributes:
        config (dict): A dictionary containing the database configuration.
        conn (mariadb.connection): The MariaDB connection object.
        cursor (mariadb.cursor): The MariaDB cursor object.
    """

    def __init__(self, config):
        """
        Initializes the ElectionDatabase class with configuration parameters.

        Args:
            config (dict): A dictionary containing the database configuration parameters.
                           Expected keys: 'hostname', 'port', 'user', 'password', 'database'.
        """
        self.config = config
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
        """
        Prepares the database by creating necessary tables if they do not exist.
        """
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
        """
        Checks if a candidate exists in the database.

        Args:
            candidate (dict): A dictionary containing candidate details.

        Returns:
            bool: True if the candidate exists, False otherwise.
        """
        self.cursor.execute(
            "SELECT * FROM candidates WHERE name=%s", (candidate['name'],))
        return self.cursor.fetchone() is not None

    def voter_exists(self, voter):
        """
        Checks if a voter exists in the database.

        Args:
            voter (int): The ID of the voter.

        Returns:
            bool: True if the voter exists, False otherwise.
        """
        self.cursor.execute(
            "SELECT * FROM votes WHERE user_id=%s", (voter,))
        return self.cursor.fetchone() is not None

    def add_candidate(self, candidate):
        """
        Adds a candidate to the database.

        Args:
            candidate (dict): A dictionary containing candidate details.
                            Expected keys: 'name' and 'description'.
        """
        # intert name and description
        self.cursor.execute("INSERT INTO candidates (name, description) VALUES (%s, %s)",
                            (candidate['name'], candidate['description']))
        self.conn.commit()

    def add_voter(self, voter):
        """
        Adds a voter to the database.

        Args:
            voter (int): The ID of the voter.
        """
        self.cursor.execute(
            "INSERT INTO votes (user_id) VALUES (%s)", (voter,))
        self.conn.commit()

    def get_candidates(self):
        """
        Retrieves all candidates from the database.

        Returns:
            list: A list of tuples containing candidate details.
        """
        self.cursor.execute("SELECT * FROM candidates")
        return self.cursor.fetchall()

    def add_vote(self, voter, candidate):
        """
        Records a vote for a candidate in the database.

        Args:
            voter (int): The ID of the voter.
            candidate (int): The ID of the candidate.
        """
        self.cursor.execute(
            "UPDATE votes SET candidate_id=%s WHERE user_id=%s", (candidate, voter))
        self.cursor.execute(
            "UPDATE candidates SET votes=votes+1 WHERE id=%s", (candidate,))
        self.conn.commit()

    def has_voted(self, voter):
        """
        Checks if a voter has already cast their vote.

        Args:
            voter (int): The ID of the voter.

        Returns:
            bool: True if the voter has voted, False otherwise.
        """
        self.cursor.execute("SELECT * FROM votes WHERE user_id=%s", (voter,))
        return self.cursor.fetchone()[2] is not None

    def get_results(self):
        """
        Retrieves the election results.

        Returns:
            list: A list of tuples containing candidate names and their respective vote counts.
        """
        self.cursor.execute(
            "SELECT candidates.name, COUNT(votes.candidate_id) "
            "FROM candidates "
            "LEFT JOIN votes ON candidates.id = votes.candidate_id "
            "GROUP BY candidates.name"
        )
        return self.cursor.fetchall()
