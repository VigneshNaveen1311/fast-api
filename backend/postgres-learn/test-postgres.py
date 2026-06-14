import psycopg

conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="playground",
    user="postgres",
    password="123"
)



# cur.execute("select * from users")


# cur.execute("insert into users (name, age) values (%s, %s)", ("Chino", 25))
# cur.execute("delete from users where id > (%s)", (3,))
# conn.commit()



def add_user(name: str, age: int):
    cur = conn.cursor()
    cur.execute("insert into users (name, age) values (%s, %s)", (name, age))
    conn.commit()
    cur.close()

def get_user(id: str):
    cur = conn.cursor()
    cur.execute("select * from users where id = (%s)",
                (id,))
    row = cur.fetchall()
    return row[0]

add_user("lewis", 44)
add_user("Max", 30)

cur = conn.cursor()
cur.execute("select * from users")
rows = cur.fetchall()
for row in rows:
    print(row)

print(get_user(1))

cur.close()
conn.close()