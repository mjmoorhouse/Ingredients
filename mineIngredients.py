"""
mineIngredients.py

This takes a list (currently fixed internally to simulate) and filters the main dataset by it initially for matching
products.
This is then Rendered to HTML internally and the actual 'highlighted' terms highlighted in a post processing step;
styling is as per the 'ingredients.py' module.

This S/W is currently in a demonstrator status.

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
        products_df = pd.read_csv(combined_matrix_fname, sep="\t", na_values="NaN")
    except:
        # If we can't load the basic data, we can't continue:
        print("Could not load data from '{}', exiting".format(combined_matrix_fname))
        sys.exit(1)
    print ("Loaded {} products".format(len(products_df["index"])))
    short_df = products_df.head(30)

    #Get a product list locally for now:
    c_product_list = example_product_list()

    #Create a list to store the matching product IDs as appending to Dataframes is slow:
    search_result_list = list()

    for c_ingredient in c_product_list:
        #Do the search (case insensitive), add just the IDs to list (duplicates being filtered later):
        search_result_list.extend(
            short_df[short_df['Ingredients'].str.contains(c_ingredient, case=False)]['Product ID'])
        print ("After testing for ingredient: '{}'\t there are '{}' unique product IDs".
               format(c_ingredient,len(search_result_list)))
    before_uniquing_ids = len(search_result_list)
    search_result_list = list(set(search_result_list))
    after_uniquing_ids = len(search_result_list)
    print ("Before and after uniquing IDs in list: {} & {} length of list".format(before_uniquing_ids, after_uniquing_ids))

    #Subset the total dataframe with the results of the 'pre-search' done above:
    matching_products_df = short_df[short_df['Product ID'].isin(search_result_list)]
    print (matching_products_df.columns)
    print (matching_products_df.dtypes)


    #print(matching_products_df['Weight'])

    matching_products_df.astype({'Weight':'Int64'}, copy=False)



    # Send off the data for rendering to HTML in the 'House Style'
    html_table = ind.render_df_to_html(matching_products_df)
    print ("HTML Table is: '{}'...etc...\n'{}'".format(html_table[:500], html_table[-1000:-1]))

    #Clean up the worst of the silliness in the HTML such as:

#This construct to allow functions in any order:
if __name__ == '__main__':
    main()
