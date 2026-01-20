# Image Generation Feature - Important Note

## Current Status

**Gemini 2.0 Flash models are text-generation models and cannot directly generate images.**

The current implementation detects image generation requests and provides helpful responses, but does not actually create images.

## To Enable Actual Image Generation

You have several options:

### Option 1: Google Imagen API (Recommended for Google ecosystem)
```bash
# Requires separate API access from Google Cloud
# https://cloud.google.com/vision/docs/image-generator
```

Add to `.env`:
```
GOOGLE_IMAGEN_API_KEY=your_imagen_key
```

### Option 2: OpenAI DALL-E
```bash
pip install openai
```

Add to `.env`:
```
OPENAI_API_KEY=your_openai_key
```

### Option 3: Stable Diffusion (Self-hosted or API)
```bash
pip install diffusers torch transformers
```

### Option 4: External Image APIs
- **Replicate** - https://replicate.com
- **Hugging Face Inference API** - https://huggingface.co/inference-api

## Implementation Guide

Once you have access to an image generation API, update `backend/app/services/image_service.py`:

```python
async def generate_image(self, prompt: str, user_id: int = None):
    # Replace with actual API call
    # Example for DALL-E:
    # response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    # image_url = response['data'][0]['url']
    
    # Return image URL or base64 data
    return {
        "success": True,
        "image_url": image_url,
        "prompt": prompt,
        "timestamp": datetime.now().isoformat()
    }
```

## Current Behavior

When users request image generation, the AI will:
1. Detect the request using keywords
2. Explain that direct generation isn't available
3. Offer to create detailed prompts for external tools
4. Suggest alternatives

This maintains a good user experience while being transparent about capabilities.
