from PIL import Image
import pytesseract
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')

def get_total_amount(img):
    """
    Using OCR, gets the total amount from a receipt image
    returns None if no total amount is found
    """
    img = np.array(img)
    text = pytesseract.image_to_string(img)
    text = text.upper()
    total_arr = text.split("TOTAL")
    try:
        for i in reversed(range(len(total_arr))):
            # logic to get the total amount
            # finds the last word total with number coming after it
            # For each value after the word total, check if it is a number by
            # attemping to remove the first character that is not a nunber (ex: $)
            # Then remove all the commas, values after \n, whitespaces around it, and one period to get raw number
            # If that raw number is a digit, then that is the total
            if not total_arr[i].strip()[0].isdigit():
                total_arr[i] = total_arr[i].strip()[1:]
            if total_arr[i].replace(",","").split("\n")[0].strip().replace('.','',1).isdigit():
                total = total_arr[i].replace(",","").split("\n")[0].strip()
                break
        total = float(total)
    except ValueError:
        total = None
    return total

if __name__ == '__main__':
    directory = os.fsencode('test/receipts')
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img = Image.open('test/receipts/' + filename)
            print(get_total_amount(img))
    

