import psycopg2
import gensim
import argparse
import numpy as np
import faiss
from faiss import write_index
from multiprocessing import Pool
import logging
import time
import sys


DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="127.0.0.1"
DB_NAME="stack_overflow"

VECTOR_SIZE=50
EPOCHS=50
MIN_COUNT=200
WORKERS=8

PROCESS_POOL_SIZE=8

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()


def process_post(post_data):
    p_id, title, body = post_data
    post_text = body
    if title is not None:
        post_text = title + "\n\n" + body
    tokens = gensim.utils.simple_preprocess(post_text)
    # Use string due to int management in doc2vec
    # https://stackoverflow.com/questions/43051902/gensim-docvecs-most-similar-returns-ids-that-dont-exist
    return gensim.models.doc2vec.TaggedDocument(tokens, [str(p_id)])

def create_tagged_docs(port, tag, until_year, limit=None):
    connection = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=port, database=DB_NAME)

    posts_query = f"""
        select p.id, p.title, p.body_text
        from posts_19 p
        join posts_19_tags pt on pt.post_id=p.id
        join tags t on pt.tag_id=t.id
        where p.body_text is not null
        and p.post_type_id=1 
        and creation_date < '{until_year}-01-01'
        and t.tag_name = '{tag}'"""
    if limit is not None:
        posts_query += f" limit {limit}"

    start_time = time.time()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(posts_query)
            posts = cursor.fetchall()
    logger.info(f"Query time: {time.time() - start_time}")

    start_time = time.time()
    with Pool(PROCESS_POOL_SIZE) as p:
        posts = p.map(process_post, posts)
    logger.info(f"Document processing time: {time.time() - start_time}")
    return posts            

class Doc2VecTrainer:
    def __init__(self, posts) -> None:
        self.posts = posts

    def run(self, file_names):
        logger.info(f"Posts for training: {len(self.posts)}")
        start_time = time.time()
        model = gensim.models.doc2vec.Doc2Vec(self.posts, vector_size=VECTOR_SIZE, epochs=EPOCHS,
                                              min_count=MIN_COUNT, workers=WORKERS)
        logger.info(f"Doc2Vec training time: {time.time() - start_time}")
        model.save(f'{file_names}.doc')
        logger.info(f"Vectors in trained model: {len(model.dv)}")

        start_time = time.time()
        p_vectors_ids = [(model.infer_vector(p.words), p.tags[0]) for p in self.posts]
        logger.info(f"Vectors inference time: {time.time() - start_time}")
        vectors, vectors_ids = zip(*p_vectors_ids)
        vectors = np.array(vectors)
        vectors_ids = np.array(vectors_ids)

        start_time = time.time()
        index = faiss.index_factory(VECTOR_SIZE, "IDMap,Flat")
        index.train(vectors)
        index.add_with_ids(vectors, vectors_ids)
        logger.info(f"Faiss index creation time: {time.time() - start_time}")
        write_index(index, f'{file_names}.index')

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train doc2vec.')
    parser.add_argument('port')
    parser.add_argument('tag')
    parser.add_argument('until_year')
    parser.add_argument('file_names')
    parser.add_argument('limit', nargs='?')
    args = parser.parse_args()

    logger.info(f"""Arguments: port:{args.port}, tag:{args.tag}, until_year:{args.until_year},
                    limit:{args.limit}, file_names:{args.file_names}""")
    Doc2VecTrainer(create_tagged_docs(args.port, args.tag, args.until_year,
                                      args.limit)).run(args.file_names)