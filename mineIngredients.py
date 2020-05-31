"""
mineIngredients.py

"""
print ("Loading modules:...[", end="")
import pandas as pd
import sys
import re
import seaborn as sb
import matplotlib.pyplot as plt
import ingredients as ind
import collections # Because not Perl and Hash Arrays...
print ("]....Done")
#User servicable parts:
combined_matrix_fname = "all_products.txt"

def example_product_list ():
    return ["milk", "whey", "Lactose","ShouldBeFalse"]

def main():
    # Read the data in:
    try:
        products_df = pd.read_csv(combined_matrix_fname, sep="\t")
    except:
        # If we can't load the basic data, we can't continue:
        print("Could not load data from '{}', exiting".format(combined_matrix_fname))
        sys.exit(1)
    print ("Loaded {} products".format(len(products_df["index"])))
    short_df = products_df.head(30)
    # print (short_df.head())

    #short_df = short_df.reindex()
    #short_df.reset_index(inplace=True, drop=True)
    # print ()
    # print (short_df)
    #sys.exit(0)
    # print(short_df.head())
    # #Get a product list locally for now:
    c_product_list = example_product_list()
    #Create a set of the product IDs:
    matching_products = list()
    #As appending to Dataframes is slow we append to the list, then build a DF from that.
    search_result_list = list()
    for c_ingredient in c_product_list:
        #Do the search (case insensitive), add just the IDs to list (we can filter for duplicates later):
        matching_products.extend(
            short_df[short_df['Ingredients'].str.contains(c_ingredient, case=False)]['Product ID'])
        print ("After testing for ingredient: '{}'\t there are '{}' unique product IDs".
               format(c_ingredient,len(matching_products)))
    before_uniquing_ids = len(matching_products)
    matching_products = list(set(matching_products))
    after_uniquing_ids = len(matching_products)
    print ("Before and after uniquing IDs in list: {} & {} length of list".format(before_uniquing_ids, after_uniquing_ids))


#This construct to allow functions in any order:
if __name__ == '__main__':
    main()
