import os
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import tempfile
import subprocess

import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import pytesseract
from PIL import Image
import pdf2image

from app.config import settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDF processing utility with multiple extraction methods and OCR fallback"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def extract_text_pypdf2(self, file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Extract text using PyPDF2"""
        try:
            text_content = ""
            page_info = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        text_content += f"\n--- Page {page_num} ---\n{page_text}\n"
                        
                        page_info.append({
                            "page_number": page_num,
                            "text_length": len(page_text),
                            "extraction_method": "pypdf2"
                        })
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num} with PyPDF2: {e}")
                        page_info.append({
                            "page_number": page_num,
                            "text_length": 0,
                            "extraction_method": "pypdf2_failed",
                            "error": str(e)
                        })
            
            return text_content, page_info
            
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            raise
    
    def extract_text_pdfminer(self, file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Extract text using pdfminer.six"""
        try:
            # Simple extraction
            text_content = pdfminer_extract_text(file_path)
            
            # Get page count for metadata
            page_info = []
            with open(file_path, 'rb') as file:
                pages = list(PDFPage.get_pages(file))
                for i, page in enumerate(pages, 1):
                    page_info.append({
                        "page_number": i,
                        "text_length": len(text_content) // len(pages),  # Approximate
                        "extraction_method": "pdfminer"
                    })
            
            return text_content, page_info
            
        except Exception as e:
            logger.error(f"PDFMiner extraction failed: {e}")
            raise
    
    def extract_text_ocr(self, file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Extract text using OCR (Tesseract) as fallback"""
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(file_path)
            
            text_content = ""
            page_info = []
            
            for page_num, image in enumerate(images, 1):
                try:
                    # Save image temporarily
                    temp_image_path = os.path.join(self.temp_dir, f"page_{page_num}.png")
                    image.save(temp_image_path, "PNG")
                    
                    # Extract text using Tesseract
                    page_text = pytesseract.image_to_string(image, lang='eng')
                    text_content += f"\n--- Page {page_num} (OCR) ---\n{page_text}\n"
                    
                    page_info.append({
                        "page_number": page_num,
                        "text_length": len(page_text),
                        "extraction_method": "ocr_tesseract",
                        "confidence": "medium"  # OCR confidence is typically lower
                    })
                    
                    # Clean up temp image
                    os.remove(temp_image_path)
                    
                except Exception as e:
                    logger.warning(f"OCR failed for page {page_num}: {e}")
                    page_info.append({
                        "page_number": page_num,
                        "text_length": 0,
                        "extraction_method": "ocr_failed",
                        "error": str(e)
                    })
            
            return text_content, page_info
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise
    
    def extract_text(self, file_path: str, methods: List[str] = None) -> Dict[str, Any]:
        """
        Extract text from PDF using multiple methods with fallback
        
        Args:
            file_path: Path to PDF file
            methods: List of extraction methods to try ['pypdf2', 'pdfminer', 'ocr']
        
        Returns:
            Dict containing extracted text, metadata, and extraction info
        """
        if methods is None:
            methods = ['pypdf2', 'pdfminer', 'ocr']
        
        extraction_results = {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "checksum": self.calculate_checksum(file_path),
            "text_content": "",
            "page_info": [],
            "extraction_method": None,
            "success": False,
            "errors": []
        }
        
        # Try each extraction method in order
        for method in methods:
            try:
                logger.info(f"Attempting text extraction with method: {method}")
                
                if method == 'pypdf2':
                    text_content, page_info = self.extract_text_pypdf2(file_path)
                elif method == 'pdfminer':
                    text_content, page_info = self.extract_text_pdfminer(file_path)
                elif method == 'ocr':
                    text_content, page_info = self.extract_text_ocr(file_path)
                else:
                    logger.warning(f"Unknown extraction method: {method}")
                    continue
                
                # Check if extraction was successful (has meaningful content)
                if text_content and len(text_content.strip()) > 100:
                    extraction_results.update({
                        "text_content": text_content,
                        "page_info": page_info,
                        "extraction_method": method,
                        "success": True
                    })
                    logger.info(f"Successfully extracted text using {method}")
                    break
                else:
                    logger.warning(f"Method {method} produced insufficient content")
                    
            except Exception as e:
                error_msg = f"Method {method} failed: {str(e)}"
                logger.error(error_msg)
                extraction_results["errors"].append(error_msg)
                continue
        
        if not extraction_results["success"]:
            logger.error("All extraction methods failed")
            extraction_results["errors"].append("All extraction methods failed")
        
        return extraction_results
    
    def chunk_text(self, text: str, chunk_size: int = 1500, overlap: int = 200) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks for processing
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
        
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or len(text.strip()) < chunk_size:
            return [{
                "chunk_id": 0,
                "text": text,
                "start_pos": 0,
                "end_pos": len(text),
                "length": len(text)
            }]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                sentence_endings = ['. ', '! ', '? ', '\n\n']
                for i in range(end - 200, end):
                    if i > start and any(text[i:i+2] == ending for ending in sentence_endings):
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "start_pos": start,
                    "end_pos": end,
                    "length": len(chunk_text)
                })
                chunk_id += 1
            
            # Move start position with overlap
            start = max(start + chunk_size - overlap, end)
        
        logger.info(f"Created {len(chunks)} chunks from text of length {len(text)}")
        return chunks
    
    def save_file(self, file_content: bytes, organization_id: int, year: int, filename: str) -> str:
        """
        Save uploaded file to organized directory structure
        
        Args:
            file_content: File content as bytes
            organization_id: ID of the organization
            year: Report year
            filename: Original filename
        
        Returns:
            Path to saved file
        """
        # Create directory structure: /data/reports/{org_id}/{year}/
        org_dir = Path(settings.data_dir) / "reports" / str(organization_id) / str(year)
        org_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate safe filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        file_path = org_dir / safe_filename
        
        # Handle duplicate filenames
        counter = 1
        original_path = file_path
        while file_path.exists():
            name_parts = original_path.stem, counter, original_path.suffix
            file_path = original_path.parent / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            counter += 1
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Saved file to {file_path}")
        return str(file_path)
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")


def extract_pdf_text(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to extract text from PDF
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Extraction results dictionary
    """
    processor = PDFProcessor()
    try:
        return processor.extract_text(file_path)
    finally:
        processor.cleanup()


def chunk_document_text(text: str, chunk_size: int = 1500) -> List[Dict[str, Any]]:
    """
    Convenience function to chunk document text
    
    Args:
        text: Input text
        chunk_size: Size of each chunk
    
    Returns:
        List of text chunks
    """
    processor = PDFProcessor()
    return processor.chunk_text(text, chunk_size)
