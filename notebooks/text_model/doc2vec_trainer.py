import psycopg2
import gensim
import faiss
import numpy as np

class DBCorpus():
    def __init__(self) -> None:
        connection = psycopg2.connect(user="postgres", password="postgres", host="127.0.0.1", port="63333", database="stack_overflow")
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""select id, title, body_text
                from posts_19
                where body_text is not null
                limit 500""")
                self.posts = cursor.fetchall()

    def __iter__(self):
        for p_id, title, body in self.posts:
            post_text = body
            if title is not None:
                post_text = title + "\n\n" + body
            tokens = gensim.utils.simple_preprocess(post_text)
            yield gensim.models.doc2vec.TaggedDocument(tokens, [p_id])
            

class Doc2VecTrainer:
    def __init__(self) -> None:
        self.corpus = DBCorpus()

    def run(self):
        model = gensim.models.doc2vec.Doc2Vec(self.corpus, vector_size=50, epochs=10, hs=1, min_count=100, workers=7)
        model.save('model.doc')

if __name__ == "__main__":
    Doc2VecTrainer().run()