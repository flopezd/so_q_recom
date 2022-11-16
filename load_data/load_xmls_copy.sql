COPY users FROM '/var/lib/postgresql/data/csv/Users.csv' DELIMITER ',' CSV HEADER;
COPY posts FROM '/var/lib/postgresql/data/csv/Posts.csv' DELIMITER ',' CSV HEADER;
COPY votes FROM '/var/lib/postgresql/data/csv/Votes.csv' DELIMITER ',' CSV HEADER;
COPY post_links FROM '/var/lib/postgresql/data/csv/PostLinks.csv' DELIMITER ',' CSV HEADER;
COPY badges FROM '/var/lib/postgresql/data/csv/Badges.csv' DELIMITER ',' CSV HEADER;
COPY tags FROM '/var/lib/postgresql/data/csv/Tags.csv' DELIMITER ',' CSV HEADER;
