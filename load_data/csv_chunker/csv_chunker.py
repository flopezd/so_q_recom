import dask.dataframe as dd
import os

csv_path = os.environ['CSV_PATH']
npartitions = int(os.environ['N_PARTITIONS'])
root_path, csv_ext = os.path.splitext(csv_path)

df = dd.read_csv(csv_path, assume_missing=True)
df = df.repartition(npartitions=npartitions)
df.to_csv(f"{root_path}_*{csv_ext}", index=False)