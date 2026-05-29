# User Guide: Hourly Trend Formatter

This tool automates the cleaning of raw Metasys Trend Reports. It takes inconsistent data, fixes time gaps, calculates a total sum for the month, and outputs clean files ready for analysis.

## Step 1: One-Time Preparation
Before running the tool for the very first time, you need to set up Python on your computer. You only ever have to do this once.

1. **Download Python:** Go to [python.org](https://www.python.org/) and download the latest version for Windows.
2. **Install Python:** Run the downloaded installer file. 
   * **CRITICAL:** On the very first installation screen, check the box at the bottom that says **"Add Python to PATH"** before clicking install. If you skip this, the tool will not work.
3. **Install Core Libraries:**
   * Search for **"cmd"** or **"Command Prompt"** in your Windows start menu and open it.
   * Type this exact line into the black box and press **Enter**:
     ```bash
     pip install pandas openpyxl
     ```
   * Close the black box once it finishes loading.

---

## Step 2: How to Run the Report Tool
Follow these steps every time you have a new report file to format.

1. **Move Your File:** Put your raw, unedited trend report (`.csv`) into the **exact same folder** where the script file (`Formatter.py`) is located.
2. **Open the Tool:** Right-click `Formatter.py` and select **"Run with Python"** (or simply double-click it).
3. **Enter the Filename:** A black window will open asking for the file name. Type the full name of your file exactly as it appears in your folder, including the `.csv` extension, and press **Enter**.
   * *Example:* `Trend Report_05_27_2026.csv`
4. **Wait for Success:** The screen will display a processing message. Within a few seconds, you will see a success confirmation text message.
5. **Close Safely:** Press **Enter** on your keyboard to close the window.

---

## Step 3: Finding and Reading Your Results
The tool will automatically generate two brand-new files in that same folder, customized by the data's specific calendar month and the current timestamp:
* **The CSV File:** Named like `January_Report_20260529_1330`
* **The Excel File:** Named like `January_Report_20260529_1330` (with an Excel grid icon)

### Rules Applied to Your Clean Data:
* **Perfect Timelines:** Every hour of the month is mapped continuously (from the 1st day at 00:00 to the last day at 23:00).
* **Missing Gaps Fixed:** If a field meter dropped offline and missed an hour, the tool automatically inserts a `0` value and flags it with a `?` in the Reliability column.
* **Automatic Summary:** Scroll to the absolute bottom row of the generated worksheet to see the automated **"Total Sum"** calculated instantly for each data category.

---

## Troubleshooting Common Mistakes

* **Error: "Could not find a file named..."**
  This means there is a typo in what was entered, or the raw file isn't sitting in the exact same folder as the script. Double-check the spelling and folder placement.
* **The black window flashes and vanishes instantly:**
  This happens if a system library is missing. Make sure you successfully ran the command `pip install pandas openpyxl` inside your Command Prompt as shown in Step 1.