# Work to create new table
from pprint import pprint
import psycopg2

conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="127.0.0.1", port="5432")

conn.autocommit = True
cursor = conn.cursor()


# sql = """CREATE TABLE DETAILS(card_code char(20) NOT NULL,\
# surname char(20),\
# email varchar(30),\
# inv int,\
# amount float,\
# amount_tl int);"""


# cursor.execute(sql)

# with open("./inser_data_to_db/test_import.csv", "r") as f:

#     # Skip the header row.
#     next(f)
#     cursor.copy_from(f, "details", sep=",")


sql3 = """select * from details;"""
cursor.execute(sql3)
for i in cursor.fetchall():
    print(i)

sql4 = "SELECT card_code FROM details GROUP BY card_code HAVING count(*)>1;"
cursor.execute(sql4)

match_list = list()
for i in cursor.fetchall():
    match_list.append(i[0])
# print(f"{match_list=}")

if match_list:
    element_lts = list()
    for elem in match_list:
        sql5 = f"SELECT card_id, card_code, inv, added_time, used_time FROM details WHERE card_code='{elem}';"
        cursor.execute(sql5)
        element_lts.append(cursor.fetchall())
print(element_lts)
for elem in element_lts:
    print(len(elem))
pprint(len(element_lts))

conn.commit()
conn.close()
