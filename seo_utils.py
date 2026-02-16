import os
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import io

# --- AI WRITER ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def generate_ai_content(prompt, context, max_tokens=300):
    if not client: return "AI Configuration Error."
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert SEO content writer. Write in HTML format (using <h2>, <p>, <ul>). Do not include <html> or <body> tags. Keep it professional."},
                {"role": "user", "content": f"Write about: {prompt}. Context: {context}"}
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error generating content: {e}"

# --- DYNAMIC IMAGE GENERATOR ---
def generate_og_image(text, brand_text="StreamKey Guides"):
    """
    Creates a 1200x630 image with the article title dynamically.
    """
    width, height = 1200, 630
    background_color = (15, 23, 42) # Dark Slate
    text_color = (255, 255, 255)
    
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fallback to default if not found
    try:
        # Render usually has DejaVuSans installed
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    # Draw Title (Centered logic simplified)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width - text_width) / 2
    y = height / 2 - 50
    
    draw.text((x, y), text, font=font, fill=text_color)
    
    # Draw Brand
    draw.text((50, 550), brand_text, font=sub_font, fill=(59, 130, 246)) # Blue color

    # Save to buffer
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr
