import sqlite3
def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            tax_id TEXT,
            phone TEXT,
            UNIQUE(name, address)
        )
    """
                  )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant_id INTEGER,
            line_number INTEGER, sku TEXT, name TEXT, quantity REAL, unit TEXT, 
            unit_price REAL, total_price REAL, tax_category TEXT, discount REAL, category TEXT,
            transaction_date TEXT, transaction_time TEXT, currency TEXT, total_amount REAL, 
            payment_method TEXT, card_last_four TEXT, receipt_number TEXT,
            ocr_confidence TEXT, image_filename TEXT,
            FOREIGN KEY(merchant_id) REFERENCES merchant(id)

            UNIQUE(merchant_id, receipt_number, transaction_date, line_number)
        )
    """
              )

    return conn,cursor
    