import psycopg

conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="playground",
    user="postgres",
    password="123"
)

cur = conn.cursor()

# cur.execute("create table dogs (id serial primary key, name text not null, breed text not null, age int)")



cur.executemany("insert into dogs (name, breed, age) values (%s, %s, %s)",
            [("Cappuccino", "dobermann", 1),
            ("Cashew", "Labrador", 0)])

conn.commit()

cur.execute("select * from dogs")
rows = cur.fetchall()

for row in rows:
    print(row)

cur.close()
conn.close()