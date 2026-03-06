import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import webbrowser #for the hyperlink
import sys
from dotenv import load_dotenv
import os
import shutil
import json

####SPLASH SCREEN ###
def show_splash_screen(callback):
    """Show a splash screen. Callback is no longer used - timing is handled externally."""
    from tkinter import font as font
    
    splash = tk.Toplevel()
    splash.title("Zoltun AI")
    splash.geometry("300x300")
    splash.resizable(False, False)
    
    # Center the splash screen
    splash.update_idletasks()
    width = splash.winfo_width()
    height = splash.winfo_height()
    x = (splash.winfo_screenwidth() // 2) - (width // 2)
    y = (splash.winfo_screenheight() // 2) - (height // 2)
    splash.geometry(f'{width}x{height}+{x}+{y}')
    
    # Remove window decorations for a clean look
    splash.overrideredirect(True)
    
    # Load and display the pre-processed image
    try:
        photo = tk.PhotoImage(file="zoltun_300.png")
        label = tk.Label(splash, image=photo)
        label.image = photo  # Keep reference to prevent garbage collection
        label.pack(fill='both', expand=True)
    except Exception as e:
        print(f"Could not load splash image: {e}")
        # Fallback: create a simple label if image fails to load
        label = tk.Label(splash, text="Zoltun AI", bg="purple", fg="white")
        label.pack(fill='both', expand=True)
    
    # Make the splash screen clickable to open zoltun.org
    def open_link(event):
        webbrowser.open("https://zoltun.org")
    label.bind("<Button-1>", open_link)
    
    # Note: Timing is now handled externally by root.after(3000, create_main_app)
    # The splash screen will be destroyed by create_main_app() after 3 seconds
    
    return splash
### END SPLASH SCREEN

## Deal with build temp problems
def extract_assets():
    # 1. Get the temporary PyInstaller extraction path
    source_dir = getattr(sys, '_MEIPASS', os.path.abspath('.'))

    # 2. List of specific files and folders we want to replicate
    # These match the names you put in 'append_pkgs' in the spec file
    #added files
    assets = ['theme', 'mdWidgetDone.py', 'settings.json','zoltun_300.png', 'zoltun.png', 'zoltun.ico', 'welcome.md', 'apiSplash.py']

    for item in assets:
        src_path = os.path.join(source_dir, item)
        dst_path = os.path.abspath(item) # Puts it in the folder where the EXE is running

        # Check if source exists inside the EXE
        if os.path.exists(src_path):
            # Skip if already exists to avoid overwriting user data accidentally
            if os.path.exists(dst_path):
                print(f"Skipping copy, '{item}' already exists.")
                continue

            try:
                if os.path.isdir(src_path):
                    # Copy folder recursively
                    shutil.copytree(src_path, dst_path)
                    print(f"Folder copied: {item}")
                else:
                    # Copy single file
                    shutil.copy2(src_path, dst_path)
                    print(f"File copied: {item}")
            except Exception as e:
                print(f"Failed to copy {item}: {e}")
        else:
            print(f"Warning: Could not find {item} in bundle.")

# Function to handle missing API key by prompting user and saving to .env file
#GEMINI REVISED
def noApiKey():
    # Hacky workaround - use temp hidden root for dialogs
    temp_root = tk.Tk()
    temp_root.withdraw()
    temp_root.update()  # Force update to minimize visual artifact

    messagebox.showinfo("Setup", "No API Key found. Please enter it to continue.")
    api_key = simpledialog.askstring("API Key", "Enter your Z.ai API key - no quotes:")
    
    if api_key:
        with open(".env", "w") as env_file: # "w" to ensure we create a clean file
            env_file.write(f'ZAI_API_KEY="{api_key}"')
        # Manually set it in the current process so we don't have to reload
        os.environ["ZAI_API_KEY"] = api_key
        temp_root.destroy()  # Clean up the temporary root
        return api_key
    else:
        messagebox.showerror("Error", "API key is required.")
        temp_root.destroy()  # Clean up the temporary root
        sys.exit()

#prob broken
def lighten(color, percentage): #lightens color by x% go with 30 for good result not used yet
    percent = 1 + (percentage/100)
    color = color[1:6]
    r = int(color[0:2],16)
    g = int(color[2:4],16)
    b = int(color[4:6],16)
    r = int(r * percent)
    if r > 255:
        r = 255
    g = int(g * percent)
    if g > 255:
        g = 255
    b = int(b * percent)
    if b > 255:
        b = 255
    r = hex(r)[2:]
    if len(r) < 2:
        r = '0' + r
    g = hex(g)[2:]
    if len(g) < 2:
        g = '0' + g
    b = hex(b)[2:]
    if len(b) < 2:
        b = '0' + b
    rgb = '#' + r + g + b
    print("RGB ", rgb)
    return rgb
## GET WORKS
def get_theme_files():
    """Scans the ./theme directory and returns a list of .json filenames."""
    theme_dir = os.path.join(os.getcwd(), "theme")
    
    # Check if directory exists, create it if it doesn't (for demonstration)
    if not os.path.exists(theme_dir):
        os.makedirs(theme_dir)
        # Create dummy files for testing so the code isn't empty
        with open(os.path.join(theme_dir, "dark_mode.json"), "w") as f:
            json.dump({"bg": "#333"}, f)
        with open(os.path.join(theme_dir, "light_mode.json"), "w") as f:
            json.dump({"bg": "#fff"}, f)
    # List all files, filter for .json extension
    files = [f for f in os.listdir(theme_dir) if f.endswith('.json')]
    #print(files)
    return files