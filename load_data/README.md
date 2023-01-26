To create and insert the data in the database:

Download the data:

```bash
for table in "Tags" "Badges" "PostLinks" "Posts" "Users" "Votes"
do
    curl --proxy socks5h://localhost:8080 -LO https://archive.org/download/stackexchange/stackoverflow.com-$table.7z
done
```

Extract the xmls:
```bash
for table in "Tags" "Badges" "PostLinks" "Posts" "Users" "Votes"
do
    7z x stackoverflow.com-$table.7z
done
```

Move the xmls, except `Posts`, to `csv_convertion/xml` and create `csv_convertion/csv`, then run the extractor container inside csv_convertion:

```bash
docker compose up
```

Move the `Posts.xml` file to the `csv_convertion/xml` directory, drop the previous files. Run `posts_spliter.sh` to split the posts in 10 parts. Run `posts_conversion.sh` to convert all the parts from xml to csv.

Create pg_data directory in the root of the project to store the database files. Run the docker compose with the current user:

```bash
mkdir pg_data
UID=$(id -u) GID=$(id -g) docker compose up -d
```

Move csv files to `pg_data/csv` and copy the `load_xmls_copy.sql` script:

```bash
mv load_data/csv_convertion/csv pg_data/csv
cp load_data/load_xmls_copy.sql pg_data/
```

Finally run the copy script:

```bash
UID=$(id -u) GID=$(id -g) docker compose exec postgres psql -h localhost -p 5432 -U postgres -d stack_overflow -a -f /var/lib/postgresql/data/load_xmls_copy.sql
```

Create the new table with the posts since 2019:

```bash
UID=$(id -u) GID=$(id -g) docker compose exec postgres psql -h localhost -p 5432 -U postgres -d stack_overflow -c "CREATE TABLE posts_19 AS SELECT * FROM posts WHERE last_activity_date >= date '2019-01-01';"
```
