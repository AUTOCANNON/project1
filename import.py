import csv
import psycopg2
import time

def main():

    start = time.time()

    try:
        conn = psycopg2.connect("dbname='d8dlpb05q2libe' user='edtcjsjassoawb' host='ec2-54-197-48-79.compute-1.amazonaws.com' password=' (removed) '")
    except:
        print("Unable to connect to db")

    cur = conn.cursor()

    with open('books.csv',newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',',quotechar='|')
        
        # Iterate over each row, inserting variables into respective db columns.     
        for row in spamreader:

            isbn = row[0]
            title = row[1]
            author = row[2]
            year = row[3]

            query = "INSERT INTO books (isbn, title, author, year) VALUES (%s,%s,%s,%s)"
            data = (isbn, title, author, year)

            cur.execute(query,data)
            conn.commit()      

    end = time.time()
    print(f"Completed in {end - start} seconds")

main()