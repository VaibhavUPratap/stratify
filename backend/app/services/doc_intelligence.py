import os
import re
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class DocumentIntelligenceService:
    def __init__(self):
        # We can configure pytesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
        pass

    def extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.error(f"pdfplumber failed: {e}")
        
        # If no text extracted, try OCR (if it's a scanned PDF/image)
        if not text.strip():
            logger.info("No text extracted via pdfplumber. Trying pytesseract OCR fallback...")
            try:
                # Basic OCR logic fallback
                # Since PyMuPDF is not installed, we assume we might be parsing an image or we try pytesseract on PIL images if we can convert it.
                # If pytesseract is not installed on system, this might raise TesseractNotFoundError
                text = pytesseract.image_to_string(Image.open(file_path))
            except Exception as e:
                logger.warning(f"pytesseract OCR fallback failed (probably tesseract not installed on system): {e}")
        
        return text

    def parse_invoice(self, file_path: str) -> dict:
        """
        Parses Invoices & Bills.
        Extracts: Vendor, Products, GST, Amount, Dates, Invoice Number, Taxes.
        """
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        
        if ext == ".pdf":
            text = self.extract_text_from_pdf(file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            try:
                text = pytesseract.image_to_string(Image.open(file_path))
            except Exception as e:
                logger.error(f"Image OCR failed: {e}")
        
        # Apply standard regex parsers to extract key details
        vendor = self._find_vendor(text)
        invoice_number = self._find_invoice_number(text)
        date = self._find_date(text)
        amount = self._find_amount(text)
        gst = self._find_gst(text)
        products = self._find_products(text)
        
        return {
            "vendor": vendor,
            "invoice_number": invoice_number,
            "date": date,
            "total_amount": amount,
            "gst_amount": gst,
            "products": products,
            "raw_text_snippet": text[:500]
        }

    def parse_gst_report(self, file_path: str) -> dict:
        text = self.extract_text_from_pdf(file_path)
        gstin = re.search(r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b', text)
        total_tax = self._find_gst(text)
        return {
            "gstin": gstin.group(0) if gstin else "Unknown",
            "total_tax_amount": total_tax,
            "raw_text_snippet": text[:500]
        }

    def parse_bank_statement(self, file_path: str) -> dict:
        text = self.extract_text_from_pdf(file_path)
        # Extract transactions using basic regex line matching
        transactions = []
        lines = text.split("\n")
        for line in lines:
            # Match common transaction patterns like: Date Description Amount
            match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{2,4})\s+([\w\s\*]+)\s+([\d\.,]+)', line)
            if match:
                transactions.append({
                    "date": match.group(1),
                    "description": match.group(2).strip(),
                    "amount": float(match.group(3).replace(",", ""))
                })
        return {
            "transactions_count": len(transactions),
            "transactions": transactions[:10], # limit preview
            "raw_text_snippet": text[:500]
        }

    def parse_excel(self, file_path: str) -> dict:
        try:
            df = pd.read_excel(file_path)
            # Basic summary of Excel structure
            summary = {
                "columns": list(df.columns),
                "rows_count": len(df),
                "preview": df.head(5).to_dict(orient="records")
            }
            return summary
        except Exception as e:
            logger.error(f"Excel parsing failed: {e}")
            return {"error": str(e)}

    # Helper regex matchers
    def _find_vendor(self, text: str) -> str:
        # Match common vendor labels or take first line
        match = re.search(r'(?:Vendor|Supplier|Seller|Bill From):\s*(.*)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return lines[0] if lines else "Unknown Vendor"

    def _find_invoice_number(self, text: str) -> str:
        match = re.search(r'(?:Invoice\s*No|Inv\s*#|Invoice\s*Number|Bill\s*No):\s*([\w\-]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "INV-" + str(pd.Timestamp.now().microsecond)

    def _find_date(self, text: str) -> str:
        match = re.search(r'(?:Date|Billing Date|Invoice Date):\s*([\d\w\s,-/]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # Find any general date pattern
        date_pattern = re.search(r'\b\d{2,4}[-/]\d{2}[-/]\d{2,4}\b', text)
        if date_pattern:
            return date_pattern.group(0)
        return pd.Timestamp.now().strftime("%Y-%m-%d")

    def _find_amount(self, text: str) -> float:
        match = re.search(r'(?:Total|Grand Total|Amount Due|Total Due):\s*[\$₹]?\s*([\d\.,]+)', text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except ValueError:
                pass
        return 0.0

    def _find_gst(self, text: str) -> float:
        match = re.search(r'(?:GST|IGST|SGST|CGST|Tax|Taxes):\s*[\$₹]?\s*([\d\.,]+)', text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except ValueError:
                pass
        return 0.0

    def _find_products(self, text: str) -> list:
        # Look for simple lines containing numbers and prices
        products = []
        lines = text.split("\n")
        for line in lines:
            # Pattern matching: Item Description Qty Price Total
            match = re.search(r'([A-Za-z0-9\s\-]{3,})\s+(\d+)\s+([\d\.,]+)\s+([\d\.,]+)', line)
            if match:
                products.append({
                    "name": match.group(1).strip(),
                    "quantity": int(match.group(2)),
                    "price": float(match.group(3).replace(",", "")),
                    "total": float(match.group(4).replace(",", ""))
                })
        return products
