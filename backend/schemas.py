from pydantic import BaseModel
from typing import Optional, List

class ListingIn(BaseModel):
    business_name: str
    category: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None

class BulkInsertRequest(BaseModel):
    listings: List[ListingIn]

class CountByName(BaseModel):
    name: str
    count: int
