from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os
import shutil
import logging
import datetime
import pandas as pd

from ..database import get_db
from ..services.doc_intelligence import DocumentIntelligenceService
from ..services.business_memory import BusinessMemoryService
from ..config import settings
from ..models.models import Customer, Supplier, Product, Inventory, Invoice, Sales, Company, BusinessEvent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["Upload"])

# DI factories
def get_doc_intelligence_service() -> DocumentIntelligenceService:
    return DocumentIntelligenceService()

def get_business_memory_service(db: AsyncSession = Depends(get_db)) -> BusinessMemoryService:
    return BusinessMemoryService(db)

def save_file_locally(file: UploadFile) -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path

@router.post("/invoice")
async def upload_invoice(
    file: UploadFile = File(...), 
    parser: DocumentIntelligenceService = Depends(get_doc_intelligence_service),
    memory: BusinessMemoryService = Depends(get_business_memory_service),
    db: AsyncSession = Depends(get_db)
):
    file_path = save_file_locally(file)
    parsed_data = parser.parse_invoice(file_path)
    
    # State Synchronization & Reconciliation
    vendor = parsed_data.get("vendor", "Unknown Vendor")
    invoice_number = parsed_data.get("invoice_number", "")
    date_str = parsed_data.get("date", "")
    total_amount = parsed_data.get("total_amount", 0.0)
    gst_amount = parsed_data.get("gst_amount", 0.0)
    
    # Try to find corresponding Customer or Supplier
    supp_q = select(Supplier).filter(Supplier.name.ilike(f"%{vendor}%"))
    supp_res = await db.execute(supp_q)
    supplier = supp_res.scalar_one_or_none()
    
    cust_q = select(Customer).filter(Customer.name.ilike(f"%{vendor}%"))
    cust_res = await db.execute(cust_q)
    customer = cust_res.scalar_one_or_none()
    
    invoice_type = "AP" if supplier else "AR"
    supplier_id = supplier.id if supplier else None
    customer_id = customer.id if customer else None
    
    if not supplier_id and not customer_id:
        # Default to creating a new supplier to associate with
        new_supplier = Supplier(
            name=vendor,
            email=f"info@{vendor.lower().replace(' ', '').replace('.', '')}.com",
            payment_terms_days=30,
            reliability_score=1.0,
            average_lead_days=7
        )
        db.add(new_supplier)
        await db.flush()
        supplier_id = new_supplier.id
        invoice_type = "AP"
        
    # Check if invoice already exists
    inv_q = select(Invoice).filter(Invoice.invoice_number == invoice_number)
    inv_res = await db.execute(inv_q)
    existing_invoice = inv_res.scalar_one_or_none()
    
    try:
        issue_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        issue_dt = datetime.datetime.now()
    due_dt = issue_dt + datetime.timedelta(days=30)
    
    if existing_invoice:
        existing_invoice.total_amount = total_amount
        existing_invoice.tax_amount = gst_amount
        existing_invoice.due_date = due_dt
        existing_invoice.supplier_id = supplier_id
        existing_invoice.customer_id = customer_id
        existing_invoice.invoice_type = invoice_type
    else:
        new_invoice = Invoice(
            invoice_number=invoice_number,
            invoice_type=invoice_type,
            issue_date=issue_dt,
            due_date=due_dt,
            total_amount=total_amount,
            tax_amount=gst_amount,
            paid_amount=0.0,
            status="UNPAID",
            customer_id=customer_id,
            supplier_id=supplier_id
        )
        db.add(new_invoice)
        
    await db.commit()
    
    await memory.store_event(
        event_type="document_ingestion",
        description=f"Ingested invoice/bill '{file.filename}' from vendor '{vendor}' totaling ${total_amount:,.2f}",
        severity="INFO",
        source="system",
        entity_type="Invoice",
        metadata_dict=parsed_data
    )
    
    return {
        "message": "Invoice uploaded and processed successfully.",
        "filename": file.filename,
        "parsed_metadata": parsed_data
    }

@router.post("/gst")
async def upload_gst(
    file: UploadFile = File(...), 
    parser: DocumentIntelligenceService = Depends(get_doc_intelligence_service),
    memory: BusinessMemoryService = Depends(get_business_memory_service)
):
    file_path = save_file_locally(file)
    parsed_data = parser.parse_gst_report(file_path)
    
    await memory.store_event(
        event_type="gst_report_ingestion",
        description=f"Ingested GST report '{file.filename}' for GSTIN: {parsed_data.get('gstin')}",
        severity="INFO",
        source="system",
        metadata_dict=parsed_data
    )
    
    return {
        "message": "GST document processed successfully.",
        "filename": file.filename,
        "parsed_metadata": parsed_data
    }

