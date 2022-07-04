import cv2
import pytesseract
from pynput.keyboard import Listener, Key
from PIL import ImageGrab
import pyautogui as pya
import requests
from bs4 import BeautifulSoup
import string
import re
import random


non_alpha = string.punctuation + string.digits
nonalpha_regex = re.compile('[^a-zA-Z]')

def remove_non_alpha(text: str) -> str:
    return nonalpha_regex.sub("", text)

def contains_non_alpha(text) -> bool:
    for char_ in non_alpha:
        if char_ in text:
            return True
    return False
    
def on_release(key: Key):
    try: 
        if key == Key.f2:
            return False # stop listener
    except Exception:
        pass

def main():
    used_words = []
    while True:
        with Listener(on_release=on_release) as listener:
            listener.join() # wait until key is pressed
        img = ImageGrab.grab(bbox=(740, 500, 850, 630))
        img.save("screenshot.png")
        screenshot = cv2.imread("screenshot.png")

        # change all pixels to white and the text to black 
        height, width, _ = screenshot.shape

        for i in range(height):
            for j in range(width):
                # img[i, j] is the RGB pixel at position (i, j)
                # check if it's [0, 0, 0] and replace with [255, 255, 255] if so
                if screenshot[i, j].sum() >= 255*3-80:
                    screenshot[i, j] = [0, 0, 0]
                else:
                    screenshot[i, j] = [255, 255, 255]

        cv2.imwrite("edited.png", screenshot)
        text = pytesseract.pytesseract.image_to_string(screenshot, lang="eng")
        lower = remove_non_alpha(text.lower())
        if contains_non_alpha(lower):
            while True:
                text = pytesseract.pytesseract.image_to_string(screenshot, lang="eng")
                if not contains_non_alpha(text):
                    break
            lower = remove_non_alpha(text.lower())
        print(f"'{lower}'")
        url = f"https://www.thefreedictionary.com/words-containing-{lower}"
        print(f"sending request to {url}")

        request_ = requests.get(url)
        if not request_.ok:
            print("error response")
            continue
        
        html = request_.text
        soup = BeautifulSoup(html, "lxml")
        lists = soup.find_all("li", {"data-f": "11"})
        links = []
        for list_ in lists[0:20]:
            links.append(list_.find("a"))
        
        words = []
        for link in links:
            words.append(link['href'])

        random_word = random.choice(words)
        while random_word in used_words and not contains_non_alpha(random_word):
            random_word = random.choice(words)
        used_words.append(random_word)

        print(random_word)
        pya.write(random_word, 0.01)
        pya.press("enter")


if __name__ == "__main__":
    main()