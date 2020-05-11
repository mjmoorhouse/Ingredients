"""
listCSV.py
A very simple initial commit to test git connection.
List all the CSV files in the directory -printing the CWD on the way past.

Also tests the Pandas dependencies in a function and restructured to have a main(): function:
"""

#Test Pandas Dependencies:
import sys


def main():
    import os
    # 'Hide' the Pandas loading in a function; returns 1 on failure
    if loadPandasDeps():
        sys.exit("Could not load everything needed")
    else:
        print("Pandas dependencies Loaded (3 of) good")

    #Do file work:
    print("Current WD: '{}'".format(os.getcwd()))
    # Assume the path to the Data files is in the directory named "./Data"
    dataLocation = os.getcwd() + "\\Data"
    print("Location of data files: {}".format(dataLocation))

    # Use a list comprehension to get all the CSV - hence Data - files, then count them:
    CSVList = [x for x in os.listdir(dataLocation) if x.endswith(".csv")]
    N_CSVFiles = len(CSVList)
    if N_CSVFiles > 0:
        print("Are [{0}] Files: {1}".format(len(CSVList), CSVList))
    else:
        print("No CSV Files found")

    # Do something more interesting - or at least pretend to:
    for CFile in range(0, N_CSVFiles):
        CFile_Name = CSVList[CFile]
        print("Processing #{0} of {1}\t: '{2}':".format(CFile + 1, N_CSVFiles, CFile_Name))

def loadPandasDeps():
    # Load the 3 general dependencies for Pandas:
    # Return non-None on failure
    print("1/3: Loading pandas:")
    try:
        import pandas as pd
    except:
        print("Cannot Load 'Pandas'")
        return 1

    print("2/3: Loading NumPy:")
    try:
        import numpy as np
    except:
        print("Cannot Load 'Numpy'")
        return 1

    print("3/3: Loading MatPlotLib")
    try:
        import matplotlib.pyplot as plt
    except:
        print("Cannot Load 'MatPlotLib'")
        return 1
    return None


if __name__ == '__main__':
    main()

