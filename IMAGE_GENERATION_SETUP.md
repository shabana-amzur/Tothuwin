# Image Generation Setup Guide

## Current Status

✅ **System has 4-tier fallback:**
1. Pollinations AI (Free, unreliable)
2. Pollinations Turbo (Free, unreliable)
3. Pollinations Simple (Free, unreliable)
4. **Local Placeholder** (Always works)

---

## Option 1: Use Free Services (Current Setup - No Changes Needed)

**Pros:**
- ✅ Free forever
- ✅ No API keys needed
- ✅ Already configured
- ✅ Local fallback guarantees something displays

**Cons:**
- ⚠️ Unreliable (often down or slow)
- ⚠️ Lower quality
- ⚠️ Limited control over output

**Status:** Already working! Sometimes you'll get AI images, sometimes placeholders.

---

## Option 2: Google Vertex AI Imagen (Best Quality)

### Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Vertex AI SDK** (✅ Already installed)
3. **Authentication** setup
4. **API enabled**

### Step-by-Step Setup

#### **Step 1: Create Google Cloud Project**

1. Go to: https://console.cloud.google.com/
2. Create a new project or select existing one
3. Note your **PROJECT_ID**

#### **Step 2: Enable Billing**

1. Go to: https://console.cloud.google.com/billing
2. Link a billing account
3. **Note:** Imagen charges per image (~$0.03-0.08 per image)

#### **Step 3: Enable Vertex AI API**

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com
```

#### **Step 4: Authenticate**

```bash
gcloud auth application-default login
```

This will:
- Open your browser
- Ask you to login with Google
- Save credentials locally

#### **Step 5: Update Code**

Add this to your `.env` file:
```bash
# Google Cloud Configuration for Imagen
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
USE_VERTEX_AI_IMAGEN=true
```

#### **Step 6: Update image_service.py**

Replace the `__init__` method in `backend/app/services/image_service.py`:

```python
def __init__(self):
    """Initialize the image generation service"""
    import os
    
    use_vertex = os.getenv('USE_VERTEX_AI_IMAGEN', 'false').lower() == 'true'
    
    if use_vertex:
        try:
            from vertexai.preview.vision_models import ImageGenerationModel
            import vertexai
            
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
            location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
            
            vertexai.init(project=project_id, location=location)
            self.imagen_model = ImageGenerationModel.from_pretrained("imagegeneration@006")
            self.use_imagen = True
            logger.info(f"✅ ImageService initialized with Vertex AI Imagen (Project: {project_id})")
        except Exception as e:
            logger.warning(f"Vertex AI setup failed: {e}. Using free services.")
            self.use_imagen = False
    else:
        self.use_imagen = False
        logger.info("ImageService using free services (Vertex AI disabled)")
    
    self.image_dir = Path("uploads/generated_images")
    self.image_dir.mkdir(parents=True, exist_ok=True)
```

Update the `_generate_with_imagen` method:

```python
async def _generate_with_imagen(self, prompt: str) -> Dict[str, str]:
    """Generate image using Google Vertex AI Imagen"""
    try:
        # Generate image
        images = self.imagen_model.generate_images(
            prompt=prompt,
            number_of_images=1,
            language="en",
            aspect_ratio="1:1",
            safety_filter_level="block_some",
            person_generation="allow_adult",
        )
        
        # Save the image
        image_filename = f"{uuid.uuid4()}.png"
        image_path = self.image_dir / image_filename
        
        # Convert image bytes to file
        images[0].save(str(image_path))
        
        logger.info(f"✅ Image generated with Vertex AI Imagen: {image_filename}")
        image_url = f"/uploads/generated_images/{image_filename}"
        
        return {
            "success": True,
            "image_url": image_url,
            "message": f"🎨 Image generated with Google Vertex AI Imagen!\n\n**Prompt:** {prompt}",
            "is_image": True,
            "model": "vertex-ai-imagen",
            "original_request": prompt,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Vertex AI Imagen error: {str(e)}")
        raise Exception(f"Vertex AI generation failed: {str(e)}")
```

#### **Step 7: Restart Backend**

```bash
pkill -f uvicorn
./start_backend.sh
```

#### **Step 8: Test**

```
"generate an image of a sunset over mountains"
```

Should now use Vertex AI Imagen!

---

## Cost Comparison

| Service | Cost per Image | Quality | Reliability |
|---------|---------------|---------|-------------|
| **Pollinations (Free)** | $0.00 | ⭐⭐⭐ | 🔴 Low |
| **Local Placeholder** | $0.00 | ⭐ | 🟢 100% |
| **Vertex AI Imagen** | $0.04-0.08 | ⭐⭐⭐⭐⭐ | 🟢 High |

---

## Option 3: Other AI Image APIs

### Stability AI (Stable Diffusion)

**Setup:**
```bash
pip install stability-sdk
```

**Code:** Add to image_service.py
```python
import stability_sdk

api_key = os.getenv('STABILITY_API_KEY')
stability_api = stability_sdk.client.StabilityInference(
    key=api_key,
    engine="stable-diffusion-xl-1024-v1-0"
)
```

**Cost:** ~$0.002-0.01 per image
**Quality:** ⭐⭐⭐⭐

### OpenAI DALL-E 3

**Setup:**
```python
from openai import OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)
```

**Code:**
```python
response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
)
```

**Cost:** $0.04 per image
**Quality:** ⭐⭐⭐⭐⭐

---

## Recommendation

### For Development/Demo:
✅ **Keep current setup** (Free services + local fallback)
- No cost
- Good enough for demos
- Always shows something

### For Production:
✅ **Use Vertex AI Imagen** or **DALL-E 3**
- Reliable
- High quality
- Professional results
- Worth the cost

---

## Current Test Commands

```bash
# Try image generation (will use free services first)
"generate an image of a cat"
"create an image of a sunset"
"draw a futuristic city"

# If free services are down, you'll see beautiful placeholder
# If they work, you'll get AI-generated image
```

---

## Troubleshooting

### Free Services Always Fail
**Solution:** They're unreliable. Either:
1. Accept placeholder fallback
2. Upgrade to paid service (Vertex AI / DALL-E)

### Vertex AI "Not Authorized"
**Solution:**
```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

### "Billing not enabled"
**Solution:** Enable billing at https://console.cloud.google.com/billing

---

## Summary

**You have 3 choices:**

1. **Keep as-is** (Free, unreliable, has fallback) ← Current
2. **Add Vertex AI** (Best quality, $0.04-0.08/image, requires setup)
3. **Add DALL-E** (Great quality, $0.04/image, easy setup)

All options work with your current agent setup. The agent detects image requests and routes to the image service automatically.

**The system already works! The placeholder is your safety net.** 🎨
