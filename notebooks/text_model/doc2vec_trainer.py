import psycopg2
import gensim
import argparse
import numpy as np
import faiss
from faiss import write_index


DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="127.0.0.1"
DB_NAME="stack_overflow"

VECTOR_SIZE=50
EPOCHS=20
HS=1
MIN_COUNT=200
WORKERS=8

class DBCorpus():
    def __init__(self, port, tag, until_year, batch_size) -> None:
        self.connection = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=port, database=DB_NAME)
        self.tag, self.until_year, self.batch_size = tag, until_year, batch_size

    def _get_batch(self, idx):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(f"""select p.id, p.title, p.body_text
                from posts_19 p
                join posts_19_tags pt on pt.post_id=p.id
                join tags t on pt.tag_id=t.id
                where p.body_text is not null
                and p.post_type_id=1 
                and creation_date < '{self.until_year}-01-01'
                and t.tag_name = '{self.tag}'
                offset {self.batch_size*idx} limit {self.batch_size}""")
                return cursor.fetchall()

    def __iter__(self):
        idx = 0
        posts = self._get_batch(idx)
        while len(posts) > 0:
            for p_id, title, body in posts:
                post_text = body
                if title is not None:
                    post_text = title + "\n\n" + body
                tokens = gensim.utils.simple_preprocess(post_text)
                # Use string due to int management in doc2vec
                # https://stackoverflow.com/questions/43051902/gensim-docvecs-most-similar-returns-ids-that-dont-exist
                yield gensim.models.doc2vec.TaggedDocument(tokens, [str(p_id)])
            
            idx += 1
            posts = self._get_batch(idx)
            

class Doc2VecTrainer:
    def __init__(self, corpus) -> None:
        self.corpus = corpus

    def run(self):
        model = gensim.models.doc2vec.Doc2Vec(self.corpus, vector_size=VECTOR_SIZE, epochs=EPOCHS,
                                              hs=HS, min_count=MIN_COUNT, workers=WORKERS)
        model.save(f'{self.corpus.tag}.doc')

        p_vectors_ids = [(model.infer_vector(p.words), p.tags[0]) for p in self.corpus]
        vectors, vectors_ids = zip(*p_vectors_ids)
        vectors = np.array(vectors)
        vectors_ids = np.array(vectors_ids)
        index = faiss.index_factory(VECTOR_SIZE, "IDMap,Flat")
        index.train(vectors)
        index.add_with_ids(vectors, vectors_ids)
        write_index(index, f'{self.corpus.tag}.index')

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train doc2vec.')
    parser.add_argument('port')
    parser.add_argument('tag')
    parser.add_argument('until_year')
    parser.add_argument('batch_size', type=int)
    args = parser.parse_args()

    Doc2VecTrainer(DBCorpus(args.port, args.tag, args.until_year, args.batch_size)).run()