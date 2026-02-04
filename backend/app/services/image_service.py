"""
Image Generation Service - Vertex AI Imagen 3
Handles image generation using Google's Vertex AI Imagen 3 model
"""

import logging
from typing import Dict
from datetime import datetime
from pathlib import Path
import uuid
from PIL import Image, ImageDraw, ImageFont

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ImageService:
    """
    Service for generating images using Vertex AI Imagen 3
    """
    
    def __init__(self):
        """Initialize the image generation service"""
        from app.config import get_settings
        settings = get_settings()
        
        # Check if Vertex AI is configured
        self.google_cloud_project = settings.GOOGLE_CLOUD_PROJECT
        self.google_cloud_location = settings.GOOGLE_CLOUD_LOCATION
        self.use_imagen = bool(self.google_cloud_project and len(self.google_cloud_project) > 3)
        
        if self.use_imagen:
            try:
                import vertexai
                from vertexai.preview.vision_models import ImageGenerationModel
                from google.oauth2 import service_account
                import os
                
                # Load service account credentials
                credentials = None
                if hasattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS') and settings.GOOGLE_APPLICATION_CREDENTIALS:
                    creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
                    
                    if os.path.exists(creds_path):
                        credentials = service_account.Credentials.from_service_account_file(creds_path)
                        logger.info(f"📝 Loaded service account from: {creds_path}")
                    else:
                        logger.warning(f"⚠️ Service account file not found: {creds_path}")
                
                # Initialize Vertex AI
                vertexai.init(
                    project=self.google_cloud_project, 
                    location=self.google_cloud_location,
                    credentials=credentials
                )
                # Use the latest Imagen 3 model (imagegeneration@006 is deprecated)
                self.imagen_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
                logger.info(f"✅ ImageService initialized with Vertex AI Imagen 3 (Project: {self.google_cloud_project})")
            except Exception as e:
                logger.warning(f"⚠️ Vertex AI Imagen initialization failed: {str(e)}")
                self.use_imagen = False
        
        if not self.use_imagen:
            logger.warning("⚠️ Vertex AI not configured - only placeholder images will be available")
            
        self.image_dir = Path("uploads/generated_images")
        self.image_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_image(
        self,
        prompt: str,
        user_id: int = None
    ) -> Dict[str, str]:
        """
        Generate an image from text prompt using Vertex AI Imagen 3
        
        Args:
            prompt: The text description for image generation
            user_id: User ID for tracking
        
        Returns:
            Dictionary with image data and metadata
        """
        try:
            logger.info(f"Generating image: {prompt[:50]}...")
            
            # Try Vertex AI Imagen
            if self.use_imagen:
                try:
                    return await self._generate_with_imagen(prompt)
                except Exception as imagen_error:
                    logger.error(f"Vertex AI Imagen failed: {str(imagen_error)}")
                    # Fall back to placeholder
                    return await self._generate_placeholder(prompt, error=str(imagen_error))
            else:
                # Vertex AI not configured
                return await self._generate_placeholder(prompt, error="Vertex AI not configured")
            
        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")
            return await self._generate_placeholder(prompt, error=str(e))
    
    async def _generate_with_imagen(self, prompt: str) -> Dict[str, str]:
        """Generate image using Vertex AI Imagen 3"""
        logger.info("🎨 Generating with Vertex AI Imagen 3...")
        
        result = self.imagen_model.generate_images(
            prompt=prompt,
            number_of_images=1,
            safety_filter_level="block_some",
            person_generation="allow_adult",
            aspect_ratio="1:1",
        )
        
        if result.images and len(result.images) > 0:
            image = result.images[0]
            image_filename = f"{uuid.uuid4()}.png"
            image_path = self.image_dir / image_filename
            image._pil_image.save(str(image_path))
            
            logger.info(f"✅ Image generated with Vertex AI Imagen 3: {image_filename}")
            image_url = f"/uploads/generated_images/{image_filename}"
            
            return {
                "success": True,
                "image_url": image_url,
                "message": f"🎨 Image generated successfully with **Vertex AI Imagen 3**!\n\n**Prompt:** {prompt}\n\n**Model:** Google Imagen 3 (High Quality)\n**Powered by:** Your Google Cloud Credits",
                "is_image": True,
                "model": "vertex-ai-imagen-3",
                "original_request": prompt,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise Exception("No image was generated by Vertex AI Imagen")
    
    async def _generate_placeholder(self, prompt: str, error: str = None) -> Dict[str, str]:
        """Generate a placeholder image when Vertex AI is unavailable"""
        logger.info("🎨 Generating placeholder image...")
        
        # Create gradient image
        width, height = 1024, 1024
        img = Image.new('RGB', (width, height), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient concentric circles
        colors = [(255, 107, 107), (255, 159, 64), (255, 206, 84), (75, 192, 192), (54, 162, 235)]
        for i in range(10):
            radius = width // 2 - (i * 50)
            if radius > 0:
                color = colors[i % len(colors)]
                alpha = 255 - (i * 20)
                draw.ellipse(
                    [(width//2 - radius, height//2 - radius), 
                     (width//2 + radius, height//2 + radius)],
                    outline=color + (alpha,),
                    width=3
                )
        
        # Add text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Center text
        title = f"Image: {prompt[:40]}"
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), title, fill=(255, 255, 255), font=font)
        
        if error:
            error_text = "Vertex AI temporarily unavailable"
            bbox2 = draw.textbbox((0, 0), error_text, font=small_font)
            text_width2 = bbox2[2] - bbox2[0]
            x2 = (width - text_width2) // 2
            draw.text((x2, y + 60), error_text, fill=(255, 200, 200), font=small_font)
        
        # Save
        image_filename = f"{uuid.uuid4()}.png"
        image_path = self.image_dir / image_filename
        img.save(str(image_path), 'PNG')
        
        logger.info(f"✅ Placeholder generated: {image_filename}")
        image_url = f"/uploads/generated_images/{image_filename}"
        
        return {
            "success": True,
            "image_url": image_url,
            "message": f"⚠️ Generated placeholder image (Vertex AI unavailable)\n\n**Your prompt:** {prompt}\n\n**Note:** This is a placeholder. Vertex AI Imagen 3 is temporarily unavailable.",
            "is_image": True,
            "model": "placeholder",
            "original_request": prompt,
            "timestamp": datetime.now().isoformat()
        }
    
    def detect_image_request(self, message: str) -> bool:
        """
        Detect if the user is requesting image generation
        
        Args:
            message: User's message
            
        Returns:
            True if message contains image generation keywords
        """
        # Direct patterns that indicate image generation
        direct_patterns = [
            "generate an image", "generate image", "create an image", "create image",
            "make an image", "make image", "draw an image", "draw image",
            "generate a picture", "create a picture", "make a picture",
            "generate a photo", "create a photo", "make a photo",
            "show me an image", "show me a picture", "show me an illustration"
        ]
        
        message_lower = message.lower()
        
        # Check direct patterns first
        if any(pattern in message_lower for pattern in direct_patterns):
            return True
        
        # Check if starts with "draw" (common pattern: "draw me a...", "draw a...")
        if message_lower.startswith("draw "):
            return True
        
        # Check for action + image word combination
        keywords = ["generate", "create", "make", "show me"]
        image_words = ["image", "picture", "photo", "pic", "illustration", "drawing", "artwork"]
        
        has_action = any(keyword in message_lower for keyword in keywords)
        has_image_word = any(word in message_lower for word in image_words)
        
        return has_action and has_image_word


# Singleton instance
_service_instance = None

def get_image_service() -> ImageService:
    """Get or create singleton ImageService instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ImageService()
    return _service_instance
