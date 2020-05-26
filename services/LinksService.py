from connection import connection
from datetime import datetime
import random
from server import Request, Response
from http import HTTPStatus


def generator_code():
    generated_code = "".join(
        [
            random.choice(
                "123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
            )
            for x in range(6)
        ]
    )
    return generated_code


class LinksService:
    @staticmethod
    def getAllLinks():
        cur = connection.cursor()
        cur.execute("SELECT id, original_url, code, created_at from links;")
        data = cur.fetchall()
        return [
            {"id": v[0], "original_url": v[1], "code": v[2], "created_at": v[3]}
            for v in data
        ]

    @staticmethod
    def createNewLink(original_url):
        generated_code = generator_code()
        cur = connection.cursor()
        cur.execute(
            "INSERT INTO links (original_url, code, created_at) VALUES  (%s, %s, %s) RETURNING id,code;",
            (original_url, generated_code, datetime.now()),
        )
        connection.commit()
        (link_id, link_code) = cur.fetchone()
        return (link_id, link_code)


@staticmethod
def increase_views_count(link_id:str):
    cur = connection.cursor()
    cur.execute("UPDATE links SET redirects_count=redirects_count + 1 WHERE id=%s",(link_id,))
    cur.commit()