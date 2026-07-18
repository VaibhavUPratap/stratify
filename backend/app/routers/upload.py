from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import os
import shutil
import logging

from ..database import get_db
from ..services.doc_intelligence import DocumentIntelligenceService
from ..services.business_memory import BusinessMemoryService
from ..config import settings

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
    memory: BusinessMemoryService = Depends(get_business_memory_service)
):
    file_path = save_file_locally(file)
    parsed_data = parser.parse_invoice(file_path)
    
    await memory.store_event(
        event_type="document_ingestion",
        description=f"Ingested invoice/bill '{file.filename}' from vendor '{parsed_data.get('vendor')}' totaling ${parsed_data.get('total_amount'):,.2f}",
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
    memory: BusinessMemoryService = Depends(get_business_memory_service)
):
    file_path = save_file_locally(file)
    parsed_data = parser.parse_bank_statement(file_path)
    
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
    memory: BusinessMemoryService = Depends(get_business_memory_service)
):
    file_path = save_file_locally(file)
    parsed_data = parser.parse_excel(file_path)
    
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
