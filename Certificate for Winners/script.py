# Ex: python script.py base_cert.jpg names.txt 900 510 64 "Project Exhibition" 930 600 52 "II" 915 715 42

import os
import time
import uuid
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
import sys
import traceback

def add_texts_to_image_and_convert_to_pdf(
    image_path, 
    name, name_position, name_font_size,
    event_name, event_position, event_font_size,
    rank, rank_position, rank_font_size
):
    """
    Opens an image, adds multiple text elements at specified positions, and converts it to a PDF.
    
    Args:
        image_path (str): Path to the JPG image
        name (str): Name to add to the image
        name_position (tuple): Position (x, y) where the center of the name will be
        name_font_size (int): Font size for the name
        event_name (str): Event name to add to the image
        event_position (tuple): Position (x, y) where the center of the event name will be
        event_font_size (int): Font size for the event name
        rank (str): Rank to add to the image
        rank_position (tuple): Position (x, y) where the center of the rank will be
        rank_font_size (int): Font size for the rank
        
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
        
        # Get system font based on platform
        system_fonts = {
            'windows': 'arial.ttf',
            'darwin': '/Library/Fonts/Arial.ttf',  # macOS
            'linux': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Linux
        }
        
        if sys.platform.startswith('win'):
            default_font_path = system_fonts['windows']
        elif sys.platform == 'darwin':
            default_font_path = system_fonts['darwin']
        else:
            default_font_path = system_fonts['linux']
        
        # Function to add centered text with specified font size
        def add_centered_text(text, position, font_size):
            try:
                # Try to use system font with specified size
                font = ImageFont.truetype(default_font_path, size=font_size)
            except Exception as e:
                print(f"Error loading font: {e}, falling back to default")
                font = ImageFont.load_default()
            
            # Calculate text dimensions to center it
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
        
        # Add all text elements to the image
        add_centered_text(name, name_position, name_font_size)
        add_centered_text(event_name, event_position, event_font_size)
        add_centered_text(rank, rank_position, rank_font_size)
        
        # Save the modified image
        img_copy.save(temp_image_path)
        
        # Use the provided name as the filename for the PDF
        output_pdf = f"{name.strip().replace(' ', '_')}.pdf"
        
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

def process_names_from_file(
    image_path, names_file, 
    name_position, name_font_size,
    event_name, event_position, event_font_size,
    rank, rank_position, rank_font_size
):
    """
    Process multiple names from a text file.
    
    Args:
        image_path (str): Path to the JPG image
        names_file (str): Path to text file containing names (one per line)
        name_position (tuple): Position (x, y) where the center of the name will be
        name_font_size (int): Font size for the name
        event_name (str): Event name to add to each image
        event_position (tuple): Position (x, y) where the center of the event name will be
        event_font_size (int): Font size for the event name
        rank (str): Rank to add to each image
        rank_position (tuple): Position (x, y) where the center of the rank will be
        rank_font_size (int): Font size for the rank
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
            print(f"  Event: '{event_name}', Rank: '{rank}'")
            
            result = add_texts_to_image_and_convert_to_pdf(
                image_path, 
                properly_cased_name, name_position, name_font_size,
                event_name, event_position, event_font_size,
                rank, rank_position, rank_font_size
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
    if len(sys.argv) < 11:
        print("""
Usage: python script.py <image_path> <names_file> 
                       <name_x> <name_y> <name_font_size>
                       <event_name> <event_x> <event_y> <event_font_size>
                       <rank> <rank_x> <rank_y> <rank_font_size>
                       
Example: python script.py certificate.jpg names.txt 
                          500 300 36
                          "Annual Science Competition" 500 200 24
                          "First Prize" 500 400 20
        """)
        return
    
    # Parse basic arguments
    image_path = sys.argv[1]
    names_file = sys.argv[2]
    
    # Parse name position and font size
    name_x = int(sys.argv[3])
    name_y = int(sys.argv[4])
    name_font_size = int(sys.argv[5])
    
    # Parse event details
    event_name = sys.argv[6]
    event_x = int(sys.argv[7])
    event_y = int(sys.argv[8])
    event_font_size = int(sys.argv[9])
    
    # Parse rank details
    rank = sys.argv[10]
    rank_x = int(sys.argv[11])
    rank_y = int(sys.argv[12])
    rank_font_size = int(sys.argv[13])
    
    print(f"Image: {image_path}")
    print(f"Names file: {names_file}")
    print(f"Name position: ({name_x}, {name_y}), Font size: {name_font_size}")
    print(f"Event: '{event_name}', Position: ({event_x}, {event_y}), Font size: {event_font_size}")
    print(f"Rank: '{rank}', Position: ({rank_x}, {rank_y}), Font size: {rank_font_size}")
    
    # Process all names with the specified settings
    process_names_from_file(
        image_path, names_file,
        (name_x, name_y), name_font_size,
        event_name, (event_x, event_y), event_font_size,
        rank, (rank_x, rank_y), rank_font_size
    )

if __name__ == "__main__":
    main()