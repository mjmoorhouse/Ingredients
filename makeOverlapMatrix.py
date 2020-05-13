"""
makeOverlapMatric.py

When supplied with a directory containing cleaned files, this loads the first columns - containining product IDs -
in and produces a distance matrix of them.

The distance measure used is relatively simple - but easy to calculate:
d = 2 x N of matches between lists / Sum of the list lengths

It is expected - assumed implicitly - the lists are different lengths.

A check for uniqueness on loading of any lists is done.

"""
import os
import sys
import re


def main():
    print("Loading Pandas and dependencies:")
    try:
        import pandas as pd
    except:
        sys.exit("Could not load pandas module - check installation and environment is active")
    #Declare the list storing the IDs explictly.
    IDs_list = []
    # Set / Test the working directory; stop if it doesn't exist:
    data_location = os.getcwd() + "\\Cleaned"
    if not os.path.isdir(data_location):
        sys.exit("Could not find output directory: '{}'".format(data_location))
    print("Location of data files: {}".format(data_location))

    # Build the name of the distance matrix here so we can log it already:
    dist_matrix_file_path = data_location + "\\distance_mat.txt"
    print("Distance matrix will be output to: '{}'".format(dist_matrix_file_path))

    # Use a list comprehension to get all the CSV - hence Data - files, then count them:
    data_file_list = [x for x in os.listdir(data_location) if x.endswith(".txt")]
    num_data_file_list = len(data_file_list)
    if num_data_file_list > 0:
        print("Are [{0}] Files: {1}".format(len(data_file_list), data_file_list))
    else:
        print("No CSV Files found")

    # Do something more interesting - or at least pretend to:
    for c_file in range(0, num_data_file_list):
        c_file_name = data_file_list[c_file]
        # File Base Name: the file name without extensions:

        re_match = re.search(re.compile('(?P<tag>^.+)\.'), c_file_name)
        # re.compile('(?P<weight>[\d.]+)(?P<units>[kK]*[Gg])')
        c_base_name = re_match.group("tag")
        print("Tag is: '{}'".format(c_base_name))
        c_file_path = data_location + "\\" + c_file_name
        print("Processing #{0} of {1}\t: '{2}'".format(c_file + 1, num_data_file_list, c_file_name))

        # Read the data in:
        data_table = pd.read_csv(c_file_path, sep="\t")

        # Does it have the column we expect called "Product ID"?
        if not 'Product ID' in data_table.columns:
            print("Cannot find 'ID' column in this ({}) data loaded, skipping".format(c_base_name))
        these_IDs = data_table['Product ID']
        #Are the products unique?  Really they need to be for a fair count:
        if Check_Duplicates(these_IDs):
            print ("Duplicates in list found ({}) of".format(Check_Duplicates(these_IDs)))
            continue
        #All good, so add these IDs to the main list:
        IDs_list.append(these_IDs)

    # Loading done; some printout to assure us it is working:
    print ("There are '{}' lists added".format(len(IDs_list)))
    for x in range (0,len(IDs_list)):
        print ("List {} has {} elements".format(x, len(IDs_list[x])))

def Score_List(list_a, list_b):


def Check_Duplicates(data_list):
    """
    Expects a list, returns the number of duplicates found - hence 0 / False if none.
    Creates a 'set' of the list and compares the count - so formally nLog(n) time from memory.
    """
    result = len(data_list) - len(set(data_list))
    print ("Result of list: {} for {} items".format(result, len(data_list)))
    return result

# Originals:
# listA = ["Alice", "Bob", "Joe"]
# listB = ["Joe", "Bob", "Alice", "Ken"]

# Current:
# listA = ["Alice", "Bob", "Joe", "Kevin", "Julia", "Liam"]
# listB = ["Joe", "Bob", "Alice", "Ken", "Michelle", "Nick", "Marcel"]
#
# setA = set(listA)
# setB = set(listB)
#
# overlap = setA & setB
# universe = setA | setB
# total_len = len(listA) + len(listB)
#
# d = (2 * len(overlap) / total_len)
#
# result1 = float(len(overlap)) / len(setA) * 100
# result2 = float(len(overlap)) / len(setB) * 100
# result3 = float(len(overlap)) / len(universe) * 100
#
# print ("Result 1: '{}'".format(result1))
# print ("Result 2: '{}'".format(result2))
# print ("Result 3: '{}'".format(result3))
#
# print ("Total lenght: {}".format(total_len))
#
# print ("Distance: {:.2f}".format(d))

if __name__ == '__main__':
    # contains_result_str = "Fluffy"
    # al_string = re.sub(r"Contains",  contains_result_str, "Contains Nothing")
    # print ("Result: '{}'".format(al_string))
    main()
