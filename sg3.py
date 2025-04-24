"""
Language: Python 3
IDE: Thonny

Team Members:
  - Zach Brown
  - Khristian East
  - Anthony Burrows
  - Damion Daniels

Date Started: 2025-04-24
Class: CS4500 – Introduction to Software Profession

Program Description:
SG3 reads a species-abundance CSV file, validates its structure and contents,
and generates various outputs:
  • Species.txt       – list of species names
  • DatedData.txt     – list of dates
  • PresentAbsent.txt – presence/absence vectors
  • HeatMap.txt       – a heat-map representation
"""

print("SG3: This program reads and validates a species-abundance CSV, then outputs species list, dated data, presence/absence, and a heat map.")

import os

# --- Prompt until we get a .csv filename (any case) ---
while True:
    filename = input("Enter the name of the CSV file: ")
    if not filename.lower().endswith(".csv"):
        print("Error: filename must end with .csv (case-insensitive). Please try again.")
    else:
        break

# --- Prompt until we can open the file in the current directory ---
while True:
    try:
        f = open(filename, 'r')
        break
    except FileNotFoundError:
        print(f"Error: file '{filename}' not found in this directory.")
        filename = input("Enter the name of the CSV file: ")