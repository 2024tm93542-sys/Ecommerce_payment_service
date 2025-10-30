#!/usr/bin/env python3
"""
Simple CSV → MySQL loader for product catalog.
"""

import csv
import mysql.connector
import argparse

def connect_db(host, user, password, database):
    """Establish a connection to MySQL."""
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def create_table_if_not_exists(conn):
    """Create the catalogue table if it doesn't exist, using CSV's schema (no AUTO_INCREMENT)."""
    cursor = conn.cursor()
    ddl = """
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        amount DECIMAL(10,2),
        method VARCHAR(255) NOT NULL,
        status BOOLEAN,
        reference VARCHAR(100) UNIQUE,
        created_at TIMESTAMP,
        refunded BOOLEAN NOT NULL DEFAULT 0
    );
    """
    cursor.execute(ddl)
    conn.commit()
    cursor.close()
    print("✅ Ensured table 'payments' exists.")

def load_csv(csv_path, conn):
    """Read the CSV and insert/update rows."""
    cursor = conn.cursor()
    with open(csv_path, newline='') as csvfile:
        # Try to detect delimiter automatically, but assume tab if not comma-separated
        sample = csvfile.read(1024)
        csvfile.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="\t,")
        except Exception:
            # Fallback to comma if sniffing fails on small/irregular samples
            dialect = csv.get_dialect('excel')
        reader = csv.DictReader(csvfile, dialect=dialect)

        for row in reader:

            sql = """
                INSERT INTO payments (payment_id, order_id, amount, method, status, reference, created_at, refunded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    payment_id=VALUES(payment_id),
                    order_id=VALUES(order_id),
                    amount=VALUES(amount),
                    method=VALUES(method),
                    status=VALUES(status),
                    reference=VALUES(reference),
                    created_at=VALUES(created_at),
                    refunded=VALUES(refunded);
            """
            vals = (
                int(row['payment_id']),
                int(row['order_id']),
                float(row['amount']),
                row['method'],
                # Convert status to boolean --> SUCCESS = 1, FAILED = 0
                1 if row['status'].upper() == 'SUCCESS' else 0,
                row['reference'],
                row['created_at'],
                0,  # refunded not present in CSV; set to 0
            )
            cursor.execute(sql, vals)

    conn.commit()
    cursor.close()
    print("✅ CSV data successfully loaded into 'payments' table.")

def main():
    parser = argparse.ArgumentParser(description="Load CSV into MySQL 'payments' table")
    parser.add_argument("--csv", default="eci_payments.csv", help="Path to CSV file")
    parser.add_argument("--host", default="127.0.0.1", help="MySQL host")
    parser.add_argument("--user", default="root", help="MySQL username")
    parser.add_argument("--password", required=True, help="MySQL password")
    parser.add_argument("--db", default="ecommerce", help="Target database name")
    args = parser.parse_args()

    conn = connect_db(args.host, args.user, args.password, args.db)
    create_table_if_not_exists(conn)
    load_csv(args.csv, conn)
    conn.close()

if __name__ == "__main__":
    main()
