from pydantic import BaseModel
from typing import Optional, List, Any


def clean_strip(raw_string):
    clean_string = raw_string.strip()
    if clean_string.startswith("```json"):
        clean_string = clean_string[7:] # Schneidet die ersten 7 Zeichen ab
    if clean_string.endswith("```"):
        clean_string = clean_string[:-3] # Schneidet die letzten 3 Zeichen ab
    
    clean_string = clean_string.strip()
    return clean_string

class Merchant(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    phone: Optional[str] = None


class Transaction(BaseModel):
    date: Optional[str] = None          # oder: from datetime import date → date
    time: Optional[str] = None          # oder: from datetime import time → time
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = None
    card_last_four: Optional[str] = None
    receipt_number: Optional[str] = None
   

class Item(BaseModel):
    line_number: Optional[int] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    tax_category: Optional[str] = None
    discount: Optional[float] = None
    category:Optional[str] = None


class Metadata(BaseModel):
    ocr_confidence: Optional[str] = None
    image_filename: Optional[str] = None
    source: Optional[str] = None
    
class Receipt(BaseModel):
    merchant: Merchant
    transaction: Transaction
    items: List[Item]
    taxes: List[Any] = []   # leer in deinem Beispiel; bei Bedarf eigenes Tax-Modell
    metadata: Metadata