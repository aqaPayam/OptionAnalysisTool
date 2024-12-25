from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import base64
import cv2
import pytesseract
import numpy as np

# Path to your ChromeDriver
chrome_driver_path = r"C:\Users\payam\Desktop\chromedriver-win64\chromedriver.exe"  # Adjust path as needed

# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Open the browser maximized

# Setup the service for ChromeDriver
service = Service(chrome_driver_path)

# Initialize the WebDriver for Chrome with options
driver = webdriver.Chrome(service=service, options=options)

# Specify the path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust this path as needed

try:
    # Open the desired URL
    url = "https://bbi.ephoenix.ir/auth/login"
    print(f"Opening URL: {url}")
    driver.get(url)

    # Wait for the images to load
    print("Waiting for images to load...")
    max_attempts = 5  # Max attempts to refresh the page
    attempt = 0
    images = []

    while not images and attempt < max_attempts:
        try:
            # Wait until at least one image is found or timeout after 10 seconds
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.TAG_NAME, "img")) > 0
            )
            images = driver.find_elements(By.TAG_NAME, "img")
        except TimeoutException:
            print("No images found, refreshing the page...")
            driver.refresh()  # Refresh the page
            attempt += 1

    if not images:
        print("Failed to load images after multiple attempts.")
    else:
        print(f"Found {len(images)} images. Processing CAPTCHA...")

        # Process only the CAPTCHA image
        for idx, img in enumerate(images):
            img_src = img.get_attribute("src")
            if img_src and img_src.startswith("data:image/png;base64,"):
                print(
                    f"Found CAPTCHA image (Image {idx + 1}): {img_src[:30]}...")  # Display first 30 characters of Base64 string
                try:
                    # Extract and decode Base64 data
                    base64_data = img_src.split(",")[1]  # Get the Base64 part
                    image_data = base64.b64decode(base64_data)

                    # Convert the binary image data to a numpy array for OpenCV processing
                    nparr = np.frombuffer(image_data, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale

                    # Preprocess the image
                    image = cv2.medianBlur(image, 3)  # Denoise
                    _, image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Thresholding

                    # Use Tesseract to extract text
                    custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789'
                    captcha_text = pytesseract.image_to_string(image, config=custom_config)

                    # Print the extracted CAPTCHA text
                    print(f"Extracted CAPTCHA text: {captcha_text.strip()}")
                    break  # Stop after processing the CAPTCHA image
                except Exception as e:
                    print(f"Failed to process CAPTCHA image: {e}")
            else:
                print(f"Image {idx + 1} is not a CAPTCHA.")
finally:
    # Close the browser
    driver.quit()
