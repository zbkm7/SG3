"""
Language: Python 3
IDE: Thonny
Created by: Zach Brown, Diamon Daniels

Build & Execution:
  1. I ensured Python 3 was installed.
  2. In a terminal, I installed dependencies:
       pip install matplotlib
  3. I then cloned the SG3 repository and change into its folder:
       git clone https://github.com/zbkm7/SG3.git
       cd SG3
  4. I place my CSV in the SG3 folder, then ran:
       python sg3.py
  
Team Members:
  - Zach Brown (Programmer)
  - Khristian East
  - Anthony Burrows
  - Diamon Daniels (programmer)

Date Started: 2025-04-23
Date Submitted: 2025-05-29
Class: CS4500 – Introduction to Software Profession

Program Description:
  SG3 ingests a species-abundance CSV, validates its structure,
  and produces these outputs:
    • Species.txt       – newline list of species names
    • DatedData.txt     – newline list of date strings
    • PresentAbsent.txt – CSV of presence (1)/absence (0) per species
    • HeatMap.txt       – ASCII L/M/H map per date
    • HeatMap.png       – graphical heat map colored by abundance
  Then it reports any dates or species sharing identical L/M/H patterns,
  and finally waits for the user to press ENTER before exiting.

Central Data Structures:
  • species_names      – list[str] of column headers (species)
  • dates              – list[str] of date strings from file
  • presence_absence   – list[list[str]] of '1'/'0' per species per date
  • abundance_matrix   – list[list[float]] raw counts per species per date
  • thresholds         – list[tuple[float,float]] low/med cutoffs per species
  • date_groups        – dict mapping L/M/H tuples to lists of dates
  • species_groups     – dict mapping L/M/H tuples to lists of species

External Files:
  Input:
    • validfile.csv     – comma-first-field date, then numeric abundance columns
  Outputs:
    • Species.txt, DatedData.txt, PresentAbsent.txt,
      HeatMap.txt, HeatMap.png

External Resources (Sources):
**I got most of the code from our Previous Projects!**

matplotlib pyplot (https://matplotlib.org/stable/api/_as_gen/matplotlib.colors.LinearSegmentedColormap.html):
     - For plotting 2D matrix heat map.
LinearSegmentedColormap (https://matplotlib.org/stable/index.html):
     - I figured out how to create custom yellow→orange→red gradients.
defaultdict grouping (docs.python.org/3/library/collections.html#collections.defaultdict):
     - I learned how grouping keys worked to lists without key-existence checks.
Python packaging (pip.pypa.io):
     - Ensuring matplotlib installation.


"""

import csv
import os
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict

# Entry message to user
print(
    "SG3: This program reads and validates a species-abundance CSV, "
    "then outputs species list, dated data, presence/absence, and a heat map."
)
input('Press ENTER to continue')

def validate_file_dates(csv_dates): #ensure all dates are valid; csv_dates- list of lists where first element is a date
    for i in range(1, len(csv_dates)):
        date_value = csv_dates[i][0].split("/") #split into list of month, day, year
        date_value = is_invalid_date(date_value) 
        if date_value:
            input(f"error: {csv_dates[i][0]} in line {i} is an illegel date. Reason: invalid {date_value}\nPress ENTER to exit program")
            exit()
    return

def is_invalid_date(date_value): #date_value is a list of strings in [MM, DD, YYYY]
    if len(date_value[2]) != 4: #make sure year is 4 characters long
        return "year"
    month = int(date_value[0])
    day = int(date_value[1])
    year = int(date_value[2])
    day_ranges = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if year % 4 == 0: #exception for February
        if year % 100 != 0 or year % 400 == 0: #if leap year
            day_ranges[2] = 29
    if not (month > 0 and month <= 12): # if month is invalid
        return "month"
    elif not (day > 0 and day <= day_ranges[month]):  #if the day does not exist in current month
        return "day"
    return "" #return empty string if date is valid

