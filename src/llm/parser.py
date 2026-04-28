from pydantic import BaseModel
from typing import Optional, List, Any

# ============================================================
# Pydantic-Modelle für ALDI-Quittung (Pydantic v2)
# ============================================================

def clean_strip(raw_string):
    clean_string = raw_string.strip()
    if clean_string.startswith("```json"):
        clean_string = clean_string[7:] # Schneidet die ersten 7 Zeichen ab
    if clean_string.endswith("```"):
        clean_string = clean_string[:-3] # Schneidet die letzten 3 Zeichen ab
    
    clean_string = clean_string.strip()
    return clean_string

class Merchant(BaseModel):
    name: str
    address: str
    tax_id: Optional[str] = None
    phone: Optional[str] = None


class Transaction(BaseModel):
    date: str          # oder: from datetime import date → date
    time: str          # oder: from datetime import time → time
    currency: str
    total_amount: float
    payment_method: str
    card_last_four: Optional[str] = None
    receipt_number: Optional[str] = None
   


class Item(BaseModel):
    line_number: int
    sku: str
    name: str
    quantity: float
    unit: Optional[str] = None
    unit_price: float
    total_price: float
    tax_category: str
    discount: Optional[float] = None
    category:str


class Metadata(BaseModel):
    ocr_confidence: str
    image_filename: Optional[str] = None


class Receipt(BaseModel):
    merchant: Merchant
    transaction: Transaction
    items: List[Item]
    taxes: List[Any] = []   # leer in deinem Beispiel; bei Bedarf eigenes Tax-Modell
    metadata: Metadata