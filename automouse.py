import pyautogui
import random
import time

# Function to move the mouse to random positions
def move_mouse_randomly():
    # Generate random coordinates and duration
    x = random.randint(0, 1920)
    y = random.randint(0, 1080)
    duration = random.uniform(0.5, 2.0)
    
    # Move the mouse to the random position
    pyautogui.moveTo(x, y, duration=duration)

# Run the mouse movement for 1 hour
end_time = time.time() + 60 * 60  # 60 minutes * 60 seconds
while time.time() < end_time:
    move_mouse_randomly()
    time.sleep(random.uniform(1, 5))  # Wait for a random time between movements