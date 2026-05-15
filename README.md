# Hourly Trend Formatter

This tool takes a raw Trend Report CSV and organizes it into a consistent hourly list.

### What this tool does
* **Complete Months:** Creates a row for every hour from the 1st to the last day.
* **Gap Filling:** Sets missing values to '0' and marks reliability with '?'.
* **Time Rounding:** Rounds minutes to the nearest hour.
* **Dual Output:** Generates both CSV and Excel versions of the report.

---

### Setup Instructions

1.  **Install Python:** Download from python.org. Ensure "Add Python to PATH" is checked.
2.  **Install Libraries:** Run this command in your terminal:
    pip install pandas openpyxl

---

### How to use the tool

1.  Place your raw CSV in the same folder as 'Formatter.py'.
2.  Run 'Formatter.py'.
3.  Type the name of your file (e.g., report.csv) and press Enter.
4.  Find your output: Two new files will appear, named by the month and time (e.g., May_Report_20260515_1430).
5.  Press Enter to close the window when finished.