def validate_numbers(csv_list, N): #ensure all numbers in list are valid; csv_list is a list of csv data stored in a list, N is an integer representing how many numbers should be in each line
    for num in csv_list:
        if len(num[1:]) != N: #if the amount of numbers in the line if not the same as the number of names in the header
            input(f"error: {num[1:]} in line {csv_list.index(num) + 1} is illegal. Reason: wrong amount of numbers ({len(num[1:])} numbers). There should be {N} numbers per line\nPress ENTER to terminate program") #https://www.geeksforgeeks.org/python-list-index/
            exit()
        else:
            for val in num[1:]:
                if not is_number_valid(val):
                    input(f"error: {val} in line {csv_list.index(num) + 1} is illegal. Reason: negative numbers are not allowed for an abundance count\nPress ENTER to terminate program")
                    exit()

def is_number_valid(val): #validate single number string; val is the number to be tested; returns boolean value of whether the given string passes all validity tests
    try:
        return float(val) >= 0 and val[0] != '.' #only returns true if val is a number, positive, and correctly formatted
    except ValueError: #if float() fails
        return False
    
def find_duplicate_pa(dict_list):
    # Dictionary to store Present/Absent patterns and their dates
    pa_tracker = {}
    
    # add all Present/Absent values and their date to pattern_tracker
    for entry in dict_list:
        pa = tuple(entry['Present/Absent']) # Convert the list to tuple so it can be used as a dict key
        date = entry['Date']
        
        if pa in pa_tracker: # if the Present/Absent value is a key in the dict already add the date
            pa_tracker[pa].append(date)
        else: # otherwise start a new list with that Present/Absent value as the key and add date as a new list
            pa_tracker[pa] = [date]

    # find any Present/Absent values that have more than one date connected to them
    duplicates = {
        pa: dates 
        for pa, dates in pa_tracker.items() 
        if len(dates) > 1
    }  
    # store results back into a list of dicts
    result = []
    for pa, dates in duplicates.items():
        result.append({
            'PA': list(pa),  # Convert tuple back to list for output
            'Dates': dates,
            'Occurrences': len(dates)
        })
    
    return result

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

dates = []
presence_absence = []
header = []

with open(filename, mode='r') as file:
    csv_file = csv.reader(file)
    csv_list = list(csv_file)
    validate_file_dates(csv_list) #validate dates
    header = csv_list[0]
    validate_numbers(csv_list[1:], len(header) - 1) #validate the numbers in the list
    dates = [row[0] for row in csv_list[1:]] #store first column from each row
header.pop(0) #remove blank cell

#display summary of species and dates and wait for 
species_count = len(header)
date_count = len(dates)
print(f"{species_count} species and {date_count} dates were found in this file.")
input("Press ENTER to continue")

# --- Read and parse header for species names ---
header_line = f.readline().strip()
columns = header_line.split(",")
species_names = columns[1:]  # drop the date column

# Write species names to Species.txt
with open("Species.txt", "w") as species_file:
        species_file.write('\n'.join(header))
print(f"Wrote {len(species_names)} species names to Species.txt")

# Write dates to DatedData.txt
with open("DatedData.txt", "w") as date_file:
    date_file.write('\n'.join(dates))
print(f"Wrote {len(dates)} dates to DatedData.txt")


# --- Compute presence/absence vectors ---
with open('PresentAbsent.txt', mode='w') as pa_file:
    with open(filename, mode ='r') as in_file:
        csv_file = csv.reader(in_file)
        header = next(csv_file) #skip header row
        pa_file.write(','.join(header) + '\n') #write header to 'PresentAbsent.txt'
        
        #processing each data row
        for row in csv_file:
        #convert numbers to 1 or 0- 1 if >0, 0 if 0
            vector = ['1' if float(val) > 0 else '0' for val in row[1:]]
            vector.insert(0, row[0])
            pa_file.write(','.join(vector) + '\n')
            presence_absence.append({'Date': vector[0], 'Present/Absent': vector[1:]})
print(f"Wrote {len(presence_absence)} presence/absence records to PresentAbsent.txt")

