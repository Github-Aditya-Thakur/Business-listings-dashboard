from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP, text, UniqueConstraint
from database import Base

class ListingMaster(Base):
    __tablename__ = "listing_master"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    business_name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False, default="")
    city = Column(String(100), nullable=False, default="")      # changed
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    source = Column(String(50), nullable=False, default="")     # changed
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint("business_name", "category", "city", "source", name="uq_listing_dedupe"),
    )