@router.post("/bank")
async def upload_bank(
    file: UploadFile = File(...), 
    parser: DocumentIntelligenceService = Depends(get_doc_intelligence_service),
    memory: BusinessMemoryService = Depends(get_business_memory_service),
    db: AsyncSession = Depends(get_db)
):
    file_path = save_file_locally(file)
    parsed_data = parser.parse_bank_statement(file_path)
    
    # State Synchronization & Reconciliation
    transactions = parsed_data.get("transactions", [])
    ending_balance = parsed_data.get("ending_balance")
    
    # Get company profile
    comp_q = select(Company).limit(1)
    comp_res = await db.execute(comp_q)
    company = comp_res.scalar_one_or_none()
    
    for tx in transactions:
        tx_desc = tx.get("description", "")
        tx_type = tx.get("type", "")
        tx_amount = tx.get("amount", 0.0)
        
        if tx_type == "Credit":
            inv_q = select(Invoice).filter(Invoice.invoice_type == "AR", Invoice.status != "PAID")
            inv_res = await db.execute(inv_q)
            unpaid_invoices = inv_res.scalars().all()
            for inv in unpaid_invoices:
                if str(inv.invoice_number).lower() in tx_desc.lower() or abs(inv.total_amount - tx_amount) < 0.01:
                    inv.status = "PAID"
                    inv.paid_amount = inv.total_amount
                    break
        elif tx_type == "Debit":
            inv_q = select(Invoice).filter(Invoice.invoice_type == "AP", Invoice.status != "PAID")
            inv_res = await db.execute(inv_q)
            unpaid_invoices = inv_res.scalars().all()
            for inv in unpaid_invoices:
                if str(inv.invoice_number).lower() in tx_desc.lower() or abs(inv.total_amount - tx_amount) < 0.01:
                    inv.status = "PAID"
                    inv.paid_amount = inv.total_amount
                    break
                    
    if ending_balance is not None and company:
        company.cash_balance = ending_balance
        
    await db.commit()
    
    await memory.store_event(
        event_type="bank_statement_ingestion",
        description=f"Ingested bank statement '{file.filename}' containing {parsed_data.get('transactions_count')} transactions.",
        severity="INFO",
        source="system",
        metadata_dict=parsed_data
    )
    
    return {
        "message": "Bank statement processed successfully.",
        "filename": file.filename,
        "parsed_metadata": parsed_data
    }

@router.post("/excel")
async def upload_excel(
    file: UploadFile = File(...), 
    parser: DocumentIntelligenceService = Depends(get_doc_intelligence_service),
    memory: BusinessMemoryService = Depends(get_business_memory_service),
    db: AsyncSession = Depends(get_db)
):
    file_path = save_file_locally(file)
    parsed_data = parser.parse_excel(file_path)
    
    # State Synchronization & Reconciliation
    try:
        df = pd.read_excel(file_path)
        for idx, row in df.iterrows():
            prod_name = str(row.get('Product', ''))
            sku = str(row.get('SKU', ''))
            stock = int(row.get('Stock', 0))
            reorder_level = int(row.get('Reorder Level', 10))
            cost = float(row.get('Cost', 0.0))
            price = float(row.get('Selling Price', 0.0))
            
            if not sku:
                continue
                
            prod_q = select(Product).filter(Product.sku == sku)
            prod_res = await db.execute(prod_q)
            product = prod_res.scalar_one_or_none()
            
            if product:
                product.name = prod_name
                product.price = price
                product.cost = cost
                product.stock_level = stock
                product.reorder_point = reorder_level
                
                inv_q = select(Inventory).filter(Inventory.product_id == product.id)
                inv_res = await db.execute(inv_q)
                inventory = inv_res.scalar_one_or_none()
                if inventory:
                    inventory.current_stock = stock
                else:
                    inventory = Inventory(product_id=product.id, current_stock=stock)
                    db.add(inventory)
            else:
                new_product = Product(
                    sku=sku,
                    name=prod_name,
                    price=price,
                    cost=cost,
                    stock_level=stock,
                    reorder_point=reorder_level,
                    reorder_quantity=stock * 2 if stock > 0 else 50,
                    is_active=True
                )
                db.add(new_product)
                await db.flush()
                
                new_inventory = Inventory(
                    product_id=new_product.id,
                    current_stock=stock,
                    reserved_stock=0
                )
                db.add(new_inventory)
        await db.commit()
    except Exception as e:
        logger.error(f"Error synchronizing inventory Excel: {e}")
        
    await memory.store_event(
        event_type="excel_sheet_ingestion",
        description=f"Ingested Excel document '{file.filename}' containing {parsed_data.get('rows_count', 0)} rows.",
        severity="INFO",
        source="system",
        metadata_dict=parsed_data
    )
    
    return {
        "message": "Excel file processed successfully.",
        "filename": file.filename,
        "parsed_metadata": parsed_data
    }

