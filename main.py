from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Function to get valid input with a default value
def get_input(prompt, default):
    user_input = input(prompt)
    if user_input.strip() == "":
        return default
    try:
        value = float(user_input)
        if value <= 0:
            raise ValueError("Value must be positive.")
        return value
    except ValueError as e:
        print(f"Invalid input: {e}. Using default value: {default}")
        return default

# Set default purchase interval
default_purchase_interval = 15  # Default interval between purchase attempts (in seconds)

# Prompt user for custom purchase interval
purchase_interval = get_input(f"Enter the interval between purchase attempts (default {default_purchase_interval} seconds): ", default_purchase_interval)

# Set the click interval for 50 CPS
click_interval = 1 / 50  # 0.02 seconds

# Set up the WebDriver
driver = webdriver.Chrome()

# Open the Cookie Clicker game
driver.get('https://orteil.dashnet.org/cookieclicker/')

# Wait for the page to load and the language selection to be available
try:
    lang_select_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="langSelect-EN"]'))
    )
    lang_select_button.click()
except Exception as e:
    print(f"Error selecting language: {e}")

# Wait for the game to load completely
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'bigCookie'))
    )
except Exception as e:
    print(f"Error loading the game: {e}")

# Locate the big cookie button
cookie = driver.find_element(By.ID, 'bigCookie')

# Accept cookies if the button is present
try:
    accept_cookies = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/a[1]'))
    )
    accept_cookies.click()
except Exception as e:
    print(f"Error accepting cookies: {e}")

# Function to get the number of cookies
def get_cookies():
    cookies = driver.find_element(By.ID, 'cookies').text.split()[0].replace(',', '')
    return int(cookies)

# Function to get the price of a building
def get_building_price(building):
    try:
        price = building.find_element(By.CSS_SELECTOR, '.price').text.replace(',', '')
        return int(price)
    except Exception as e:
        print(f"Error getting building price: {e}")
        return 0

# Function to buy the most cost-effective building or upgrade
def buy_items():
    try:
        # Find all available upgrades
        upgrades = driver.find_elements(By.CSS_SELECTOR, '.crate.upgrade.enabled')
        if upgrades:
            print("Buying upgrade...")
            upgrades[-1].click()  # Buy the most expensive upgrade
            return True

        # Get the list of unlocked and enabled buildings
        buildings = driver.find_elements(By.CSS_SELECTOR, '.product.unlocked.enabled')

        if not buildings:
            print("No buildings available for purchase.")
            return False

        # Extract building prices
        building_data = []
        for building in buildings:
            price = get_building_price(building)
            building_data.append((price, building))

        # Sort buildings by price in descending order (most expensive first)
        building_data.sort(key=lambda x: x[0], reverse=True)

        # Get current number of cookies
        cookies = get_cookies()

        # Buy the most expensive available building
        for price, building in building_data:
            if cookies >= price:
                print(f"Buying building with price {price}...")
                building.click()
                return True
        return False
    except Exception as e:
        print(f"Error buying items: {e}")
        return False

# Timing settings
last_purchase_time = time.time()

# Click the cookie in a loop
try:
    while True:
        start_time = time.time()
        # Click 50 times per second
        while time.time() - start_time < 1:
            cookie.click()
            time.sleep(click_interval)

        # Check for achievements and close them if they appear
        try:
            achievements = WebDriverWait(driver, 1).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.close'))
            )
            for achievement in achievements:
                achievement.click()
        except:
            pass  # No achievements to close

        # Check if enough time has passed since the last purchase
        if time.time() - last_purchase_time >= purchase_interval:
            if buy_items():
                print(f"Purchased an item, resetting purchase timer")
                last_purchase_time = time.time()  # Update the last purchase time

except KeyboardInterrupt:
    print("Stopping the script...")

# Close the WebDriver
driver.quit()
