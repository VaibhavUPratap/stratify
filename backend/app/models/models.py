from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String)
    tax_id = Column(String)
    registration_number = Column(String)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    cash_balance = Column(Float, default=0.0)
    annual_revenue_target = Column(Float, default=0.0)
    founded_year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    address = Column(String)
    company_name = Column(String)
    credit_score = Column(Integer, default=700)
    credit_limit = Column(Float, default=10000.0)
    payment_terms_days = Column(Integer, default=30)
    clv = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    contact = Column(String)
    phone = Column(String)
    address = Column(String)
    payment_terms_days = Column(Integer, default=30)
    reliability_score = Column(Float, default=1.0)
    average_lead_days = Column(Integer, default=7)
    total_orders_placed = Column(Integer, default=0)
    total_delayed_orders = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    unit_of_measure = Column(String, default="unit")
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    stock_level = Column(Integer, default=0)
    reorder_point = Column(Integer, default=10)
    reorder_quantity = Column(Integer, default=50)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    inventory = relationship("Inventory", back_populates="product", uselist=False)

class Inventory(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), unique=True)
    current_stock = Column(Integer, default=0)
    reserved_stock = Column(Integer, default=0)
    warehouse_location = Column(String)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="inventory")

class Sales(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_pct = Column(Float, default=0.0)
    total_price = Column(Float, nullable=False)
    channel = Column(String, default="direct")
    date = Column(DateTime(timezone=True), server_default=func.now())

class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    invoice_type = Column(String, default="AR") # AR or AP
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=False)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    status = Column(String, default="UNPAID") # UNPAID, PARTIAL, PAID, OVERDUE
    notes = Column(String)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    department = Column(String, nullable=False)
    salary = Column(Float, nullable=False)
    employment_type = Column(String, default="full_time")
    is_active = Column(Boolean, default=True)
    hire_date = Column(DateTime(timezone=True), server_default=func.now())

class BusinessEvent(Base):
    __tablename__ = 'business_events'

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    severity = Column(String, default="INFO")
    source = Column(String, default="user")
    entity_type = Column(String)
    entity_id = Column(Integer)
    metadata_json = Column(String) # Simple string storage for JSON for now
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class RecommendationHistory(Base):
    __tablename__ = 'recommendation_history'

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, nullable=False)
    recommendation_text = Column(String, nullable=False)
    confidence_score = Column(Float, default=0.0)
    risk_level = Column(String)
    supporting_evidence = Column(String)
    roi = Column(Float, default=0.0)
    business_impact = Column(String)
    affected_departments = Column(String) # JSON or comma-separated string
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED, MODIFIED
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class DecisionHistory(Base):
    __tablename__ = 'decision_history'

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey('recommendation_history.id'))
    action_taken = Column(String, nullable=False) # Maps to user_action in docs
    business_outcome = Column(String)
    modification_notes = Column(String)
    outcome_revenue_impact = Column(Float, default=0.0)
    feedback = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
