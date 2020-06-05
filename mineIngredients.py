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
pd.set_option('display.max_columns', None)

def example_product_list():
    """
    Really simple helper function to fix/fake the search terms:
    :return:
    """
    return ["Salt"]
    #return ["milk", "whey", "Lactose","Salt"]

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
    #
    # for c_ingredient in query_ingredients_list:
    #
    #     #Create a 'match mask' using a simple search for now:
    #     product_mask = products_df['Ingredients'].str.contains(c_ingredient, case=False)
    #
    #     #Convert the NaN (from missing ingredients) to False:
    #     #There must be a list comprehension version of this (lamabda function? Map?)
    #     for x in range (0, len(product_mask)):
    #         #print ("x {} = {}".format(x, product_mask[x]))
    #         if math.isnan(product_mask[x]):
    #             product_mask[x] = False
    #
    #     #Note all the matching IDs as 'True' into a simple list (easier to extend+filter this than a Data Frame:
    #     matching_products_list.extend(products_df[product_mask]['Product ID'])
    #
    # #Remember this section is per target ingredients:
    # before_uniquing_ids = len(matching_products_list)
    # matching_products_list = list(set(matching_products_list))
    # after_uniquing_ids = len(matching_products_list)
    # print ("Before and after uniquing IDs in list: {} & {} length of list".format(before_uniquing_ids, after_uniquing_ids))
    #
    # #Subset the matching products into a new dataframe (as we will adapt / markup) - Remember to RE-INDEX it...
    # #....otherwise iterrows will get confused and iterate row-items that aren't there:
    # matching_products_df = products_df[products_df['Product ID'].isin(matching_products_list)]
    # matching_products_df.reset_index(inplace=True)

    print ("There are '{}' rows and columns in the 'matching_products' Data Frame".format(products_df.shape))
    #sys.exit(0)
    #Add the new columns to store the ingredients match (we don't need this?)
    colindex_counter = 3
    colindex = dict()
    #Create the new columns for each ingredient we are searching for:
    for c_ingredient in query_ingredients_list:
        products_df.insert(3,c_ingredient.title(), "")
        #Store where we added each in a dictionary:
        colindex[c_ingredient] = colindex_counter
        colindex_counter = colindex_counter +1

    # sys.exit(0)
    #print (products_df.iloc[56:59])
    #Basically everything that doesn't match:
    product_ids_to_remove = list()
    #Store the 'problematic ingredients' that can't be split on commas
    #  - likely this is because they are missing and "NaN"
    problematic_ingredients = list()
    #Iterate through the matching rows
    for c_index, c_row in products_df.iterrows():
        this_product_id= c_row['Product ID']
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
        try:
            split_ingredients = raw_ingredients.split(",")
        except:
            problematic_ingredients.append(raw_ingredients)
            product_ids_to_remove.append(c_index)
            continue
            # print (c_row)
            # print (raw_ingredients)
            # sys.exit(0)
        #As we use this a lot:
        c_productid = c_row['Product ID']
        #When we find a  match: flip this 'bit' to prevent the product getting added to the removal list:
        no_match_marker = True

        #Test - properly this time - the ingredients we are searching for against the ingredients list:
        for c_target_ingredient in query_ingredients_list:
            print ("Testing '{}' Target ingredient".format(c_target_ingredient))
            #Compile a Regex to exclude "(Milk)" but include "Milk", "Milk Protein", "milk powder"
            this_re = re.compile('(?<![(])'+c_target_ingredient+'(?![)])',re.I)
            for c_ingredient in split_ingredients:
                #Do the search (ignoring the upper/lower casee)
                result = this_re.search(c_ingredient)

                #Result of a match is not 'None', do something with the match:
                if result:
                    #First a match reqiires we to keep this product in the table:
                    no_match_marker = False
                    #Get the boundaries of the text match:
                    start, end = result.span()
                    #Ask for the text marking up and store the result in the dataframe:
                    html_markup = markup_ingredient_text(c_ingredient, start, end)
                    print  ("HTML markup:'{}'".format(html_markup))
                    products_df.at[c_index, c_target_ingredient.title()] = html_markup
        #So if we really don't find a match then add this product to the removal (kill) list:
        if no_match_marker == True:
            product_ids_to_remove.append(c_index)
    #Remove all the non-matching products:
    print("This many products didn't match and were removed: {} / {} products ".
           format(len(product_ids_to_remove), len(products_df.index)))
    products_df.drop(index= product_ids_to_remove, inplace=True)
    print ("Included in this are {} products with problematic (missing likely) ingredients".
           format(len(problematic_ingredients)))
    #Likely we don't care - but should we need to investigate:
    #print(problematic_ingredients)
    n_matching_products = len(products_df.index)
    print ("Hence this many products matches and will be outputted: {}".format(n_matching_products))

    #Just remove this column for printout purposes temporarally:
    products_df.drop(columns='Ingredients',inplace=True)
    #print (products_df.head())

    """
    HTML Table rendering:
    """

    #A little pre-rendering manipulation as this easier here (weights round to ints, supress NaN to empty (&nbsp?)
    #than back-hacking the HTML afterwards with Regexs.
    products_df.astype({'Weight':'Int64'}, copy=False)
    products_df['Comments'].fillna("",inplace=True)

    # Send off the data for rendering to HTML in the 'House Style'
    html_table = ind.render_df_to_html(products_df,
                    "Results of {} products search of '{}'".
                    format(str(n_matching_products), str(query_ingredients_list)))

    #Clean up the worst of the silliness in the HTML such as:

    #a) Make the product link really a link:
    # class="data row29 col3" >https://www.tesco.com/groceries/en-GB/products/305781649</td>
    #->
    # class="data row29 col3" ><A href="https://www.tesco.com/groceries/en-GB/products/305781649></a>
    # https://www.tesco.com/groceries/en-GB/products/305781649</td>
    #For this we have to find the column:
    URL_colindex_groups = re.match(r"<th.*?(?:col)(\d)\">URL", html_table)
    print ("Match result = '{}'".format(URL_colindex_groups))
    URL_colindex = 4
    #URL_colindex = URL_colindex_groups.group(1)
    print ("The URL column is {}".format(URL_colindex))
    html_table = re.sub(r"(?:col"+str(URL_colindex)+"\" \>)(.*?)(?: *\<\/td>)",
                        r'col3" >\n<a href="\1">\1</a></td>',html_table)

    #Print a subsection of the table if you are having difficultly:
    #print("HTML Table is: \n'{}'...etc...\n'{}'".format(html_table[:500], html_table[-2000:-1]))
    if ind.write_item_to_file(html_table, "example_match_table.html"):
        print ("Could not write out HTML table")
        sys.exit(1)
    print("All Done, Bye Bye")
    sys.exit(0)

