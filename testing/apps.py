from django.apps import AppConfig
import psycopg2


class TestingConfig(AppConfig):
    name = 'testing'

    # def ready(self):
    #     conn = psycopg2.connect(
    #         dbname='contest',
    #         user='myuser',
    #         host='localhost',
    #         port=5432,
    #         password='password',
            # options=f'-c search_path=contesttest'
        # )
        # print(conn)
        # cur = conn.cursor()
        # cur.execute('SELECT * FROM contesttest.category')
        # print(cur.fetchall())
        # print("HELLO")
