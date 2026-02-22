from PIL import Image
import os

img_path = 'app/static/images/logo.png'

if os.path.exists(img_path):
    img = Image.open(img_path)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Get bounding box of non-transparent areas
    bbox = img.getbbox()
    if bbox:
        # crop the image to the boundary box
        cropped_img = img.crop(bbox)
        
        # Save cropped image back
        cropped_img.save(img_path)
        print("Logo successfully cropped and saved.")
    else:
        print("Image is entirely transparent or could not find bbox.")
else:
    print(f"File not found: {img_path}")
