# CLASS_SN B1

# Project Specification: CSV Data Analyzer
# Your script must:
# 1. Accept a CSV filename as a command-line argument (or ask the user if none provided)
# 2. Read the CSV file using the csv module or pandas
# 3. Automatically detect which columns contain numeric data
# 4. For each numeric column, calculate: count, sum, mean, minimum, maximum
# 5. For non-numeric columns, show: count and number of unique values
# 6. Handle errors gracefully: file not found, empty file, no numeric columns
# 7. Print a clearly formatted summary table in the terminal
# 8. BONUS: Accept --output flag to save results as JSON

"""
CSV Data Analyzer — Mini Project 1
Reads a CSV file and prints statistical summaries for each column.
"""
import csv
import sys
import math as m
from pathlib import Path


def read_csv(filename):
    """Read a CSV file and return a list of dictionaries (one per row)."""
    try:
        with open(filename,"r") as file:
            reader = csv.DictReader(file) # uses the csv.reader to read the file
            data = list(reader) # stores this as a list called data which will be returned

            if not data:
                raise ValueError 
            
            return data  # failure to include this will result in an error during the formatting stage
    except FileNotFoundError:  # Raise FileNotFoundError if the file does not exist
        raise  FileNotFoundError
    except ValueError:   # Raise ValueError if the file is empty
        raise ValueError
        
    
    

def detect_numeric(data):
    """Return a list of column names where all values are numbers."""
    numerics = []
    #cols = data[0].keys
    for cols in data[0]:
        try:
            for rows in data:
                float(rows[cols])
            numerics.append(cols)
        except ValueError:
                continue
    #print("It is numeric")
    return numerics

def calculate_stats(values):
    """Return a dict with count, sum, mean, min, max."""
    count = len(values)
    total = sum(values)
    mean = total / count
    minimum = min(values)
    maximum = max(values)
    
    return {
        "count": count,
        "sum": total,
        "mean": mean,
        "min": minimum,
        "max": maximum
     }
# data = [34,64,64,757,24,24]
# print(calculate_stats(data))


def format_report(data, filename, numerics):
    """Print the formatted analysis report."""
    print("="* 40)
    print("CSV ANALYSIS REPORT")
    print("="*40)
    print(f"""file: {filename}
    Total rows: {len(data)}
    Total columns: {len(data[0])}""")
    print("NUMERIC COLUMNS:")
    print("-" * 40)

    # we have to iterate here
    for col in numerics: # this runs through each col in the numerics list
        values = []
        for row in data:
            values.append(float(row[col]))
        calculations = calculate_stats(values)
    print(f""" Column: {col}
          count: {round(calculations["count"],2)}
          sum  : {round(calculations["sum"],2)}
          mean : {round(calculations["mean"],2)}
          min  : {round(calculations["min"],2)}
          max  : {round(calculations["max"],2)}
""")
    
    print("NON NUMERIC COLUMNS:")
    print()
    for col in data[0]:
        if col not in  numerics: # this runs through each col in the numerics list
            # values = []
            # for row in data:
            #     values.append(row[col])
            values = [row[col] for row in data]
            unique_values = len(set(values))
            print(f"Column: {col} -- {len(values)} values, {unique_values} unique")

    print("-" * 40)
    print("=" * 40)

    #print header, numeric column stats, non-numeric summary
    

def main():
    # Get filename from command line or ask the user
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Enter CSV filename: ").strip()

        project_root = Path(__file__).parent.parent

        filename = project_root / "data" / filename
    try:
        data = read_csv(filename)
        numerics = detect_numeric(data)
        format_report(data, filename,numerics)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: file {e} is empty")
        sys.exit(1)

if __name__ == "__main__":
    main()

# use thisdata.csv  to check for another csv file
# use data.csv which is an empty file
# use emp.csv does not exist