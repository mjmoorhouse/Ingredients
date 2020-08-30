"""
mineIngredients.py

This takes a list (currently fixed internally to simulate) and filters the main dataset by it initially for matching
products.
This is then Rendered to HTML internally and the actual 'highlighted' terms highlighted in a post processing step;
styling is as per the 'ingredients.py' module.

This S/W is currently in a demonstrator status.

An optional config file can be used to override some program operations - specifically:
a) The list of ingredients searched for
b) The output file base used

For example run with:
./mineIngredients.py --config="config.ini"

Then in config.ini:
'
[DEFAULT]
# Note the "'" in the Ingredients list will be replaced by "-" to stop these confusing the OS / FS:
Ingredients = Milk,Salt,Whey,'Salt'

# OutputFileTag - the name given to the output files created.
# (As this is used for multiple files, it is best to not add extensions and keep it short: e.g.
# OutputFileTag = Milk_and_Cheese
OutputFileTag = Milk_and_Cheese

[DEFAULT]
'
Note that any "'" marks causing exact pattern matches are auto-translated to "-" to be more OS/FS friendly.

"""
print ("Loading modules:...[", end="")
import pandas as pd
import sys
import re
import ingredients as ind
import argparse as argparser
import datetime
print ("]....Done")
#User servicable parts (put these into a config file....soon.
combined_matrix_fname = "all_products.txt"
#The two suffixes of the html tables we will generate: e.g. "2020-06-10_milwheLacSal_matches.html"
product_match_table_base_fname = "matches.html"
ingredient_counts_base_fname = "counts.html"

#Filter the ingredient count table (if necessary):
report_threhold = 3


#This is the extra CSS used for rendering the match table:
mtable_extra_css = """
    #TABLE_ID .col1 {
      width: 15em;
}    
    #TABLE_ID .col2 {
      width: 3em;
}    
    #TABLE_ID .col3 {
      width: 10em;
}    
    #TABLE_ID .col4 {
      width: 4em;
}    
    #TABLE_ID .col5.data, .col6.data{
    word-break: break-all;
    font-size: 75%;
      width: 10em;
}
    #TABLE_ID EXTRA_COLS {
    word-break: break-all;
    border-bottom: 1px solid #AAA;
    border-left: 2px solid #AAA;
      width: 15em;
}
"""
ctable_extra_css = """
    #TABLE_ID .col0 {
      width: 15em;
}
    
    #TABLE_ID EXTRA_COLS {
    word-break: break-all;
    border-bottom: 1px solid #AAA;
    border-left: 2px solid #AAA;
      width: 15em;
}
"""

