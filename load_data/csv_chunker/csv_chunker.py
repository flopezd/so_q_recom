import pandas as pd
import os

csv_path = os.environ['CSV_PATH']
chunk_size = int(os.environ['CHUNK_SIZE'])
root_path, csv_ext = os.path.splitext(csv_path)

with pd.read_csv(csv_path, chunksize=chunk_size) as reader:
    i=0
    for chunk in reader:
        chunk.to_csv(root_path + f"_{i}" + csv_ext, index=False)
        i+=1
