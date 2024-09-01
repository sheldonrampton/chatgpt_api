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
    CREATE TABLE IF NOT EXISTS SocialData (
        vector_id TEXT PRIMARY KEY,
        platform TEXT,
        title TEXT,
        unix_timestamp INT,
        formatted_datetime TEXT,
        content TEXT,
        url TEXT
    );

## Display tables
    \dt

## Load data into table from a CSV
    COPY SocialData(vector_id, platform, title, unix_timestamp, formatted_datetime, content, url) FROM '/Users/sheldonmrampton/Documents/Code/chatgpt_api/socialdata.csv' WITH (FORMAT csv, HEADER);

    \copy SocialData(vector_id, platform, title, unix_timestamp, formatted_datetime, content, url) FROM '/Users/sheldonmrampton/Documents/Code/chatgpt_api/socialdata.csv' WITH (FORMAT csv, HEADER);

## Clone a table
    CREATE TABLE new_table_name AS TABLE original_table_name;

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


