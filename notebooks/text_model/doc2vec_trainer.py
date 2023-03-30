import psycopg2
import gensim
import argparse

class DBCorpus():
    def __init__(self, port, tag, until_year, batch_size) -> None:
        self.connection = psycopg2.connect(user="postgres", password="postgres", host="127.0.0.1", port=port, database="stack_overflow")
        self.tag, self.until_year, self.batch_size = tag, until_year, batch_size

    def _get_batch(self, idx):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(f"""select p.id, p.title, p.body_text
                from posts_19 p
                join posts_19_tags pt on pt.post_id=p.id
                join tags t on pt.tag_id=t.id
                where p.body_text is not null
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
                yield gensim.models.doc2vec.TaggedDocument(tokens, [p_id])
            
            idx += 1
            posts = self._get_batch(idx)
            

class Doc2VecTrainer:
    def __init__(self, corpus) -> None:
        self.corpus = corpus

    def run(self):
        model = gensim.models.doc2vec.Doc2Vec(self.corpus, vector_size=50, epochs=20, hs=1, min_count=100, workers=7)
        model.save('model.doc')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train doc2vec.')
    parser.add_argument('port')
    parser.add_argument('tag')
    parser.add_argument('until_year')
    parser.add_argument('batch_size', type=int)
    args = parser.parse_args()

    Doc2VecTrainer(DBCorpus(args.port, args.tag, args.until_year, args.batch_size)).run()