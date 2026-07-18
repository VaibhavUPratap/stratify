from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..database import get_db
from ..models import models
from ..schemas import schemas

router = APIRouter(prefix="/business", tags=["Business CRUD"])

@router.get("/company", response_model=schemas.CompanySchema)
async def get_company(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Company).limit(1))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.get("/customers", response_model=List[schemas.CustomerSchema])
async def get_customers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Customer).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/suppliers", response_model=List[schemas.SupplierSchema])
async def get_suppliers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Supplier).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/products", response_model=List[schemas.ProductSchema])
async def get_products(skip: int = 0, limit: int = 100, category: str = None, db: AsyncSession = Depends(get_db)):
    query = select(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/inventory", response_model=List[schemas.InventorySchema])
async def get_inventory(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Inventory))
    return result.scalars().all()

@router.get("/sales", response_model=List[schemas.SalesSchema])
async def get_sales(skip: int = 0, limit: int = 100, customer_id: int = None, db: AsyncSession = Depends(get_db)):
    query = select(models.Sales).order_by(models.Sales.date.desc())
    if customer_id:
        query = query.filter(models.Sales.customer_id == customer_id)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/invoices", response_model=List[schemas.InvoiceSchema])
async def get_invoices(skip: int = 0, limit: int = 100, status: str = None, invoice_type: str = None, db: AsyncSession = Depends(get_db)):
    query = select(models.Invoice)
    if status:
        query = query.filter(models.Invoice.status == status)
    if invoice_type:
        query = query.filter(models.Invoice.invoice_type == invoice_type)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/employees", response_model=List[schemas.EmployeeSchema])
async def get_employees(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Employee))
    return result.scalars().all()

@router.get("/events", response_model=List[schemas.BusinessEventSchema])
async def get_events(limit: int = 50, event_type: str = None, db: AsyncSession = Depends(get_db)):
    query = select(models.BusinessEvent).order_by(models.BusinessEvent.timestamp.desc())
    if event_type:
        query = query.filter(models.BusinessEvent.event_type == event_type)
    result = await db.execute(query.limit(limit))
    return result.scalars().all()