#Might be useful if printing dataframes to terminal, otherwise causes no harm:
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

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
    # The ingredients we are going to search for (populate later) Get a product list locally for now from a function (ultimately likely a tab delimited or JSON file):
    # As all these might be set in the config file, declare them in first in the wider scope:
    query_ingredients_list = list()
    config_file = ""
    search_tag = ""
    # Do we have command line arguments at all?
    if len(sys.argv) > 1:
        # Ok - go get the the config file...

        parser = argparser.ArgumentParser()
        parser.add_argument('--config', action="store")
        details = parser.parse_args()
        config_file = details.config
        # ....there is an implicit assumption that if the --config switch is being used then it should be expected
        # that a config file is at the end of it.
        import configparser
        print("Using config file ('{}')".format(config_file))

        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            print ("Config file: read successful")
            # Try to get the items we need - all are optional:
            #The Ingredients search list:
            if config['DEFAULT'].get('Ingredients'):
                query_ingredients_list = config['DEFAULT']['Ingredients'].split(",")
            #The rank order file:
            if config['DEFAULT']['RankedIngCountsFile']:
                rankOrderFile = config['DEFAULT']['RankedIngCountsFile']
            else:
                rankOrderFile = "ingredients_rank_order.txt"
            #The outputfile tag:
            if config['DEFAULT'].get('OutputFileTag'):
                search_tag = config['DEFAULT']['OutputFileTag']
            else:
                # ....We weren't given it so ... Build the search tag from the list of ingredients we are searching for:
                search_tag = "".join([x[0:3] for x in query_ingredients_list])
                # Change any quotes to a "%" to prevent problems with the OS:
                search_tag = search_tag.replace("'", "-")
        except Exception as s:
            print ("Tried to read config file ('{}') and failed; exiting".format(config_file))
            print ("(Formally exception error was: '{}'".format(str(s)))
            sys.exit(1)
        #
    else:
        # Nothing passed - so run with the internal hard coded list:
        query_ingredients_list = ind.example_product_list()
        print ("Using internal ingredients list: '{}'".format(query_ingredients_list))
    print ("Using ingredients list and search tag: '{}' & '{}'".format(query_ingredients_list, search_tag))

    # Read the Products data in (contains the ingredients linked to products):
    try:
        products_df = pd.read_csv(combined_matrix_fname, sep="\t", na_values="NaN")
    except:
        # If we can't load the basic data, we can't continue so error:
        print("Could not load data from '{}', exiting".format(combined_matrix_fname))
        sys.exit(1)
    print ("Loaded {} products".format(len(products_df["index"])))

    try:
        counts_df = pd.read_csv(rankOrderFile, sep='\t')
    except Exception as error_recvd:
        print("ERROR: Cannot read the counts of ingredient ranks '{}'".format(rankOrderFile))
        print(error_recvd)
        sys.exit(1)
    print ("rankOrderFile = '{}'".format(rankOrderFile))
    # sys.exit(0)
    #print ("There are '{}' rows and columns in the 'matching_products' Data Frame".format(products_df.shape))
    #sys.exit(0)
    #Build the output filenames from the list of ingredients we are searching for:
    search_tag = "".join([x[0:3] for x in query_ingredients_list])
    #Change any quotes to a "%" to prevent problems with the OS:
    search_tag = search_tag.replace("'","-")

    print ("Filenames will be tagged with: '{}' (and today's date)".format(search_tag))
    this_day = str(datetime.date.today())
    match_res_fname = "_".join([this_day,search_tag,product_match_table_base_fname])
    counts_res_fname = "_".join([this_day, search_tag,ingredient_counts_base_fname])

    #Replace any quotation marks that might confuse the shell / OS:
    match_res_fname = match_res_fname.replace("'","^")
    counts_res_fname = counts_res_fname.replace("'", "^")
    # counts_res_fname = "{}-{}-{}".format(this_day,search_tag,ingredient_counts_base_fname)
    print ("Output html files are: {} and {}".format(match_res_fname,counts_res_fname))

    #Create the new columns for each ingredient we are searching for:
    for c_ingredient in query_ingredients_list:
        products_df.insert(products_df.shape[1],c_ingredient.title(), "")

    #To store the products that don not match:
    product_ids_to_remove = list()

    #Store the 'problematic ingredients' that can't be split on commas
    #  - likely this is because they are missing and "NaN"
    problematic_ingredients = list()

    #This stores a count of the ingredients matched:
    #ingredient_hits = defaultdict(lambda: defaultdict(dict))
    ingredient_hits = dict ()
    #Iterate through the matching rows:
    for c_index, c_row in products_df.iterrows():
        this_product_id= c_row['Product ID']
        raw_ingredients = c_row['Ingredients']
        # Split list on commas for individual ingredients:
        try:
            split_ingredients = raw_ingredients.split(",")
        except:
            problematic_ingredients.append(raw_ingredients)
            product_ids_to_remove.append(c_index)
            continue
        # When we find a  match: flip this 'bit' to prevent the product getting added to the removal list:
        no_match_marker = True

        # Test - properly this time - the ingredients we are searching for against the ingredients list:
        for c_target_ingredient in query_ingredients_list:
            # Use the module to build the Regex object:
            search_re = ind.build_ingredient_search_regex(c_target_ingredient)
            # Try to match all the ingredients in all the products:
            for c_ingredient in split_ingredients:
                # Do the search (ignoring the upper/lower case)
                result = search_re.search(c_ingredient)
                # Result of a actually match is not 'None', - so there is data to extract:

                if result:
                    # First a match reqiires we to keep this product in the table:
                    no_match_marker = False
                    # Get the boundaries of the text match:
                    start, end = result.span()
                    #Ask for the text marking up and store the result in the dataframe:
                    html_markup = markup_ingredient_text(c_ingredient, start, end)
                    #print  ("HTML markup:'{}'".format(html_markup))
                    products_df.at[c_index, c_target_ingredient.title()] = html_markup

                    #Also note it in the ingredients hit count:
                    #increment_dict(tally_dict, level_1_key, level_2_key)
                    increment_dict (ingredient_hits, c_target_ingredient, c_ingredient.title())

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

    """
    Create a table of the ingredient hits - reported exceeding the threshold of 'report_threhold'
    
    """
    #print ("Breakdown of the ingredients found:\n'{}'".format(ingredient_hits))
    #Insist
    ingredient_hits_df = pd.DataFrame.from_dict(ingredient_hits,dtype='int64')
    print (ingredient_hits_df.head())

    print (len(ingredient_hits_df.columns))
    print ("Columns are: '{}'".format(list(ingredient_hits_df.columns)[::-1]))


    ingredient_hits_df.sort_values(inplace=True, by=list(ingredient_hits_df.columns)[::-1], ascending=False)


    #Just remove this column for printout purposes temporally:
    #(We might want to add this back in at some point to give context; not now)
    products_df.drop(columns='Ingredients',inplace=True)
    #print (products_df.head())

    #Create a mask for filtering the rows with not much in them:
    #(Ask for a sum across all rows {list} then test using a comprehension for Boolean array:
    exceeds_report_count_df = [True if x>report_threhold else False for x in ingredient_hits_df.sum(axis=1)]

    #print (exceeds_report_count_df)
    n_below_below_reporting_threshold = len(exceeds_report_count_df) - sum(exceeds_report_count_df)
    print ("Will exclude '{}' (of {}) ingredients as below threshold of {} instances required for reporting".
           format(n_below_below_reporting_threshold,len(ingredient_hits_df),report_threhold))

    short_ingredient_hits_df = ingredient_hits_df[exceeds_report_count_df]
    short_ingredient_hits_df.index.name = 'Ingredient'
    short_ingredient_hits_df.reset_index(inplace=True)

    #['Ingredient'] = short_ingredient_hits_df.index
    # short_ingredient_hits_df = short_ingredient_hits_df.astype(int, errors='ignore')

    """
    HTML Table rendering:
    1) The product matches
    """

    #A little pre-rendering manipulation as this easier here (weights round to ints, supress NaN to empty (&nbsp?)
    #than back-hacking the HTML afterwards with Regexs.
    #Set nan to empty, truly:
    products_df['Comments'].fillna("",inplace=True)
    print ("Column names are: '{}'".format(products_df.columns))

    #Relabel the weight:
    if 'Weight' in products_df.columns:
        products_df.rename(columns = {"Weight":"Weight (g)"}, inplace=True)
        products_df = products_df.astype({'Weight (g)':'Int64'})
    print ("Column types are: {}".format(products_df.dtypes))
    # sys.exit(0)
    # Send off the data for rendering to HTML in the 'House Style'
    pm_html_table = ind.render_df_to_html(products_df,
                    "Results of {} products search of '{}'".
                    format(str(n_matching_products), str(query_ingredients_list)))
    #Add in the extra CSS for this particular table:

    #First - before we manipulate anything too much get the table ID (less likely to break here!):
    mt_table_id = ind.get_table_id(pm_html_table)

    #Clean up the worst of the silliness in the HTML such as:

    #a) Make the product link really a link:
    # class="data row29 col3" >https://www.tesco.com/groceries/en-GB/products/305781649</td>
    #->
    # class="data row29 col3" ><A href="https://www.tesco.com/groceries/en-GB/products/305781649></a>
    # https://www.tesco.com/groceries/en-GB/products/305781649</td>
    #For this we have to find the column:
    URL_colindex_groups = re.search(r'col(\d)" *>URL</th>', pm_html_table)
    URL_colindex = URL_colindex_groups.group(1)
    print ("The URL column determined as '{}'".format(URL_colindex))
    pm_html_table = re.sub(r"(?:col"+str(URL_colindex)+"\" \>)(.*?)(?: *\<\/td>)",
                        r'col3" >\n<a href="\1">link</a></td>',pm_html_table)

    #Add in the specific CSS formatting for this table over the default just before the "</style>" tag:
    #See Start of program for the actual text:
    #First add in the table IDs:
    mt_temp_css_string = mtable_extra_css.replace("TABLE_ID", mt_table_id)

    #Next build and format the extra 'Ingredient' columns:
    #Use a list comprehension to workaround upper & lower cases (else we could use just .index())
    ingredient_col_start = [item.lower() for item in products_df.columns].index("Comments".lower())
    #And assume there is one for each target / query ingredient:
    ingredient_col_end = ingredient_col_start + len(query_ingredients_list)-1
    #Use a list comprehension to build the list of tags and join the list using commas to form a string:
    tags_string = ','.join([".col{}.data".format(x)  for x in range(ingredient_col_start,ingredient_col_end+1)])
    #Replace the Hook in the CSS template with the column ids:
    mt_temp_css_string = mt_temp_css_string.replace('EXTRA_COLS', tags_string)

    #Merge in the bespoke CSS just before the </style> tag in the rendered table string with the above
    # added on the front of it:
    pm_html_table = pm_html_table.replace("</style>", mt_temp_css_string + "</style>\n")

    #Print a subsection of the table if you are having difficultly:
    #print("HTML Table is: \n'{}'...etc...\n'{}'".format(pm_html_table[:500], pm_html_table[-2000:-1]))

    #Request a write out using the module file handling routine(s):
    if ind.write_item_to_file(pm_html_table, match_res_fname):
        print ("Could not write out HTML table {} (matching ingredients)".format(product_match_table_base_fname))
        sys.exit(1)

    """
    HTML Table rendering:
    2) The counts of ingredients observed
    """
    print ("Starting Ingredient Counts Table Rendering")
    # Set all the column data types of the Ingredients to integer:
    # NB:s the Pandas Int64 (allows NAs), not the NumPy int64
    # Get the types - though really we use the len of the list programatically
    ct_dtypes = list(short_ingredient_hits_df.dtypes)
    print ("Column types before: '{}'".format(ct_dtypes))
    # The new types (all Int64 actually) are added here linked to the column name:
    new_dtypes = dict()
    # Everything but the first column (the ingredient):
    for c_col_indx in range (1,len(ct_dtypes)):
        col_name = short_ingredient_hits_df.columns[c_col_indx]
        # Printout for if anybody is watching:
        print ("Setting column '{}' to Int64 (integer allowing the NaN)".format(col_name))
        new_dtypes[col_name] = "Int64"
    # Set the column types:
    short_ingredient_hits_df = short_ingredient_hits_df.astype(new_dtypes)
    # For the 'before and after' status:
    print("Column types after: '{}'".format(list(short_ingredient_hits_df.dtypes)))


    #Render the dataframe to an HTML table:
    ct_html_table = ind.render_df_to_html(short_ingredient_hits_df,
                    "Counts of ingredient occurrences observed more than {} times'".
                    format(str(report_threhold)))
    #Get the ID from it:
    ct_table_id = ind.get_table_id(ct_html_table)
    print (ct_table_id)

    #
    #First add in the table IDs:
    ct_temp_css_string = mtable_extra_css.replace("TABLE_ID", mt_table_id)

    #Write the count table out:
    if ind.write_item_to_file(ct_html_table, counts_res_fname):
        print ("Could not write out HTML table {} (ingredient counts)".format(counts_res_fname))
        sys.exit(1)
    print("All Done, Bye Bye")

    """
    The individual Ingredient frequency graphs:
    """
    for c_target_ingredient in query_ingredients_list:
        # Use the first (up to) 7 characters of the ingredient name:
        graph_fname = c_target_ingredient[0:6]+"highcount.png"
        # This helps with various OSs:
        graph_fname = graph_fname.replace(" ","_")

        print("Drawing  graphand highlighting ingredient '{}' into file '{}'".format(c_target_ingredient, graph_fname))
        # Make the graphing call:
        result = ind.draw_count_graph_with_highlighting(counts_df, c_target_ingredient, graph_fname)
        # Enable this to use/develop the internal function:
        # result = draw_count_graph_with_highlighting(counts_df, c_target_ingredient, graph_fname)
        print("Result of plotting call: '{}'".format(result))


    sys.exit(0)