@router.post("/supplier_notice")
async def upload_supplier_notice(
    file: UploadFile = File(...),
    parser: DocumentIntelligenceService = Depends(get_doc_intelligence_service),
    memory: BusinessMemoryService = Depends(get_business_memory_service),
    db: AsyncSession = Depends(get_db)
):
    file_path = save_file_locally(file)
    parsed_data = parser.parse_supplier_notice(file_path)
    
    supplier_name = parsed_data.get("supplier_name", "")
    markup_pct = parsed_data.get("markup_pct", 0.0)
    
    if supplier_name and markup_pct > 0:
        supp_q = select(Supplier).filter(Supplier.name.ilike(f"%{supplier_name}%"))
        supp_res = await db.execute(supp_q)
        supplier = supp_res.scalar_one_or_none()
        
        if supplier:
            prod_q = select(Product).filter(Product.supplier_id == supplier.id)
            prod_res = await db.execute(prod_q)
            products = prod_res.scalars().all()
            for p in products:
                p.cost = p.cost * (1 + markup_pct / 100.0)
                
            await db.commit()
            
    await memory.store_event(
        event_type="supplier_notice_ingestion",
        description=f"Ingested price increase notice '{file.filename}' from supplier '{supplier_name}' proposing a {markup_pct}% markup.",
        severity="INFO",
        source="system",
        metadata_dict=parsed_data
    )
    
    return {
        "message": "Supplier notice processed and product costs updated successfully.",
        "filename": file.filename,
        "parsed_metadata": parsed_data
    }

@router.post("/purchase_order")
async def upload_purchase_order(
    file: UploadFile = File(...),
    parser: DocumentIntelligenceService = Depends(get_doc_intelligence_service),
    memory: BusinessMemoryService = Depends(get_business_memory_service),
    db: AsyncSession = Depends(get_db)
):
    file_path = save_file_locally(file)
    parsed_data = parser.parse_purchase_order(file_path)
    
    customer_name = parsed_data.get("customer_name", "")
    po_number = parsed_data.get("po_number", "")
    products_list = parsed_data.get("products", [])
    
    if customer_name:
        cust_q = select(Customer).filter(Customer.name.ilike(f"%{customer_name}%"))
        cust_res = await db.execute(cust_q)
        customer = cust_res.scalar_one_or_none()
        
        if not customer:
            customer = Customer(
                name=customer_name,
                email=f"info@{customer_name.lower().replace(' ', '').replace('.', '')}.com",
                credit_score=700,
                credit_limit=10000.0,
                is_active=True
            )
            db.add(customer)
            await db.flush()
            
        for item in products_list:
            prod_name = item.get("name")
            qty = item.get("quantity", 0)
            price = item.get("price", 0.0)
            total = item.get("total", 0.0)
            
            prod_q = select(Product).filter(Product.name.ilike(f"%{prod_name}%"))
            prod_res = await db.execute(prod_q)
            product = prod_res.scalar_one_or_none()
            
            if product:
                sale = Sales(
                    product_id=product.id,
                    customer_id=customer.id,
                    quantity=qty,
                    unit_price=price,
                    total_price=total
                )
                db.add(sale)
                
                product.stock_level = max(0, product.stock_level - qty)
                inv_q = select(Inventory).filter(Inventory.product_id == product.id)
                inv_res = await db.execute(inv_q)
                inventory = inv_res.scalar_one_or_none()
                if inventory:
                    inventory.current_stock = max(0, inventory.current_stock - qty)
                    
        await db.commit()
        
    await memory.store_event(
        event_type="purchase_order_ingestion",
        description=f"Ingested purchase order '{file.filename}' from customer '{customer_name}' totaling ${parsed_data.get('total_amount'):,.2f}",
        severity="INFO",
        source="system",
        metadata_dict=parsed_data
    )
    
    return {
        "message": "Purchase order processed and sales logged successfully.",
        "filename": file.filename,
        "parsed_metadata": parsed_data
    }
