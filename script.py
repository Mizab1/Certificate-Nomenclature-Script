import os
import time
import uuid
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
import sys
import traceback

def add_text_to_image_and_convert_to_pdf(image_path, text, position, font_path=None, font_size=30):
    """
    Opens an image, adds text centered at a specific position, and converts it to a PDF in landscape orientation.
    
    Args:
        image_path (str): Path to the JPG image
        text (str): Text to add to the image
        position (tuple): Position (x, y) where the center of the text will be
        font_path (str, optional): Path to a TTF font file
        font_size (int, optional): Font size
        
    Returns:
        str: Path to the created PDF file
    """
    try:
        # Generate a unique temporary filename to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        temp_image_path = f"temp_with_text_{unique_id}.jpg"
        
        # Open the image
        with Image.open(image_path) as img:
            # Create a copy of the image to work with
            img_copy = img.copy()
        
        # Create a drawing object
        draw = ImageDraw.Draw(img_copy)
        
        # Font handling - ensuring the correct size is applied
        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, size=font_size)
                print(f"Using custom font: {font_path} with size {font_size}")
            else:
                # If no font is provided or it doesn't exist, try to use a system font
                system_fonts = {
                    'windows': 'arial.ttf',
                    'darwin': '/Library/Fonts/Arial.ttf',  # macOS
                    'linux': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Linux
                }
                
                if sys.platform.startswith('win'):
                    default_font = system_fonts['windows']
                elif sys.platform == 'darwin':
                    default_font = system_fonts['darwin']
                else:
                    default_font = system_fonts['linux']
                
                try:
                    font = ImageFont.truetype(default_font, size=font_size)
                    print(f"Using system font: {default_font} with size {font_size}")
                except Exception:
                    # Last resort - use default font
                    font = ImageFont.load_default()
                    print(f"Using PIL default font (size may not scale properly)")
        except Exception as e:
            print(f"Error with font: {e}")
            font = ImageFont.load_default()
            print("Falling back to default font")
        
        # Calculate text dimensions to center it
        # Handle different versions of Pillow
        if hasattr(draw, 'textsize'):
            text_width, text_height = draw.textsize(text, font=font)
        else:
            bbox = font.getbbox(text)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        # Calculate the position for centered text
        x, y = position
        x_centered = x - (text_width / 2)
        
        # Add text to the image with center alignment
        draw.text((x_centered, y), text, fill="black", font=font)
        
        # Save the modified image
        img_copy.save(temp_image_path)
        
        # Use the provided text as the filename for the PDF
        output_pdf = f"{text.strip().replace(' ', '_')}.pdf"
        
        # Convert the image to PDF with landscape orientation
        pagesize = landscape(letter)  # This creates a landscape orientation
        c = canvas.Canvas(output_pdf, pagesize=pagesize)
        width, height = pagesize  # Note that width and height are swapped in landscape mode
        
        # Open the temp image to get its dimensions
        with Image.open(temp_image_path) as img:
            img_width, img_height = img.size
            
            # Calculate scaling to fit the image on the PDF page
            ratio = min(width/img_width, height/img_height)
            img_width = img_width * ratio
            img_height = img_height * ratio
            
            # Center the image on the page
            x_centered = (width - img_width) / 2
            y_centered = (height - img_height) / 2
        
        # Add the image to the PDF
        c.drawImage(temp_image_path, x_centered, y_centered, width=img_width, height=img_height)
        c.save()
        
        # Small delay to ensure file operations are complete
        time.sleep(0.5)
        
        # Try to remove the temporary image file
        try:
            os.remove(temp_image_path)
        except Exception as e:
            print(f"Warning: Could not delete temporary file {temp_image_path}: {e}")
            print("You may need to delete it manually later.")
        
        return output_pdf
    
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

def title_case_name(name):
    """
    Convert a name to title case (first letter of each word capitalized, rest lowercase)
    
    Args:
        name (str): The name to convert
        
    Returns:
        str: The name in title case
    """
    # Split the name into words and apply title case to each word
    words = name.strip().split()
    title_cased_words = [word.capitalize() for word in words]
    
    # Join the words back together
    return ' '.join(title_cased_words)

def process_names_from_file(image_path, names_file, position, font_path=None, font_size=30):
    """
    Process multiple names from a text file.
    
    Args:
        image_path (str): Path to the JPG image
        names_file (str): Path to text file containing names (one per line)
        position (tuple): Position (x, y) where the center of the text will be
        font_path (str, optional): Path to a TTF font file
        font_size (int, optional): Font size
    """
    successful = 0
    failed = 0
    
    try:
        with open(names_file, 'r', encoding='utf-8') as file:
            # Read all non-empty lines and strip whitespace
            names = [line.strip() for line in file if line.strip()]
        
        total_names = len(names)
        print(f"Found {total_names} names in {names_file}")
        
        for i, raw_name in enumerate(names, 1):
            # Convert name to title case (first letter of each word capitalized)
            properly_cased_name = title_case_name(raw_name)
            
            print(f"Processing {i}/{total_names}: '{raw_name}' → '{properly_cased_name}'")
            
            result = add_text_to_image_and_convert_to_pdf(
                image_path, properly_cased_name, position, font_path, font_size
            )
            
            if result:
                print(f"  ✓ PDF created successfully: {result}")
                successful += 1
            else:
                print(f"  ✗ Failed to create PDF for: {properly_cased_name}")
                failed += 1
        
        print("\nSummary:")
        print(f"  Successful: {successful}/{total_names}")
        print(f"  Failed: {failed}/{total_names}")
        
    except Exception as e:
        print(f"Error processing names file: {e}")
        traceback.print_exc()

def main():
    if len(sys.argv) < 4:
        print("Usage: python script.py <image_path> <names_file> <x_position> <y_position> [font_path] [font_size]")
        print("Example: python script.py image.jpg names.txt 500 300 Arial.ttf 36")
        return
    
    image_path = sys.argv[1]
    names_file = sys.argv[2]
    x_pos = int(sys.argv[3])
    y_pos = int(sys.argv[4])
    
    font_path = None
    if len(sys.argv) >= 6:
        font_path = sys.argv[5]
    
    font_size = 30
    if len(sys.argv) >= 7:
        font_size = int(sys.argv[6])
        print(f"Using font size: {font_size}")
    
    process_names_from_file(image_path, names_file, (x_pos, y_pos), font_path, font_size)

if __name__ == "__main__":
    main()