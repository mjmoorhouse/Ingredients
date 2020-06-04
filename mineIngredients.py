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
import numpy as np
import ingredients as ind
import math
print ("]....Done")
#User servicable parts:
combined_matrix_fname = "all_products.txt"
#Might be useful if printing to terminal, otherwise causes no harm:
pd.set_option('display.max_rows', None)

def example_product_list():
    """
    Really simple helper function to fix/fake the search terms:
    :return:
    """
    return ["milk", "whey", "Lactose","ShouldBeFalse"]

def main():
    """
    This uses a 'double pass' search for now:
    1) Any match against the ingredients being searched for termed 'target ingredients'
        (supplied internally for testing by example_product_list() )
    2) A finner grained match against the ingredients split by commas

    In addition there is a data loading section (read from tab-delimited file).
    and an HTML table output section showing the matches for manual inspection
    (expect this to Go Away ultimately - or into Suppl. Mat. ) and the general counts are useful.

    :return:
    """
    # Read the data in:
    try:
        products_df = pd.read_csv(combined_matrix_fname, sep="\t", na_values="NaN")
    except:
        # If we can't load the basic data, we can't continue so error:
        print("Could not load data from '{}', exiting".format(combined_matrix_fname))
        sys.exit(1)
    print ("Loaded {} products".format(len(products_df["index"])))

    #Get a product list locally for now from a function (ultimately likely a tab delimited or JSON file):
    query_ingredients_list = example_product_list()

    #Create a list to store the matching product IDs as appending to Dataframes is slow:
    matching_products_list = list()

    for c_ingredient in query_ingredients_list:

        #Create a 'match mask' using a simple search for now:
        product_mask = products_df['Ingredients'].str.contains(c_ingredient, case=False)

        #Convert the NaN (from missing ingredients) to False:
        #There must be a list comprehension version of this (lamabda function? Map?)
        for x in range (0, len(product_mask)):
            #print ("x {} = {}".format(x, product_mask[x]))
            if math.isnan(product_mask[x]):
                product_mask[x] = False

        #Note all the matching IDs as 'True' into a simple list (easier to extend+filter this than a Data Frame:
        matching_products_list.extend(products_df[product_mask]['Product ID'])

    #Remember this section is per target ingredients:
    before_uniquing_ids = len(matching_products_list)
    matching_products_list = list(set(matching_products_list))
    after_uniquing_ids = len(matching_products_list)
    print ("Before and after uniquing IDs in list: {} & {} length of list".format(before_uniquing_ids, after_uniquing_ids))

    #Subset the matching products into a new dataframe (as we will adapt / markup) - Remember to RE-INDEX it...
    #....otherwise iterrows will get confused and iterate row-items that aren'the there:
    matching_products_df = products_df[products_df['Product ID'].isin(matching_products_list)]
    matching_products_df.reset_index(inplace=True)

    print ("There are '{}' rows and columns in the 'matching_products' Data Frame".format(matching_products_df.shape))
    #sys.exit(0)
    #Add the new columns to store the ingredients match (we don't need this?)
    colindex_counter = 3
    colindex = dict()
    #Create the new columns for each ingredient we are searching for:
    for c_ingredient in query_ingredients_list:
        matching_products_df.insert(3,c_ingredient.title(), "")
        #Store where we added each in a dictionary:
        colindex[c_ingredient] = colindex_counter
        colindex_counter = colindex_counter +1

    # sys.exit(0)
    #Iterate through the matching rows
    for c_index, c_row in matching_products_df.iterrows():
        raw_ingredients = c_row['Ingredients']
        #Keep this section for now...ICE
        # try:
        #     #raw_ingredients = matching_products_df.iloc[c_index]['Ingredients']
        # except Exception as e:
        #
        #     print("\n\n\This combination is erroring: '{}' index, row '\n{}'".format(c_index, c_row))#
        #     print("Erroring ingredients: ".format(matching_products_df.iloc[12]['Ingredients']))
        #     print("Raw Ingredients: '{}'".format(raw_ingredients))
        #     #print("split: '{}'".format(split_ingredients))
        #     print ("Error was: '{}'".format(str(e)))
        #     print ("Count is: '{}'".format(count))
        #     print ("We will iterate through this number of rows: '{}'".format(len(list(matching_products_df.iterrows()))))
        #     sys.exit(0)
        # Split list on commas for indvidual ingredients:
        split_ingredients = raw_ingredients.split(",")
        #As we use this a lot:
        c_productid = c_row['Product ID']
        #Test - properly this time - the ingredients we are searching for against the ingredients list:
        for c_target_ingredient in query_ingredients_list:
            this_re = re.compile("[^(]"+c_target_ingredient+"[^)]",re.IGNORECASE)
            for c_ingredient in split_ingredients:
                #Do the search (ignoring the upper/lower casee)
                result = this_re.search(c_ingredient, re.IGNORECASE)
                if result:
                    start, end = result.span()
                    marked_up = c_ingredient[0:start+1]+"|"+c_target_ingredient+"|"+c_ingredient[end-1:]
                    print ("{}:\t [{} - {}] (product '{}') as marked up: '{}'".
                           format(c_target_ingredient,start,end, c_productid, marked_up))

    """
    HTML Table rendering:
    """
    print ("All Done, Bye Bye")
    sys.exit(0)
    #A little pre-rendering manipulation as this easier here (weights round to ints, supress NaN to empty (&nbsp?)
    #than back-hacking the HTML afterwards with Regexs.
    matching_products_df.astype({'Weight':'Int64'}, copy=False)
    matching_products_df['Comments'].fillna("",inplace=True)

    # Send off the data for rendering to HTML in the 'House Style'
    html_table = ind.render_df_to_html(matching_products_df)
    print ("HTML Table is: \n'{}'...etc...\n'{}'".format(html_table[:500], html_table[-2000:-1]))
    #Clean up the worst of the silliness in the HTML such as:

    #a) Make the product link really a link:
    # class="data row29 col3" >https://www.tesco.com/groceries/en-GB/products/305781649</td>
    #->
    # class="data row29 col3" ><A href="https://www.tesco.com/groceries/en-GB/products/305781649></a>
    # https://www.tesco.com/groceries/en-GB/products/305781649</td>
    html_table = re.sub(r"(?:col3\" \>)(.*?)(?: *\<\/td>)",r'col3" >\n<a href="\1">\1</a></td>',html_table)
    print("HTML Table is: \n'{}'...etc...\n'{}'".format(html_table[:500], html_table[-2000:-1]))

    # Demonstrate we can mark up columns afterwards (might not be needed?)
    # match_locations = re.findall(re.compile('col4" >(.*?)</td>'), html_table)
    # for c_match in match_locations:
    #     print ("Matches are: {}".format(c_match))
    #
    # print ("Match locations for the ingredient cells: {}".format(match_locations))
#This construct to allow functions in any order:

if __name__ == '__main__':
    main()