def increment_dict(tally_dict, level_1_key, level_2_key):
    """
    Because in Python we have dictionaries that don't auto-vivify their sub level keys
    (Perl has to be better at something)
    :param tally_dict: the dictionary to increment
    :param level_1_key: dict[THIS ONE][]
    :param level_2_key: dict[][THIS ONE]
    :return:
    """
    #Initialise the base (1st level key) if it doesn't exist:
    if tally_dict.get(level_1_key) == None:
        #print ("Base key doesn't exist; so adding...")
        tally_dict[level_1_key] = dict()

    #Initilise the second level key now?
    if tally_dict.get(level_1_key).get(level_2_key) == None:
        tally_dict[level_1_key][level_2_key] = 0
        #print ("Key init: {}".format(tally_dict[level_1_key][level_2_key]))

    #Increment the tally now both keys levels exist:
    tally_dict[level_1_key][level_2_key] = tally_dict[level_1_key][level_2_key] + 1
    return 0

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
    #print ("MIT: {},{},{},{}".format(text,start,end,css_class))
    marked_up_text =  '{}<span class="{}">{}</span>{}'.\
                    format(text[0:start],
                           css_class,
                           text[start:end],
                           text[end:])
    #print ("MIT: returning: '{}'".format(marked_up_text))
    return marked_up_text


if __name__ == '__main__':
    main()
