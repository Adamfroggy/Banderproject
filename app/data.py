from os import getenv

import certifi
from certifi import where
from dotenv import load_dotenv
from MonsterLab import Monster
from pandas import DataFrame
from pymongo import MongoClient

load_dotenv()


class Database:
    def __init__(self):
        """
        Initialize the database class.
        Establishes a connection to the MongoDB database using environment variables.
        """
        self.db = MongoClient(
            getenv("MONGO_URI"),
            tlsCAFile=certifi.where()
        )["BanderCluster"]
        self.collection = self.db.get_collection("COLLECTION_NAME")

    def seed(self, amount):
        """
        Insert a specified number of documents into the database collection.
        :param amount: Number of documents to insert.
        """
        monsters = [Monster().to_dict() for _ in range(amount)]
        self.collection.insert_many(monsters)

    def reset(self):
        """
        Delete all documents from collection.
        """
        self.collection.delete_many({})

    def count(self) -> int:
        """
        Return the number of documents in the collection.

        :return: Number of documents in the collection.
        """
        return self.collection.count_documents({})

    def dataframe(self) -> DataFrame:
        """
        Return a DataFrame containing all documents in the collection.

        :return: DataFrame with all documents.
        """
        cursor = self.collection.find({}, {"_id": False})
        return DataFrame(list(cursor))

    def html_table(self) -> str | None:
        """
        Return an HTML table representation of the DataFrame, or None if the collection is empty.

        :return: HTML table as a string or None.
        """
        df = self.dataframe()
        if df.empty:
            return None
        return df.to_html()

    # Explanation Summary Notes:
    # The Database class is designed to interface with a MongoDB database securely.
    # - The `__init__` method establishes a connection using credentials from environment variables
    # and ensures a secure connection using a TLS certificate.
    # - The `seed` method inserts a specified number of random Monster documents into the database.
    # - The `reset` method deletes all documents from the database collection.
    # - The `count` method returns the total number of documents present in the collection.
    # - The `dataframe` method fetches all documents and converts them
    # into a pandas DataFrame for easy manipulation and analysis.
    # - The `html_table` method converts the DataFrame into an HTML table,
    # providing a convenient way to visualize the data,
    # returning None if the DataFrame is empty.

if __name__ == "__main__":
    db = Database()
    db.seed(1000)