#find max abundance measured on a date and all species with same abundance count
with open(filename, mode = 'r') as f:
    csv_file = csv.reader(f)
    next(csv_file)
    for row in csv_file:
        numbers = []
        for s in row[1:]: 
            numbers.append(float(s)) #change abundance counts to float and append them to numbers
        max_abundance = max(numbers)
        indexes = [] 
        for i, num in enumerate(numbers): #add all indexes of species that match the max_abundance amount
            if num == max_abundance:
                indexes.append(i)

        species_with_max = ', '.join([header[i+1] for i in indexes]) #create a string with all species of the same max abundance count
        print(f"Date: {row[0]}, Max abundance: {max_abundance:g}, Species: {species_with_max}") #print required message with date abundance count and species

duplicates = find_duplicate_pa(presence_absence)
for duplicate in duplicates: #print any duplicates found
    print(f"{duplicate['PA']} appears {duplicate['Occurrences']} times on these dates: {[date for date in duplicate['Dates']]}")

# --- Build abundance_matrix for heat map ---
abundance_matrix = []
with open(filename, 'r') as csv_file:
    next(csv_file)
    for line in csv_file:
        parts = line.strip().split(",")[1:]
        row_counts = [float(x) for x in parts]
        abundance_matrix.append(row_counts)

# --- Compute H/M/L thresholds once ---
species_mins = [min(col) for col in zip(*abundance_matrix)]
species_maxs = [max(col) for col in zip(*abundance_matrix)]
thresholds = []
for mn, mx in zip(species_mins, species_maxs):
    span = mx - mn
    t1 = mn + span/3  # 1/3 cutoff
    t2 = mn + 2*span/3  # 2/3 cutoff
    thresholds.append((t1, t2))

# --- Write ASCII heat map to HeatMap.txt ---
with open("HeatMap.txt", "w") as hm_file:
    for date, row in zip(dates, abundance_matrix):
        codes = []
        for val, (t1, t2) in zip(row, thresholds):
            if val <= t1:
                codes.append("L")
            elif val <= t2:
                codes.append("M")
            else:
                codes.append("H")
        line = date + "," + ",".join(codes)
        print(line)              # echo to console
        hm_file.write(line + "\n")
print("Wrote ASCII heat map to HeatMap.txt")

# --- Find dates sharing identical H/M/L patterns ---
date_groups = defaultdict(list)
for date, row in zip(dates, abundance_matrix):
    pattern = tuple(
        "L" if val <= t1 else "M" if val <= t2 else "H"
        for val, (t1, t2) in zip(row, thresholds)
    )
    date_groups[pattern].append(date)

found_dates = False
for pattern, ds in date_groups.items():
    if len(ds) > 1:
        found_dates = True
        pat_str = ",".join(pattern)
        print(f"Dates {', '.join(ds)} share the H/M/L pattern: {pat_str}")
if not found_dates:
    print("No dates share exactly the same H/M/L values for all species.")

# --- Generate graphical heat map with custom cmap ---
cmap = LinearSegmentedColormap.from_list("yo_red", ["yellow", "orange", "red"])
plt.figure()
plt.imshow(abundance_matrix, aspect='auto', cmap=cmap)
plt.colorbar(label='Abundance')
plt.xticks(range(len(species_names)), species_names, rotation=45, ha='right')
plt.yticks(range(len(dates)), dates)
plt.title('Species Abundance Heat Map')
plt.tight_layout()
plt.savefig("HeatMap.png")
plt.show()

# --- Find species sharing identical H/M/L patterns ---
species_groups = defaultdict(list)
for idx, name in enumerate(species_names):
    pattern = tuple(
        "L" if row[idx] <= thresholds[idx][0]
        else "M" if row[idx] <= thresholds[idx][1]
        else "H"
        for row in abundance_matrix
    )
    species_groups[pattern].append(name)

found_species = False
for pattern, names in species_groups.items():
    if len(names) > 1:
        found_species = True
        pat_str = ",".join(pattern)
        print(f"Species {', '.join(names)} share the H/M/L pattern: {pat_str}")
if not found_species:
    print("No species share exactly the same H/M/L values for all dates.")

# --- Polite exit ---
input("All done! Press ENTER to finish the program.")
