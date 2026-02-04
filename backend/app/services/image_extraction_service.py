"""
Image data extraction service using Google Gemini Vision API.

IMPORTANT: This service uses the Gemini API (v1) for vision tasks.
- Gemini 1.5 Flash supports multimodal input (text + images)
- Uses stable v1 API endpoint (not v1beta)
- Falls back to OCR if Gemini Vision fails
"""
import base64
import io
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image
import google.generativeai as genai
import os
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ImageExtractionService:
    """Service for extracting structured data from images using Gemini Vision API."""
    
    def __init__(self):
        """
        Initialize the extraction service with Gemini API.
        
        Uses gemini-1.5-flash which:
        - Supports vision (multimodal: text + images)
        - Uses stable v1 API (not v1beta)
        - Has good performance and cost efficiency
        """
        try:
            # Configure Gemini API with API key
            genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
            
            # Use gemini-2.0-flash - latest model with vision support
            # NOTE: Available models that support image input:
            # - gemini-2.0-flash (recommended, latest)
            # - gemini-2.0-flash-001 (stable version)
            # The library uses v1beta API internally, but that's handled automatically
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("✅ Gemini Vision API initialized with gemini-2.0-flash")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini Vision API: {str(e)}")
            self.model = None
    
    def encode_image(self, image_bytes: bytes) -> str:
        """
        Encode image bytes to base64 string.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def validate_image(self, image_bytes: bytes) -> tuple[bool, Optional[str]]:
        """
        Validate image format and size.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Ensure we have bytes, not BytesIO
            if isinstance(image_bytes, io.BytesIO):
                image_bytes = image_bytes.read()
            
            # Check file size (max 10MB)
            if len(image_bytes) > 10 * 1024 * 1024:
                return False, "Image size exceeds 10MB limit"
            
            # Validate image format - support WEBP too
            bytes_io = io.BytesIO(image_bytes)
            image = Image.open(bytes_io)
            if image.format not in ['JPEG', 'PNG', 'JPG', 'WEBP']:
                return False, f"Unsupported image format: {image.format}"
            
            return True, None
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    def build_extraction_prompt(
        self,
        document_type: Optional[str] = None,
        expected_fields: Optional[List[str]] = None
    ) -> str:
        """
        Build a structured prompt for data extraction.
        
        Args:
            document_type: Type of document (invoice, receipt, etc.)
            expected_fields: List of fields to extract
            
        Returns:
            Formatted prompt string
        """
        prompt = "Extract structured data from this image and return it as valid JSON.\n\n"
        
        if document_type:
            prompt += f"Document Type: {document_type}\n\n"
        
        if expected_fields:
            prompt += "Extract the following fields:\n"
            for field in expected_fields:
                prompt += f"- {field}\n"
            prompt += "\n"
        else:
            prompt += "Extract all relevant fields including but not limited to:\n"
            prompt += "- Document numbers (invoice, receipt, ID, etc.)\n"
            prompt += "- Dates (issue date, due date, expiry, etc.)\n"
            prompt += "- Monetary amounts (total, subtotal, tax, etc.)\n"
            prompt += "- VENDOR/SELLER information:\n"
            prompt += "  * vendor_name or merchant_name: The company/person ISSUING/SELLING (usually at top with logo)\n"
            prompt += "  * Look for business name in header, footer, or 'From' section\n"
            prompt += "- CUSTOMER/BUYER information:\n"
            prompt += "  * customer_name: The person/company RECEIVING/BUYING (billing/shipping address)\n"
            prompt += "- Contact information (email, phone, address)\n"
            prompt += "- IMPORTANT: Look carefully for email addresses throughout the entire document, especially in headers, footers, and bottom sections\n"
            prompt += "- Any other relevant information\n\n"
        
        prompt += """
IMPORTANT INSTRUCTIONS:
1. Return ONLY valid JSON, no additional text or markdown
2. Use snake_case for field names (e.g., invoice_number, total_amount)
3. For dates, use ISO format: YYYY-MM-DD
4. For monetary values, return as numbers WITHOUT currency symbols (not strings)
5. If a field is not found, omit it from the JSON (do not use null)
6. Extract exactly what you see, do not infer or guess
7. SCAN THE ENTIRE DOCUMENT including headers, footers, and fine print at the bottom for email addresses
8. ALWAYS extract currency as a separate field:
   - If you see $ symbol, set "currency": "USD"
   - If you see ₹ symbol, set "currency": "INR"
   - If you see € symbol, set "currency": "EUR"
   - If you see £ symbol, set "currency": "GBP"
   - Look for currency in amounts, totals, or any monetary fields
8. Extract amounts as pure numbers (e.g., 162.37 not $162.37)

Example response format:
{
    "invoice_number": "INV-2024-001",
    "invoice_date": "2024-01-15",
    "total_amount": 1500.00,
    "currency": "USD",
    "vendor_name": "ABC Corp",
    "customer_name": "John Doe",
    "email": "contact@company.com"
}
"""
        return prompt
    
    async def extract_from_image(
        self,
        image_bytes: bytes,
        document_type: Optional[str] = None,
        expected_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from an image using Gemini Vision API (v1).
        
        Args:
            image_bytes: Raw image bytes
            document_type: Type of document being processed
            expected_fields: List of fields to extract
            
        Returns:
            Dictionary containing extracted data
            
        Raises:
            ValueError: If image is invalid, model unavailable, or extraction fails
        """
        # Check if model is initialized
        if self.model is None:
            raise ValueError("Gemini Vision API not initialized. Check API key configuration.")
        
        # Validate image
        is_valid, error_msg = self.validate_image(image_bytes)
        if not is_valid:
            raise ValueError(f"Image validation failed: {error_msg}")
        
        # Build prompt
        prompt = self.build_extraction_prompt(document_type, expected_fields)
        
        try:
            # Prepare image for Gemini API
            # NOTE: google-generativeai library accepts PIL Images directly
            from PIL import Image as PILImage
            image = PILImage.open(io.BytesIO(image_bytes))
            
            logger.info(f"📸 Calling Gemini Vision API with {document_type or 'generic'} document")
            
            # Call Gemini API with multimodal input (text + image)
            # This uses the v1 API endpoint with generateContent
            response = self.model.generate_content(
                [prompt, image],
                generation_config={
                    'temperature': 0.1,  # Low temperature for consistent extraction
                    'max_output_tokens': 2048
                }
            )
            
            # Check if response was blocked or empty
            if not response or not response.text:
                if hasattr(response, 'prompt_feedback'):
                    raise ValueError(f"Gemini API blocked response: {response.prompt_feedback}")
                raise ValueError("Gemini API returned empty response")
            
            # Extract and parse response
            content = response.text
            logger.info(f"✅ Gemini Vision API response received ({len(content)} chars)")
            
            # Try to parse JSON from response
            try:
                # Remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()
                
                extracted_data = json.loads(content)
                logger.info(f"✅ Successfully extracted {len(extracted_data)} fields")
                return extracted_data
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parse error: {str(e)}")
                raise ValueError(f"Failed to parse extracted data as JSON: {str(e)}\nContent: {content[:200]}...")
        
        except ValueError:
            # Re-raise ValueError (image validation, JSON parsing, API errors)
            raise
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Gemini Vision API error: {error_msg}")
            
            # Distinguish different types of errors
            if "404" in error_msg or "not found" in error_msg.lower():
                raise ValueError(
                    f"Gemini Vision model not available. "
                    f"Ensure 'gemini-1.5-flash' is accessible with your API key. "
                    f"Error: {error_msg}"
                )
            elif "403" in error_msg or "permission" in error_msg.lower():
                raise ValueError(
                    f"Gemini API access denied. Check your API key permissions. "
                    f"Error: {error_msg}"
                )
            elif "429" in error_msg or "quota" in error_msg.lower():
                raise ValueError(
                    f"Gemini API quota exceeded. Please try again later. "
                    f"Error: {error_msg}"
                )
            else:
                raise ValueError(f"Gemini Vision API error: {error_msg}")
    
    async def extract_with_fallback(
        self,
        image_bytes: bytes,
        document_type: Optional[str] = None,
        expected_fields: Optional[List[str]] = None
    ) -> Tuple[Dict[str, Any], str]:
        """
        Extract data with OCR fallback if Gemini Vision API fails.
        
        Strategy:
        1. Try Gemini Vision API first (preferred method)
        2. If Gemini fails, attempt OCR fallback with pytesseract
        3. If OCR is unavailable, return clear error message
        
        Args:
            image_bytes: Raw image bytes
            document_type: Type of document being processed
            expected_fields: List of fields to extract
            
        Returns:
            Tuple of (extracted_data, extraction_method)
            - extraction_method: 'vision_ai', 'ocr', or 'failed'
            
        Raises:
            ValueError: If both Vision and OCR extraction fail
        """
        vision_error = None
        ocr_error = None
        
        # Try Gemini Vision API first
        try:
            logger.info("🔍 Attempting extraction with Gemini Vision API...")
            data = await self.extract_from_image(image_bytes, document_type, expected_fields)
            logger.info("✅ Gemini Vision extraction successful")
            return data, "vision_ai"
        except Exception as e:
            vision_error = str(e)
            logger.warning(f"⚠️ Gemini Vision failed: {vision_error}")
        
        # Fallback to OCR if Gemini fails
        try:
            logger.info("🔍 Falling back to OCR extraction...")
            data = await self._ocr_fallback(image_bytes, document_type, expected_fields)
            logger.info("✅ OCR extraction successful")
            return data, "ocr"
        except Exception as e:
            ocr_error = str(e)
            logger.error(f"❌ OCR fallback failed: {ocr_error}")
        
        # Both methods failed - provide comprehensive error message
        error_parts = []
        error_parts.append("Both Vision and OCR extraction failed.")
        error_parts.append(f"\nVision error: {vision_error}")
        error_parts.append(f"\nOCR error: {ocr_error}")
        
        # Add helpful suggestions based on error types
        if "tesseract" in ocr_error.lower() or "not installed" in ocr_error.lower():
            error_parts.append(
                "\n\nOCR is unavailable (Tesseract not installed). "
                "Please fix the Gemini Vision API configuration or install Tesseract."
            )
        
        raise ValueError("".join(error_parts))
    
    async def _ocr_fallback(
        self,
        image_bytes: bytes,
        document_type: Optional[str] = None,
        expected_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fallback OCR extraction using pytesseract (Tesseract OCR).
        
        NOTE: Requires Tesseract to be installed on the system:
        - macOS: brew install tesseract
        - Ubuntu: apt-get install tesseract-ocr
        - Windows: Download from GitHub
        
        Args:
            image_bytes: Raw image bytes
            document_type: Type of document being processed
            expected_fields: List of fields to extract
            
        Returns:
            Dictionary containing extracted data (basic text patterns)
            
        Raises:
            ValueError: If pytesseract is not installed or OCR fails
        """
        try:
            import pytesseract
        except ImportError:
            raise ValueError(
                "OCR fallback requires pytesseract library. "
                "Install with: pip install pytesseract"
            )
        
        try:
            # Ensure we have bytes, not BytesIO
            if isinstance(image_bytes, io.BytesIO):
                image_bytes = image_bytes.read()
            
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            logger.info("📄 Running Tesseract OCR on image...")
            
            # Perform OCR - this may fail if tesseract binary is not installed
            try:
                text = pytesseract.image_to_string(image)
            except pytesseract.TesseractNotFoundError:
                raise ValueError(
                    "Tesseract OCR is not installed or not in PATH. "
                    "Install Tesseract: "
                    "macOS: 'brew install tesseract', "
                    "Ubuntu: 'apt-get install tesseract-ocr'"
                )
            
            logger.info(f"✅ OCR extracted {len(text)} characters")
            
            # Simple extraction logic (can be enhanced)
            extracted_data = {
                "raw_text": text,
                "extraction_method": "ocr_fallback",
                "note": "Limited field extraction - OCR provides raw text only"
            }
            
            # Try to find common patterns
            import re
            
            # Look for dates
            date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'
            dates = re.findall(date_pattern, text)
            if dates:
                extracted_data["extracted_dates"] = dates[:5]  # Limit to first 5
            
            # Look for amounts (money)
            amount_pattern = r'\$?\s*\d+[,.]?\d*\.?\d{2}'
            amounts = re.findall(amount_pattern, text)
            if amounts:
                extracted_data["extracted_amounts"] = amounts[:5]  # Limit to first 5
            
            # Look for email
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, text)
            if emails:
                extracted_data["email"] = emails[0]
            
            return extracted_data
            
        except ImportError as e:
            raise ValueError(f"OCR library error: {str(e)}")
        except Exception as e:
            raise ValueError(f"OCR extraction failed: {str(e)}")
            if dates:
                extracted_data["extracted_dates"] = dates
            
            # Look for amounts
            amount_pattern = r'\$?\s*\d+[,.]?\d*\.?\d{2}'
            amounts = re.findall(amount_pattern, text)
            if amounts:
                extracted_data["extracted_amounts"] = amounts
            
            # Look for email
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, text)
            if emails:
                extracted_data["email"] = emails[0]
            
            return extracted_data
            
        except ImportError:
            raise ValueError("OCR fallback requires pytesseract library")
        except Exception as e:
            raise ValueError(f"OCR extraction failed: {str(e)}")


# Singleton instance
_extraction_service = None


def get_extraction_service() -> ImageExtractionService:
    """Get or create singleton extraction service instance."""
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ImageExtractionService()
    return _extraction_service
