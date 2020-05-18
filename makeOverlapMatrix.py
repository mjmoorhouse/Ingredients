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

overlap_matrix_fname = "overlapmatrix.txt"
combined_matrix_fname = "all_products.txt"
dist_martrix_fname = "overlapmatrix.png"

#These are used to build the mega/meta dataframe: they should sync - ideally via a cofig file at some point -
#to those in cleanRawDownloads.py
from pandas import DataFrame

new_column_names = ["Product ID", "Product Name", "URL", "Ingredients", "Allergens", "Weight", "Source"]

def main():
    print("Loading Pandas and dependencies:")
    try:
        import pandas as pd
        import numpy as np
        import seaborn as sb
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
    except:
        sys.exit("Could not load pandas module - check installation and environment is active")
    #Declare the list storing the IDs explictly and the 'columns names' based on the none-extension parts of the filenames
    IDs_list = []
    tag_list = list()
    # Set / Test the working directory; stop if it doesn't exist:
    data_location = os.getcwd() + "\\Cleaned"
    if not os.path.isdir(data_location):
        sys.exit("Could not find output directory: '{}'".format(data_location))
    print("Location of data files: {}".format(data_location))

    # Build the name of the distance matrix here so we can log it already:
    dist_matrix_file_path = data_location + "\\distance_mat.txt"

    #Unique-Mega dataframe / table containing all unique product IDs (prefixed with their search origin):
    mega_data_df = pd.DataFrame(columns=new_column_names)

    print("Distance matrix will be output to: '{}'".format(dist_matrix_file_path))

    # Use a list comprehension to get all the CSV - hence Data - files, then count them:
    data_file_list = [x for x in os.listdir(data_location) if x.endswith(".txt")]
    num_data_file_list = len(data_file_list)
    if num_data_file_list > 0:
        print("Are [{0}] Files: {1}".format(len(data_file_list), data_file_list))
    else:
        print("No CSV Files found - Exiting")
        sys.exit(0)

    # Iterate through the files found:
    for c_file in range(0, num_data_file_list):
        c_file_name = data_file_list[c_file]

        c_file_path = data_location + "\\" + c_file_name
        print("Processing #{0} of {1}\t: '{2}'".format(c_file + 1, num_data_file_list, c_file_name))

        # Read the data in:
        data_table = pd.read_csv(c_file_path, sep="\t")

        # Does it have the column we expect called "Product ID"?
        if not 'Product ID' in data_table.columns:
            print("Cannot find 'ID' column in this ({}) data loaded, skipping".format(c_base_name))
        #Extract the product IDs into separate list:
        these_product_ids = data_table['Product ID']
        # Are the products unique?  Really they need to be for a fair count:
        if Check_Duplicates(these_product_ids):
            print("Duplicates in list found ({}) of".format(Check_Duplicates(these_product_ids)))
            continue

        #Build the tag name (File Base Name + number of items):
        re_match = re.search(re.compile('(?P<tag>^.+)\.'), c_file_name)
        c_base_name = re_match.group("tag")
        #Tag the data as to it's origin:

        data_table['Source'] = c_base_name
        #The number of IDs - we use this more than once so:
        n_in_list = len(these_product_ids)
        #Build and store the tag name in the format "choc_biscuits(33)" or "crackers(46)"
        #Note: This is used for displate purposes only in the distance matrix:
        tag_list.append(c_base_name)
        #Alternative if the number of items in the name is helpful "dips(28)" cf. "dips"
        #tag_list.append(c_base_name + "(" + str(n_in_list) + ")")

        #Add these IDs to the main list also:
        IDs_list.append(these_product_ids)

        #Also add these to the other mega/meta analysis matrix:
        for c_id in range (0, n_in_list):
            c_id_value = these_product_ids[c_id]
            if len(mega_data_df.loc[(mega_data_df['Product ID'] == c_id_value)]) == 0:
                #Remember we need to cast the product IDs as Integers:
                row = data_table.loc[data_table['Product ID']==int(c_id_value)]
                mega_data_df = mega_data_df.append(row)

        print ("mega_data_df has {} entries now".format(mega_data_df['Product ID'].count()))

    # Loading done; some printout to assure us it is working by printing stats:
    print ("There are '{}' lists added".format(len(IDs_list)))
    [print ("List {} has {} elements".format(x, len(IDs_list[x]))) for x in range (0,len(IDs_list))]

    #Do the overlap to compare ID Lists:
    ###
    #Create the distance matrix frame:
    dist_matrix: DataFrame = pd.DataFrame(columns = tag_list, index=tag_list)

    #Score the lists against each other:
    #(Could be a list comprehension if needed too)
    for x in range(0, len(IDs_list)):
        for y in range(0, len(IDs_list)):
            dist_matrix.at[tag_list[x],tag_list[y]] = Score_List(list(IDs_list[x]), list(IDs_list[y]))

    #Write out the distance matrix and the combined table:
    #To STDOUT:
    print(dist_matrix)

    #To FS: the distance Matrix:
    dist_matrix.to_csv(overlap_matrix_fname, sep='\t', index=True)
    print("Writing out overlap matrix as : '{}'".format(overlap_matrix_fname))

    #To FS: The Mega / Meta data frame:
    mega_data_df.index.name = "index"
    mega_data_df.to_csv(combined_matrix_fname, sep ='\t', index=True)
    print("Writing out combined results matrix as: '{}'".format(combined_matrix_fname))
    print ("Which has '{}' entries.".format(len(mega_data_df.index)))

    #Create heatmaps of distance matrix using seaborn, saving the result to a png file:
    #
    # To tweak plot elements: https://seaborn.pydata.org/tutorial/aesthetics.html#seaborn-figure-styles
    plt.subplots(figsize=(15,15))
    plt.suptitle("Counts of Product ID Common for Product Data Lists", fontsize= 20)
    plt.title("(Numbers on diagonal indicate number of products in list)", fontsize=15)

    #Mask off half (less diagonal) of the matrix.
    mask = np.zeros_like(dist_matrix)
    mask[np.triu_indices_from(mask, k=1)] = True

    #Create custom colors (orange):
    #After: https://stackoverflow.com/questions/38836154/discrete-legend-in-seaborn-heatmap-plot
    myColors = ('#fff5e6', '#ffcc80', '#ffc266', '#ffad33', '#ff9900')
    my_cmap = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))

    #Create the heatmap and annotation it
    #(briefly: masked to triangular, blue theme, grey grids lines, full blue at 5m, integer annotations, titles as above.

    sb.heatmap(dist_matrix.astype('float'), annot=True,
               mask=mask, square=True, cmap=my_cmap, linewidths=.5, linecolor='grey', fmt='g', vmax=5)
    from matplotlib.colors import LinearSegmentedColormap
    #Now faff with the color bar labels - maybe:
    # colorbar = ax.colorbar(sb)
    # colorbar.set_ticks(range(0,4))
    # colorbar.set_ticklabels(range(0,4))

    try:
        print ("Saving distance matrix as a PNG to '{}'".format(dist_martrix_fname))
        plt.savefig(dist_martrix_fname)
    except:
        print ("Saving distance as PNG failed")
    plt.show()

#### End of Main Program
def Score_List(list_a, list_b):
    """
    Basically the count of all the matches / the lengths of the two lists; i.e. classical...except for the 0->2 scale
    which might get cut back to 0->1 in future.
    """
    setA = set(list_a)
    setB = set(list_b)
    overlap = setA & setB
    universe = setA | setB
    #Scaled 0-1:
    #d = 1 * len(overlap) / len(universe)
    #Just raw counts: 1-max (A|B)
    d = len(overlap)
    return d

def Check_Duplicates(data_list):
    """
    Expects a list, returns the number of duplicates found - hence 0 / False if none.
    Creates a 'set' of the list and compares the count - so formally nLog(n) time from memory.
    """
    result = len(data_list) - len(set(data_list))
    return result

#This construct to allow functions in any order:
if __name__ == '__main__':
    main()
