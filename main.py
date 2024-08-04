import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# User configuration
def get_user_input(prompt, default_value):
    user_input = input(prompt)
    return float(user_input) if user_input else default_value

click_interval = get_user_input("Enter the click interval in seconds (default 50 CPS): ", 0.02)
purchase_interval = get_user_input("Enter the purchase interval in seconds (default 15): ", 15)

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
def accept_cookies():
    try:
        accept_cookies_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/a[1]'))
        )
        accept_cookies_button.click()
    except Exception as e:
        print(f"Error accepting cookies: {e}")

accept_cookies()

# Function to get the number of cookies
def get_cookies():
    cookies_text = driver.find_element(By.ID, 'cookies').text.split()[0].replace(',', '')
    return int(cookies_text)

# Function to get the price of a building
def get_building_price(building):
    try:
        price_text = building.find_element(By.CSS_SELECTOR, '.price').text.replace(',', '')
        return int(price_text)
    except Exception as e:
        print(f"Error getting building price: {e}")
        return 0

# Function to buy the most expensive building or upgrade
def buy_items():
    try:
        # Find all available upgrades
        upgrades = driver.find_elements(By.CSS_SELECTOR, '.crate.upgrade.enabled')
        if upgrades:
            print("Buying upgrade...")
            upgrades[-1].click()
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

        # Click the cookie
        cookie.click()

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
                print("Purchased an item, resetting purchase timer")
                last_purchase_time = time.time()

        # Ensure the click interval is maintained
        elapsed_time = time.time() - start_time
        if elapsed_time < click_interval:
            time.sleep(click_interval - elapsed_time)

except KeyboardInterrupt:
    print("Stopping the script...")

# Close the WebDriver
driver.quit()
