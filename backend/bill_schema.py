from pydantic import BaseModel
from typing import List, Optional


class LineItem(BaseModel):
    item: str
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None


class BillData(BaseModel):
    provider_name: Optional[str] = None
    provider_address: Optional[str] = None

    bill_number: Optional[str] = None
    bill_date: Optional[str] = None
    bill_time: Optional[str] = None

    patient_name: Optional[str] = None

    line_items: List[LineItem] = []

    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None

    insurance_payment: Optional[float] = None
    patient_responsibility: Optional[float] = None

    possible_duplicates: List[str] = []
    suspicious_charges: List[str] = []
    unreadable_information: List[str] = []