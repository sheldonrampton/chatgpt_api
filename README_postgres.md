# Postgres
Some commands for manipulating the Postgres database

## Heroku commands
    heroku addons
    heroku config

## Sqlite
Exporting database to CSV:

    sqlite3 shellbot2.db 
    sqlite> .headers on
    sqlite> .mode csv
    sqlite> .output socialdata.csv
    sqlite> SELECT * FROM SocialData;
    sqlite> .quit

## Connecting
### Local
    psql postgres
    psql "postgres://Mamoru:Bk1apFLYt5UvZM@localhost:5432/shellbot"
    psql "postgres://sheldonmrampton:pDjySB9TsoW8c9@localhost:5432/shellbot"

### Heroku
    psql "postgres://username:password@hostname:5432/database_name?sslmode=require"

## Show connection info
    \conninfo

## List databases
    SELECT 1 FROM pg_database WHERE datname = 'shellbot';

## Create database table

shellbot ==> shellbot_knowledge

    CREATE TABLE IF NOT EXISTS SocialData (
        vector_id TEXT PRIMARY KEY,
        platform TEXT,
        title TEXT,
        unix_timestamp INT,
        formatted_datetime TEXT,
        content TEXT,
        url TEXT
    );

    CREATE TABLE IF NOT EXISTS shellbot_knowledge (
        vector_id TEXT PRIMARY KEY,
        platform TEXT,
        title TEXT,
        unix_timestamp INT,
        formatted_datetime TEXT,
        content TEXT,
        url TEXT
    );

social_media.db ==> social_posts

    CREATE TABLE IF NOT EXISTS SocialPosts (
        id INT PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        platform_id TEXT,
        timestamp TEXT,
        content TEXT,
        url TEXT
    );

    CREATE TABLE IF NOT EXISTS social_posts (
        id INT PRIMARY KEY,
        platform TEXT,
        platform_id TEXT,
        timestamp TEXT,
        content TEXT,
        url TEXT
    );

gmail.db ==> gmail_messages

    CREATE TABLE IF NOT EXISTS GmailMessages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        timestamp INT,
        from_email TEXT,
        to_emails TEXT,
        message TEXT
    );

    CREATE TABLE IF NOT EXISTS gmail_messages (
        id INTEGER PRIMARY KEY,
        subject TEXT,
        timestamp INT,
        from_email TEXT,
        to_emails TEXT,
        message TEXT
    );

gem_wiki.db ==> gem_wiki_article_chunks

    CREATE TABLE IF NOT EXISTS ArticleChunks (
        unique_id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        url TEXT
    );

    CREATE TABLE IF NOT EXISTS gem_wiki_article_chunks (
        unique_id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        url TEXT
    );

wikipedia-climate-change.db ==> table wikipedia_climate_article_chunks

    CREATE TABLE IF NOT EXISTS ArticleChunks (
        unique_id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        url TEXT
    );

    CREATE TABLE IF NOT EXISTS wikipedia_climate_article_chunks (
        unique_id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        url TEXT
    );

## Display tables
    \dt

## Show sample data
    SELECT title from socialdata WHERE platform = 'Email' LIMIT 1;
    SELECT title from socialdata WHERE platform = 'Facebook post' LIMIT 1;
    SELECT title from socialdata WHERE platform = 'Facebook comment' LIMIT 1;
    SELECT title from socialdata WHERE platform = 'Tweet' LIMIT 1;

## Load data into table from a CSV
    COPY SocialData(vector_id, platform, title, unix_timestamp, formatted_datetime, content, url) FROM '/Users/sheldonmrampton/Documents/Code/chatgpt_api/socialdata.csv' WITH (FORMAT csv, HEADER);

    COPY social_posts(id, platform, platform_id, timestamp, content, url) FROM '/Users/sheldonmrampton/Documents/Code/chatgpt_api/social_media.csv' WITH (FORMAT csv, HEADER);

    COPY gmail_messages(id, subject, timestamp, from_email, to_emails, message) FROM '/Users/sheldonmrampton/Documents/Code/chatgpt_api/gmail.csv' WITH (FORMAT csv, HEADER);

    COPY gem_wiki_article_chunks(unique_id, title, content, url) FROM '/Users/sheldonmrampton/Documents/Code/chatgpt_api/gem_wiki.csv' WITH (FORMAT csv, HEADER);

    COPY wikipedia_climate_article_chunks(unique_id, title, content, url) FROM '/Users/sheldonmrampton/Documents/Code/chatgpt_api/wikipedia-climate-change.csv' WITH (FORMAT csv, HEADER);

    \copy SocialData(vector_id, platform, title, unix_timestamp, formatted_datetime, content, url) FROM '/Users/sheldonmrampton/Documents/Code/chatgpt_api/socialdata.csv' WITH (FORMAT csv, HEADER);

## Clone a table
    CREATE TABLE new_table_name AS TABLE original_table_name;

## Rename a table
    ALTER TABLE socialdata RENAME TO shellbot_knowledge;

## Make a column a primary key
    ALTER TABLE table_name ADD PRIMARY KEY (column_name);

## Creating, changing user
    CREATE USER Mamoru WITH PASSWORD 'XXXX';
    ALTER USER sheldonmrampton WITH PASSWORD 'XXXXX';
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "Mamoru";
    \du

## Dedupe rows with identical content
    -- Step 1: Add a temporary column to track the original row IDs
    ALTER TABLE your_table_name ADD COLUMN temp_row_id serial PRIMARY KEY;

    -- Step 2: Delete duplicates, keeping only the first occurrence of each content
    DELETE FROM your_table_name
    WHERE temp_row_id NOT IN (
        SELECT MIN(temp_row_id)
        FROM your_table_name
        GROUP BY content
    );

    -- Step 3: Drop the temporary column
    ALTER TABLE your_table_name DROP COLUMN temp_row_id;

## Delete orphan rows from Pinecone
    import pinecone
    import psycopg2

    # Initialize Pinecone
    pinecone.init(api_key='your-pinecone-api-key', environment='your-pinecone-environment')
    index = pinecone.Index('your-index-name')

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname="your_database_name",
        user="your_username",
        password="your_password",
        host="your_host",
        port="your_port"
    )
    cursor = conn.cursor()

    # Get the list of valid IDs from PostgreSQL
    cursor.execute("SELECT id FROM your_table_name")
    valid_ids = set([row[0] for row in cursor.fetchall()])

    # Fetch all IDs from Pinecone
    pinecone_ids = index.fetch_all_ids()

    # Find IDs that are in Pinecone but not in PostgreSQL
    ids_to_delete = [id for id in pinecone_ids if id not in valid_ids]

    # Delete the non-matching vectors from Pinecone
    index.delete(ids=ids_to_delete)

    # Close the database connection
    cursor.close()
    conn.close()


