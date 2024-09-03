import psycopg2

hostname = "localhost"
database = "blog_platform"
username = "postgres"
pwd = "mahak03"
port_id = 5432
cur = None
conn = None

try:
    print("Connecting to the database...")
    conn = psycopg2.connect(
        host = hostname,
        dbname = database,
        user = username,
        password = pwd,
        port = port_id
    )
    cur = conn.cursor()
    print("Connected successfully.")


    create_users_table = '''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role VARCHAR(20) DEFAULT 'reader' CHECK (role IN ('admin', 'author', 'reader'))
    )
    '''
    cur.execute(create_users_table)     
    print('users table created') 

    create_posts_table = '''
    CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        content TEXT NOT NULL,
        author_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) 
    '''
    cur.execute(create_posts_table)
    print('posts table created') 

    create_comments_table = '''
    CREATE TABLE IF NOT EXISTS comments(
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        post_id INTEGER REFERENCES posts(id),
        user_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )'''  


    cur.execute(create_comments_table)   
    print('comments table created') 

    conn.commit()
   
    
except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()

