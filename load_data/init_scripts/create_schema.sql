CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	account_id INTEGER,
	reputation INTEGER NOT NULL,
	views INTEGER DEFAULT 0,
	down_votes INTEGER DEFAULT 0,
	up_votes INTEGER DEFAULT 0,
	display_name VARCHAR(255) NOT NULL,
	location VARCHAR(512),
	profile_image_url VARCHAR(255),
	website_url VARCHAR(255),
	about_me TEXT,
	creation_date TIMESTAMP NOT NULL,
	last_access_date TIMESTAMP NOT NULL
);

CREATE TABLE posts (
	id SERIAL PRIMARY KEY,
	owner_user_id INTEGER REFERENCES users(id),
	last_editor_user_id INTEGER REFERENCES users(id),
	post_type_id SMALLINT NOT NULL,
	accepted_answer_id INTEGER REFERENCES posts(id),
	score INTEGER NOT NULL,
	parent_id INTEGER REFERENCES posts(id),
	view_count INTEGER,
	answer_count INTEGER DEFAULT 0,
	comment_count INTEGER DEFAULT 0,
	owner_display_name VARCHAR(64),
	last_editor_display_name VARCHAR(64),
	title VARCHAR(512),
	tags VARCHAR(512),
	content_license VARCHAR(64) NOT NULL,
	body TEXT,
	favorite_count INTEGER,
	creation_date TIMESTAMP NOT NULL,
	community_owned_date TIMESTAMP,
	closed_date TIMESTAMP,
	last_edit_date TIMESTAMP,
	last_activity_date TIMESTAMP
);

CREATE TABLE badges (
	id SERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES users(id),
	class SMALLINT NOT NULL,
	name VARCHAR(64) NOT NULL,
	tag_based BOOL NOT NULL,
	date TIMESTAMP NOT NULL
);

CREATE TABLE comments (
	id SERIAL PRIMARY KEY,
	post_id INTEGER NOT NULL REFERENCES posts(id),
	user_id INTEGER REFERENCES users(id),
	score SMALLINT NOT NULL,
	content_license VARCHAR(64) NOT NULL,
	user_display_name VARCHAR(64),
	text TEXT,
	creation_date TIMESTAMP NOT NULL
);


CREATE TABLE post_history (
	id SERIAL PRIMARY KEY,
	post_id INTEGER NOT NULL REFERENCES posts(id),
	user_id INTEGER REFERENCES users(id),
	post_history_type_id SMALLINT NOT NULL,
	user_display_name VARCHAR(64),
	content_license VARCHAR(64),
	revision_guid uuid,
	text TEXT,
	comment TEXT,
	creation_date TIMESTAMP NOT NULL
);

CREATE TABLE post_links (
	id SERIAL PRIMARY KEY,
	related_post_id INTEGER NOT NULL REFERENCES posts(id),
	post_id INTEGER NOT NULL REFERENCES posts(id),
	link_type_id SMALLINT NOT NULL,
	creation_date TIMESTAMP NOT NULL
);

CREATE TABLE tags (
	id SERIAL PRIMARY KEY,
	excerpt_post_id INTEGER REFERENCES posts(id),
	wiki_post_id INTEGER REFERENCES posts(id),
	tag_name VARCHAR(255) NOT NULL,
	count INTEGER DEFAULT 0
);

CREATE TABLE votes (
	id SERIAL PRIMARY KEY,
	user_id INTEGER REFERENCES users(id),
	post_id INTEGER NOT NULL REFERENCES posts(id),
	vote_type_id SMALLINT NOT NULL,
	bounty_amount SMALLINT,
	creation_date TIMESTAMP NOT NULL
);