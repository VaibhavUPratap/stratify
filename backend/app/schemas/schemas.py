from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    industry: Optional[str] = None
    tax_id: Optional[str] = None
    registration_number: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    cash_balance: float = 0.0
    annual_revenue_target: float = 0.0
    founded_year: Optional[int] = None

class CompanyCreate(CompanyBase):
    pass

class CompanySchema(CompanyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class CustomerBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    company_name: Optional[str] = None
    credit_score: int = 700
    credit_limit: float = 10000.0
    payment_terms_days: int = 30
    clv: float = 0.0
    is_active: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerSchema(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: str = "unit"
    price: float
    cost: float
    stock_level: int = 0
    reorder_point: int = 10
    reorder_quantity: int = 50
    supplier_id: Optional[int] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductSchema(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class SupplierBase(BaseModel):
    name: str
    email: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms_days: int = 30
    reliability_score: float = 1.0
    average_lead_days: int = 7
    total_orders_placed: int = 0
    total_delayed_orders: int = 0

class SupplierCreate(SupplierBase):
    pass

class SupplierSchema(SupplierBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class InventoryBase(BaseModel):
    product_id: int
    current_stock: int = 0
    reserved_stock: int = 0
    warehouse_location: Optional[str] = None

class InventoryCreate(InventoryBase):
    pass

class InventorySchema(InventoryBase):
    id: int
    last_updated: datetime
    model_config = ConfigDict(from_attributes=True)

class SalesBase(BaseModel):
    product_id: int
    customer_id: int
    quantity: int
    unit_price: float
    discount_pct: float = 0.0
    total_price: float
    channel: str = "direct"

class SalesCreate(SalesBase):
    pass

class SalesSchema(SalesBase):
    id: int
    date: datetime
    model_config = ConfigDict(from_attributes=True)

class InvoiceBase(BaseModel):
    invoice_number: str
    invoice_type: str = "AR"
    due_date: datetime
    total_amount: float
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    paid_amount: float = 0.0
    status: str = "UNPAID"
    notes: Optional[str] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceSchema(InvoiceBase):
    id: int
    issue_date: datetime
    model_config = ConfigDict(from_attributes=True)

class EmployeeBase(BaseModel):
    name: str
    email: str
    role: str
    department: str
    salary: float
    employment_type: str = "full_time"
    is_active: bool = True

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeSchema(EmployeeBase):
    id: int
    hire_date: datetime
    model_config = ConfigDict(from_attributes=True)

class BusinessEventBase(BaseModel):
    event_type: str
    description: str
    severity: str = "INFO"
    source: str = "user"
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    metadata_json: Optional[str] = None

class BusinessEventCreate(BusinessEventBase):
    pass

class BusinessEventSchema(BusinessEventBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class RecommendationHistoryBase(BaseModel):
    agent_name: str
    recommendation_text: str
    confidence_score: float = 0.0
    risk_level: Optional[str] = None
    supporting_evidence: Optional[str] = None

class RecommendationHistoryCreate(RecommendationHistoryBase):
    pass

class RecommendationHistorySchema(RecommendationHistoryBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class DecisionHistoryBase(BaseModel):
    recommendation_id: int
    action_taken: str
    business_outcome: Optional[str] = None

class DecisionHistoryCreate(DecisionHistoryBase):
    pass

class DecisionHistorySchema(DecisionHistoryBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
