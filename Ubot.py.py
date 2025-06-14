import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import tkinter as tk
from tkinter import messagebox
import re

# Replace this with your actual API key
API_KEY = "AIzaSyCUOvyeCrN3jQTvR8zucgLyE5kO5fZcRjk"

def get_video_duration(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={video_id}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if not data["items"]:
        return 15  # fallback duration

    duration_str = data["items"][0]["contentDetails"]["duration"]

    # Convert ISO 8601 duration (e.g., PT30S, PT1M5S) to seconds
    duration = 0
    match = re.match(r"PT(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if match:
        minutes = int(match.group(1) or 0)
        seconds = int(match.group(2) or 0)
        duration = minutes * 60 + seconds

    return duration

def get_video_id_from_url(url):
    if "shorts/" in url:
        return url.split("shorts/")[1].split("?")[0].split("/")[0]
    return None

def skip_ads(driver):
    try:
        skip_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Skip Ad')]")
        if skip_button.is_displayed():
            skip_button.click()
            print("▶️ Skipped ad.")
            time.sleep(2)
    except:
        pass

def skip_sponsored_content(driver):
    try:
        sponsored_label = driver.find_elements(By.XPATH, "//span[contains(text(), 'Sponsored')]")
        if sponsored_label:
            print("📢 Detected sponsored content, skipping...")
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ARROW_DOWN)
            time.sleep(1)
    except Exception as e:
        print(f"Error checking for sponsored content: {e}")

def ask_to_continue_popup():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    result = messagebox.askyesno("Continue Watching?", "Do you want to continue watching more Shorts?")
    root.destroy()
    return result

def auto_scroll_shorts():
    options = webdriver.ChromeOptions()
    # You can remove headless and allow it to show browser window
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1200,800")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.youtube.com/shorts")
    time.sleep(3)

    video_counter = 0

    try:
        while True:
            current_url = driver.current_url
            video_id = get_video_id_from_url(current_url)
            print("🎬 Watching video ID:", video_id)

            if video_id:
                duration = get_video_duration(video_id)
                print(f"⏱️ Duration: {duration} seconds")
                time.sleep(duration)
            else:
                print("❌ Could not extract video ID")
                time.sleep(10)

            skip_ads(driver)
            skip_sponsored_content(driver)

            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ARROW_DOWN)
            time.sleep(1)

            video_counter += 1

            if video_counter % 5 == 0:
                continue_watching = ask_to_continue_popup()
                if not continue_watching:
                    print("🛑 Stopping video watching...")
                    break

    except Exception as e:
        print(f"❗ Error occurred: {e}")
    finally:
        driver.quit()

# Run the bot
auto_scroll_shorts()
