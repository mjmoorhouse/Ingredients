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
    query_ingredients_list = example_product_list()

    #Create a list to store the matching product IDs as appending to Dataframes is slow:
    search_result_list = list()

    for c_ingredient in query_ingredients_list:
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

    #Add the new columns to store the ingredients match (maybe we need this?)
    colindex_counter = 3
    colindex = dict()
    #Create the new columns for each ingredient we are searching for:
    for c_ingredient in query_ingredients_list:
        matching_products_df.insert(3,c_ingredient.title(), "")
        #Store where we added each in a dictionary:
        colindex[c_ingredient] = colindex_counter
        colindex_counter = colindex_counter +1
    print ("Columns are: {}".format(matching_products_df.columns))
    print (colindex)

    #Do matches on each product and row to build output:
    #Do we need this at all? Redundant?
    product_ids = matching_products_df['Product ID']
    #Iterate down the rows of the dataframe:
    for c_index, c_row in matching_products_df.iterrows():
        product_ingredients = matching_products_df.iloc[c_index]['Ingredients']
        #Split list on commas:
        split_ingredients = product_ingredients.split(",")
        n_ingredients = len(split_ingredients)

        for c_target_ingredient in query_ingredients_list:
            this_re = re.compile("[^(]"+c_target_ingredient+"[^)]",re.IGNORECASE)
            for c_ingredient in split_ingredients:
                #print (" {} against {}".format(c_target_ingredient, c_ingredient), end="")
                #Do the search:
                if this_re.search(c_ingredient):
                    #print ("{}\t = ({})\t'{}'".format(c_index, n_ingredients, product_ingredients))
                    print ("\t::{} \t= {}".format(c_ingredient,c_target_ingredient))
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
    # match_locs = re.findall(re.compile('col4" >(.*?)</td>'), html_table)
    # for c_match in match_locs:
    #     print ("Matches are: {}".format(c_match))
    #print ("Match locations for the ingredient cells: {}".format(match_locs))
#This construct to allow functions in any order:

if __name__ == '__main__':
    main()
