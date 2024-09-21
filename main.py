import io
import json
import cv2
import requests
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from filter_data import filter_test_keywords

# Function to select the image file
def select_image_file():
    Tk().withdraw()  # Hide the root window
    file_path = askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.gif")]
    )
    return file_path

# Function to detect text using OCR API
def detect_text_with_ocr(image_path, ocr_engine=2):
    # Read the selected image
    img = cv2.imread(image_path)
    
    # OCR API endpoint
    url_api = "https://api.ocr.space/parse/image"
    
    # Compress image to prepare it for upload
    _, compressedimage = cv2.imencode(".jpg", img, [1, 90])
    file_bytes = io.BytesIO(compressedimage)
    
    # API request parameters
    params = {
        "apikey": "K86127550388957",
        "language": "eng",  # Change this to the desired language code
        "isOverlayRequired": "true",  # Set to "true" to get bounding boxes
        "detectOrientation": "true",  # Set to "true" to auto-rotate the image
        "scale": "true",  # Set to "true" to improve OCR result for low-res images
        "OCREngine": str(ocr_engine)  # Choose between 1 and 2
    }
    
    # Sending the image file to the API
    result = requests.post(url_api,
                           files={"screenshot.jpg": file_bytes},
                           data=params)

    # Parsing the response
    result = result.content.decode()
    result = json.loads(result)
    
    # Save the parsed results to a JSON file
    with open('parsed_results.json', 'w') as json_file:
        json.dump(result, json_file, indent=4)
    
    # Extracting detected text and overlay data
    parsed_results = result.get("ParsedResults")[0]
    text_detected = parsed_results.get("ParsedText")
    text_lines = text_detected.splitlines()
    print(text_lines)
    
    # Calling the filtering functions with the file name
    file_name = image_path.split("/")[-1]  # Extracting file name from path
    filter_test_keywords(parsed_results, file_name, tolerance=10)

def main():
    # Let the user select the image file
    image_path = select_image_file()
    
    if not image_path:
        print("No image selected.")
        return
    
    # Detect text with selected OCR engine
    detect_text_with_ocr(image_path)

if __name__ == "__main__":
    main()
