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

import os
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict

print(
    "SG3: This program reads and validates a species-abundance CSV, "
    "then outputs species list, dated data, presence/absence, and a heat map."
)

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

# --- Read and parse header for species names ---
header_line = f.readline().strip()
columns = header_line.split(",")
species_names = columns[1:]  # drop the date column

# Write species names to Species.txt
with open("Species.txt", "w") as species_file:
    for name in species_names:
        species_file.write(name + "\n")
print(f"Wrote {len(species_names)} species names to Species.txt")

# --- Read remaining lines to collect dates ---
dates = []
for line in f:
    line = line.strip()
    if not line:
        continue
    dates.append(line.split(",")[0])

# Write dates to DatedData.txt
with open("DatedData.txt", "w") as date_file:
    for d in dates:
        date_file.write(d + "\n")
print(f"Wrote {len(dates)} dates to DatedData.txt")

# --- Compute presence/absence vectors ---
presence_absence = []
with open(filename, 'r') as csv_file:
    next(csv_file)  # skip header
    for line in csv_file:
        parts = line.strip().split(",")[1:]
        vector = ['1' if int(val) > 0 else '0' for val in parts]
        presence_absence.append(vector)

with open("PresentAbsent.txt", "w") as pa_file:
    for vec in presence_absence:
        pa_file.write(",".join(vec) + "\n")
print(f"Wrote {len(presence_absence)} presence/absence records to PresentAbsent.txt")

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
    t1 = mn + span/3
    t2 = mn + 2*span/3
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
        print(line)
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
plt.title("Species Abundance Heat Map")
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


