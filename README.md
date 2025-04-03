# Geospatial Store Locator

## Overview
This application allows you to find the nearest stores to a given location by entering latitude and longitude coordinates. The app will display the results on an interactive map and in a sortable table, which can also be exported as a CSV file.

## Requirements
- Windows PC
- Internet connection
- Python 3.7 or higher (installation guide below)

## Installation Instructions

### Step 1: Install Python
1. Download Python from the official website: https://www.python.org/downloads/windows/
2. Click on the latest Python release (e.g., "Python 3.10.x")
3. Scroll down and click on "Windows installer (64-bit)" to download
4. Run the downloaded file
5. **IMPORTANT**: Check the box that says "Add Python to PATH" before clicking "Install Now"
6. Click "Install Now" and wait for the installation to complete
7. Click "Close" when finished

### Step 2: Install Required Packages
1. Open Command Prompt:
   - Press the Windows key
   - Type "cmd" and press Enter
2. Install the required packages by copying and pasting this command:
   ```
   pip install flask pandas numpy scikit-learn
   ```
3. Press Enter and wait for installation to complete

### Step 3: Prepare Your Data File
1. Make sure you have a file named `geocoded_stores_complete.csv` with store information
2. This file should contain columns for `latitude`, `longitude`, `Store_Num`, `Account_Name`, `Address`, `City`, `State`, and `Zip`
3. Create a folder named "Data" (with a capital D) in the same location as the app.py file
4. Place your `geocoded_stores_complete.csv` file in the "Data" folder

## Running the Application

### Step 1: Start the Server
1. Open Command Prompt:
   - Press the Windows key
   - Type "cmd" and press Enter
2. Navigate to the folder where you extracted the zip file:
   - Type `cd path\to\folder` (replace "path\to\folder" with the actual path)
   - For example: `cd C:\Users\YourName\Downloads\StoreLocator`
3. Start the application by typing:
   ```
   python app.py
   ```
4. You'll see a message saying "Running on http://127.0.0.1:5000/" (or similar)

### Step 2: Access the Application
1. Open your web browser (Chrome, Edge, Firefox, etc.)
2. Type `http://127.0.0.1:5000/` in the address bar and press Enter
3. The Store Locator application should now appear in your browser

## Using the Application

### Finding Nearby Stores
1. Enter the latitude and longitude coordinates (default values are provided)
   - If you need to find coordinates for a location:
     - Go to Google Maps (https://www.google.com/maps)
     - Right-click on a location
     - Select "What's here?"
     - The coordinates will appear at the bottom of the screen
2. Enter the number of stores you want to find (default is 10)
3. Click the "Find Nearest Stores" button

### Viewing Results
1. The results will display on an interactive map
   - Blue markers represent store locations
   - You can click on a marker to see store details
   - You can zoom in/out using the + and - buttons
2. Below the map, a table shows detailed information about each store
   - Click on any column header to sort the table by that column
3. To download the results as a CSV file:
   - Click the "Download as CSV" button
   - The file will be saved to your computer's default download location
4. To search for different coordinates, click the "Search Again" button

## Troubleshooting

### If the application doesn't start:
1. Make sure Python is installed correctly:
   - Open Command Prompt and type `python --version`
   - You should see a version number (like "Python 3.10.x")
2. Make sure all required packages are installed:
   - Open Command Prompt and type `pip list`
   - Check that flask, pandas, numpy, and scikit-learn are listed
3. Check that your data file is in the correct location:
   - It should be in a folder named "Data" in the same directory as app.py
   - The file should be named "geocoded_stores_complete.csv"

### If you see an error message in the application:
1. Read the error message carefully, it may provide specific information about what went wrong
2. Check that your data file contains all required columns
3. Make sure the coordinates you entered are valid

## Support
If you continue to experience issues with the application, please contact [Your Name/Support Email] for assistance.
