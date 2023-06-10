import sqlite3 as sq
import pandas as pd
import numpy as np

class DataBase:
    def __init__(self):
        self.conn = sq.connect('Anime.db')
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE if not exists data_table([name] TEXT, [link] TEXT, [year] TEXT,
            [category] TEXT, [rating] TEXT, [update_date] TEXT, [description] TEXT)""")
        self.conn.commit()

    def check_data(self, name, update_date):
        cursor = self.conn.cursor()
        db = ''' SELECT COUNT(*) FROM data_table WHERE name = ? AND update_date = ? '''
        cursor.execute(db, (name, update_date))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0

    def insert_data(self, name, link, year, category, rating, update_date, description):
        cursor = self.conn.cursor()
        if self.check_data(name, update_date):
            return False
        db = '''INSERT INTO data_table(NAME, LINK, YEAR, CATEGORY, RATING, UPDATE_DATE, DESCRIPTION)
        VALUES(?, ?, ?, ?, ?, ?, ?)'''
        cursor.execute(db, (name, link, year, category, rating, update_date, description))
        self.conn.commit()
        #cursor.close()
        return True

    def actualize_data(self, name, update_date):
        cursor = self.conn.cursor()
        db = '''UPDATE data_table SET UPDATE_DATE = ?
        WHERE NAME = ?'''
        cursor.execute(db, (update_date, name))
        a = cursor.rowcount
        self.conn.commit()
        cursor.close()
        return a

    def show_data(self):
        query = "SELECT * FROM data_table"
        df = pd.read_sql_query(query, self.conn)
        return df


