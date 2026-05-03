import sqlite3
import pandas as pd
def save_data(pydantic_object, cursor, conn=None, commit=True):
    """
    Persists receipt data from a Pydantic object into a relational database.

    This function performs de-normalization by embedding transaction and metadata 
    directly into the items table to satisfy a two-table schema requirement. It 
    implements idempotent logic for merchants (find or create) and utilizes 
    'INSERT OR IGNORE' for items to prevent duplicate entries from the same receipt.

    Args:
        pydantic_object (Receipt): The validated Pydantic object containing merchant, 
            transaction, item, and metadata nested objects.
        cursor (sqlite3.Cursor): The database cursor used to execute SQL commands.
        conn (sqlite3.Connection, optional): The database connection object. 
            Required if 'commit' is set to True. Defaults to None.
        commit (bool): Whether to finalize the transaction immediately. Defaults to True.

    Returns:
        int: The unique ID of the merchant associated with this receipt.

    Raises:
        sqlite3.Error: If any database integrity or operational errors occur.
        AttributeError: If the pydantic_object structure is missing expected attributes.
    """
    
    # 1. Merchant Logic: Handle unique merchant identification
    merchant = pydantic_object.merchant
    try:
        cursor.execute("""
            INSERT INTO merchant (name, address, tax_id, phone)
            VALUES (?, ?, ?, ?)
        """, (merchant.name, merchant.address, merchant.tax_id, merchant.phone))
        merchant_id = cursor.lastrowid
        print(f"[Log] New merchant registered: {merchant.name}")
    except sqlite3.IntegrityError:
        # Fallback: Retrieve existing ID if merchant (name + address) already exists
        cursor.execute(
            "SELECT id FROM merchant WHERE name = ? AND address = ?", 
            (merchant.name, merchant.address)
        )
        merchant_id = cursor.fetchone()[0]
        print(f"[Log] Using existing merchant: {merchant.name} (ID: {merchant_id})")

    # 2. Extract nested data for denormalized item storage
    trans = pydantic_object.transaction
    meta  = pydantic_object.metadata
    items = pydantic_object.items
    
    # 3. Batch Insert Items: Map transaction headers to every row
    for item in items:
        cursor.execute("""
            INSERT OR IGNORE INTO items (
                merchant_id, 
                line_number, sku, name, quantity, unit, unit_price, total_price, 
                tax_category, discount, category, transaction_date, 
                transaction_time, currency, total_amount, payment_method, 
                card_last_four, receipt_number, ocr_confidence, image_filename
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            merchant_id,
            item.line_number, item.sku, item.name, item.quantity, item.unit, 
            item.unit_price, item.total_price, item.tax_category, item.discount, 
            item.category, trans.date, trans.time, trans.currency, 
            trans.total_amount, trans.payment_method, trans.card_last_four, 
            trans.receipt_number, meta.ocr_confidence, meta.source
        ))
    
    # 4. Transaction Management
    if commit and conn:
        conn.commit()
    
    print(f"[Log] Successfully processed {len(items)} items for Merchant ID {merchant_id}.")
    return merchant_id


def read_data(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    df_items = pd.read_sql_query("SELECT * FROM items", conn).drop_duplicates()
    df_merchant = pd.read_sql_query("SELECT * FROM merchant", conn).drop_duplicates()
    df_merchant = df_merchant.rename(columns = {'name':'merchant'})

    df = pd.merge(df_items,df_merchant,how='left',left_on='merchant_id',right_on='id')

    conn.close()
    return df