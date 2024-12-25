import os
import base64
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
import pytesseract

# ======== Configuration ========
CHROME_DRIVER_PATH = r"C:\Users\payam\Desktop\chromedriver-win64\chromedriver.exe"  # Path to ChromeDriver
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Path to Tesseract-OCR executable
TARGET_URL = "https://bbimobile.ephoenix.ir/auth/login"  # URL to open
REFRESH_DELAY = 5  # Seconds to wait after refreshing the page
DOWNLOAD_FOLDER = "downloaded_images"  # Folder to save CAPTCHA images
# =================================

# Ensure the download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Initialize Selenium WebDriver
service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service)


def preprocess_and_save(image_path, output_path="high_res_cleaned_captcha.png"):
    # Step 1: Read the image
    original_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Step 2: Denoise the image using Gaussian Blur
    denoised_image = cv2.GaussianBlur(original_image, (3, 3), 0)

    # Step 3: Upscale the image to higher resolution
    high_res_image = cv2.resize(denoised_image, None, fx=10, fy=10, interpolation=cv2.INTER_CUBIC)

    # Step 4: Thresholding to make the background white and numbers black
    _, binary_image = cv2.threshold(high_res_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Step 5: Ensure the background is completely white and numbers are black
    inverted_image = cv2.bitwise_not(binary_image)

    # Step 6: Morphological operations to clean up small artifacts
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned_image = cv2.morphologyEx(inverted_image, cv2.MORPH_CLOSE, kernel)

    # Save the final high-resolution cleaned image
    cv2.imwrite(output_path, cleaned_image)

    # Return the intermediate steps for analysis (optional)
    return


def read_captcha(image_path):
    """Read the CAPTCHA from the saved image."""
    # Specify the path to Tesseract-OCR executable
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    # Read the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Simple preprocessing: Apply binary thresholding
    image = cv2.medianBlur(image, 3)  # Remove noise
    _, image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Thresholding

    # Recognize text with Tesseract
    config = "--psm 6 -c tessedit_char_whitelist=0123456789"
    result = pytesseract.image_to_string(image, config=config)

    # Clean the result
    result = result.strip()

    return result


def save_captcha_image(img_src, index):
    """Save the CAPTCHA image as a file and read its text."""
    try:
        # Decode Base64 CAPTCHA
        base64_data = img_src.split(",")[1]
        image_data = base64.b64decode(base64_data)

        # Save the binary data as an image
        file_path = os.path.join(DOWNLOAD_FOLDER, f"captcha_{index + 1}.png")
        with open(file_path, "wb") as f:
            f.write(image_data)
        print(f"CAPTCHA image saved at: {file_path}")

        # Read the CAPTCHA text
        captcha_text = read_captcha(file_path)
        print(f"CAPTCHA text: {captcha_text}")

    except Exception as e:
        print(f"Error saving CAPTCHA image: {e}")


try:
    print(f"Opening URL: {TARGET_URL}")
    driver.get(TARGET_URL)
    sleep(REFRESH_DELAY)  # Wait for the page to load

    captcha_found = False

    while not captcha_found:
        print("Checking for CAPTCHA image...")
        images = driver.find_elements(By.TAG_NAME, "img")  # Find all <img> elements

        for idx, img in enumerate(images):
            img_src = img.get_attribute("src")
            if img_src and img_src.startswith("data:image/png;base64,"):  # Check for CAPTCHA
                print(f"Found CAPTCHA image (Image {idx + 1}): {img_src[:30]}...")
                save_captcha_image(img_src, idx)  # Save the CAPTCHA image
                captcha_found = True
                break  # Stop once CAPTCHA is processed
            else:
                print(f"Image {idx + 1} is not a CAPTCHA.")

        if not captcha_found:
            print("CAPTCHA not found, refreshing the page...")
            driver.refresh()
            sleep(REFRESH_DELAY)  # Wait after refreshing

    print("CAPTCHA image saved successfully. Browser tab remains open for further actions.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Keep the browser open for further manual actions
    print("Browser tab will remain open for further inspection.")
