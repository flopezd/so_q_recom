from sentence_transformers import models, SentenceTransformer, InputExample, losses
from sentence_transformers.datasets import NoDuplicatesDataLoader
import psycopg2
import numpy as np
import time
import faiss
import logging
import argparse
from faiss import write_index
import sys


DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="127.0.0.1"
DB_NAME="stack_overflow"

WARMUP_PERC=0.1
SBERT_PREPOSITION="SBERT_"

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()

class DBDatasets:
    def __init__(self, port):
        self.connection = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=port, database=DB_NAME)
        
    def get_similar_docs_sample(self, tag, until_year, limit=100):
        with self.connection:
            with self.connection.cursor() as cursor:            
                start_time = time.time()
                cursor.execute(f"""select q.body_text, q.title, sq.body_text, sq.title
                FROM posts_19 q
                JOIN posts_19_tags pt on pt.post_id=q.id
                JOIN tags t on pt.tag_id=t.id
                JOIN posts_19 q_aa ON q_aa.id = q.accepted_answer_id
                JOIN posts_19 sa ON sa.owner_user_id=q_aa.owner_user_id
                JOIN posts_19 sq ON sq.id=sa.parent_id
                WHERE q.body_text is not null
                and sa.parent_id != q.id 
                and q.post_type_id=1 
                and q.creation_date < '{until_year}-01-01'
                and t.tag_name = '{tag}'
                and q_aa.post_type_id=2 
                and sa.post_type_id=2
                limit {limit}""")
                posts = cursor.fetchall()
                logger.info(f"Query time: {time.time() - start_time}")
                return posts
        
    def get_docs_sample(self, tag, until_year, limit=None):
        with self.connection:
            with self.connection.cursor() as cursor:  
                posts_query = f"""select p.id, p.title, p.body_text
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
                cursor.execute(posts_query)
                posts = cursor.fetchall()
                logger.info(f"Query time: {time.time() - start_time}")
                return posts

class SBERTTrainer:
    def __init__(self, posts, batch_size=2, base_model='nli-distilroberta-base-v2'):
        train_examples = [] 
        for q_text, q_title, sq_text, sq_title in posts:
            post_text = q_text
            if q_title is not None:
                post_text = q_title + "\n\n" + q_text
            sim_post_text = sq_text
            if sq_title is not None:
                sim_post_text = sq_title + "\n\n" + sq_text
            train_examples.append(InputExample(texts=[post_text, sim_post_text]))
        self.train_dataloader = NoDuplicatesDataLoader(train_examples, batch_size=batch_size)
        bert = models.Transformer(base_model)
        pooler = models.Pooling(
            bert.get_word_embedding_dimension(),
            pooling_mode_mean_tokens=True
        )

        self.model = SentenceTransformer(modules=[bert, pooler])

    def run(self, num_epochs, model_path):
        train_loss = losses.MultipleNegativesRankingLoss(model=self.model)
        warmup_steps = int(len(self.train_dataloader) * num_epochs * WARMUP_PERC)

        self.model.fit(train_objectives=[(self.train_dataloader, train_loss)], epochs=num_epochs, warmup_steps=warmup_steps,
                                    output_path=SBERT_PREPOSITION+model_path, show_progress_bar=False)

class FaissIndexTrainer:
    def __init__(self, all_posts):
        self.posts_texts = []
        self.posts_ids = []
        for p_id, title, body in all_posts:
            post_text = body
            if title is not None:
                post_text = title + "\n\n" + body
            self.posts_ids.append(p_id)
            self.posts_texts.append(post_text)

    def run(self, model, file_names, vectors_dim=768, index_type="IDMap,Flat"):
        start_time = time.time()
        encoded_data = model.encode(self.posts_texts)
        logger.info(f"Vectors inference time: {time.time() - start_time}")
        vectors_ids = np.array(self.posts_ids)

        start_time = time.time()
        index = faiss.index_factory(vectors_dim, index_type)
        index.train(encoded_data)
        index.add_with_ids(encoded_data, vectors_ids)
        logger.info(f"Faiss index creation time: {time.time() - start_time}")
        write_index(index, f'{file_names}.index')
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fine-tune SBERT and fit faiss index.')
    parser.add_argument('port')
    parser.add_argument('tag')
    parser.add_argument('until_year')
    parser.add_argument('file_names')
    parser.add_argument('similar_limit')
    parser.add_argument('--batch_size', nargs='?', type=int)
    parser.add_argument('--docs_limit', nargs='?')
    parser.add_argument('--num_epochs', nargs='?', default=1, type=int)
    args = parser.parse_args()

    logger.info(f"""Arguments: port:{args.port}, tag:{args.tag}, until_year:{args.until_year},
                    num_epochs:{args.num_epochs}, similar_limit:{args.similar_limit}, batch_size:{args.batch_size},
                    docs_limit:{args.docs_limit}, file_names:{args.file_names}""")
    
    db_ds = DBDatasets(args.port)
    sbert_trainer = SBERTTrainer(db_ds.get_similar_docs_sample(args.tag, args.until_year,
                                               args.similar_limit), args.batch_size)
    sbert_trainer.run(args.num_epochs, args.file_names)
    
    FaissIndexTrainer(db_ds.get_docs_sample(args.tag, args.until_year,
                                               args.docs_limit)).run(sbert_trainer.model, args.file_names)
    