#This construct to allow functions in any order:

def markup_ingredient_text(text, start=0, end=1, css_class="ingtxt"):
    """
    Pass the ingredient text string and it handles the markup with the CSS class ".ingtxt" by default.
    While simple the syntax is a little noisy and it is possible this routine might become more features in the
    future - so the complexity is burried here.
    :param c_ingredient: the text string to markup
    :param start: the character index to start the markup
    :param end: the character index to end the markup
    :return: the HTML text string
    The output will be similar to this:
    skimmed<div class=".ingtxt">milk</div> powder

    mimicing this:
    marked_up = c_ingredient[0:start+1]+"|"+c_target_ingredient+"|"+c_ingredient[end-1:]
    """
    print ("MIT: {},{},{},{}".format(text,start,end,css_class))
    marked_up_text =  '{}<span class="{}">{}</span>{}'.\
                    format(text[0:start],
                           css_class,
                           text[start:end],
                           text[end:])
    #print ("MIT: returning: '{}'".format(marked_up_text))
    return marked_up_text

def example_product_list():
    """
    Really simple helper function to fix/fake the search terms:
    :return:
    """
    #return ["Salt"]
    #return ["milk", "whey", "Lactose","Salt"]
    return ["milk","Salt"]


if __name__ == '__main__':
    main()
