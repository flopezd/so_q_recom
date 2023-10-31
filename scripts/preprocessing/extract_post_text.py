from multiprocessing import Pool

import psycopg2
from bs4 import BeautifulSoup
from psycopg2.extras import execute_values

BATCH_SIZE = 500000


def extract_text(id_body):
    post_id, body = id_body
    return post_id, BeautifulSoup(body, "html.parser").get_text().encode(
        "utf-8", "backslashreplace"
    ).decode().replace("\0", "\\0")


connection = psycopg2.connect(
    user="postgres",
    password="postgres",
    host="127.0.0.1",
    port="54320",
    database="stack_overflow",
)

with connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """select count(*)
        from posts_19 where body is not null"""
        )
        total_posts = cursor.fetchall()[0][0]

total_batches = (total_posts // BATCH_SIZE) + 1

for batch_index in range(total_batches):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""select id, body
            from posts_19
            where body is not null
            order by id
            limit {BATCH_SIZE} offset {BATCH_SIZE*batch_index}"""
            )
            posts = cursor.fetchall()

    with Pool(8) as p:
        maped_posts = p.map(extract_text, posts)

    with connection:
        with connection.cursor() as cursor:
            execute_values(
                cursor,
                """UPDATE posts_19 SET body_text = data.body_text
                                    FROM (VALUES %s) AS data (id, body_text)
                                    WHERE posts_19.id = data.id""",
                maped_posts,
            )
    print(f"{(batch_index+1)/total_batches*100:.2f}% posts procesados")
