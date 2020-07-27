"""
highlightIngredientFrequency.py


In the log plot of ingredient frequency, highlights the location of the ingredients in the 'decay curve' specificied
in the config.ini.

Outputs a PNG graphic of high quality to either the 'tag' file name or that specified in config.ini

"""

import ingredients as ind
import configparser
import pandas as pd
import sys
import seaborn as sb
import matplotlib.pyplot as plt
import argparse as argparser
import datetime
# Get the rank order file:
rankOrderFile = "ingredients_rank_order.txt"
"""
i.e. the one that looks like this:
	Ingredient	Count
0	Salt	650
1	Sugar	512
2	Water	425
3	Thiamin	353
4	Wheat Flour	344
5	Iron	324
6	Niacin	317
7	Milk	308
"""

def main():
    """
    Get the config file: this code needs to be factorised away into the module (assummption scoping won't cause too
    much passing of parameters about....but for now, verbatim from "mineIngredients.py"
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
            print("Config file: read successful")
            # Try to get the items we need - all are optional:
            # The Ingredients search list:
            if config['DEFAULT'].get('Ingredients'):
                query_ingredients_list = config['DEFAULT']['Ingredients'].split(",")
            # The outputfile tag:
            if config['DEFAULT'].get('OutputFileTag'):
                search_tag = config['DEFAULT']['OutputFileTag']
            else:
                # ....We weren't given it so ... Build the search tag from the list of ingredients we are searching for:
                search_tag = "".join([x[0:3] for x in query_ingredients_list])
                # Change any quotes to a "%" to prevent problems with the OS:
                search_tag = search_tag.replace("'", "-")
        except Exception as s:
            print("Tried to read config file ('{}') and failed; exiting".format(config_file))
            print("(Formally exception error was: '{}'".format(str(s)))
            sys.exit(1)
        #
    else:
        # Nothing passed - so run with the internal hard coded list:
        print("Using internal ingredients list: '{}'".format(ind.example_product_list()))
        query_ingredients_list = ind.example_product_list()
    print("Using ingredients list and search tag: '{}' & '{}'".format(query_ingredients_list, search_tag))
    try:
        counts_df = pd.read_csv(rankOrderFile,sep='\t')
    except Exception as S:
        print ("ERROR: Cannot read the counts of ingredient ranks '{}'".format(rankOrderFile))
        print (S)
        sys.exit(1)
    # If we are loading from FS then reseting column names and the index might be useful
    if 'Unnamed: 0' in counts_df.columns:
        print ("Resetting column name to 'Rank' and reindexing ")
        counts_df.rename(columns={'Unnamed: 0':'Rank'}, inplace=True)
        counts_df.reset_index(drop = True, inplace=True)

    print ("Raw table has = '{}' rows (length is)".format(len(counts_df)))
    print (counts_df.columns)

    print (counts_df.head())
    counts_df['Ingredient'] = [x.upper() for x in counts_df['Ingredient'] ]
    print(counts_df.head())
    #print ("All uppercase: '{}'".format(ingredient_list_uc))
    #To store the locations of the ingredient matches:
    """
    We are trying to mimic this line:
    if len(mega_data_df.loc[(mega_data_df['Product ID'] == c_id_value)]) == 0:
    """
    matches = dict()
    #To store the points we are going to label:
    annotations = list()
    # utterly fake this if we just want to test the top 'hits'
    import re
    #query_ingredients_list = ['Salt']
    for c_target_ingredient in query_ingredients_list:

        print ("Testing ingredient: '{}'".format(c_target_ingredient))
        ingredient_matches_df = ind.match_df_column(counts_df, 'Ingredient', c_target_ingredient)
        print (ingredient_matches_df)
        #
        # ###Pasting from makeOverlapMatrix.py START
        # # Should we use exact matching or partial matching: (Yes: if the the target in enclosed in ' ie. 'Salt')
        # if re.match(r"^'.*?'$", c_target_ingredient):
        #     # i.e. exact match:
        #     search_re = re.compile(str('^' + c_target_ingredient[1:-1] + '$'), re.IGNORECASE)
        # else:
        #     # Allow partial, fancy matches:
        #     search_re = re.compile('(?<![(])' + c_target_ingredient + '(?![)])', re.IGNORECASE)
        # ###Pasting from makeOverlapMatrix.py END
        #
        # match_bool_array = (counts_df['Ingredient'].str.match(search_re))
        #
        # # Select based on the Boolean opperation for inspection purposes:
        # print (counts_df[match_bool_array])
        # # We just need a list
        # matches_list = counts_df[match_bool_array]['Rank'].tolist()

        """
        Plot a graph....similar to the ingredients counts - but with the extra 'layer' / series.
        Really the plotting should be factorised away ultimately with a function common to assessDataCompleteness.py - 
        but not today. 
        """
        # print ("Ranks are:\n'{}'".format(matches['Rank']))
        #matches.reindex_like(counts_df)
        #matches.reindex()
        #matches.reindex()
        #matches.reset_index(drop = True, inplace = True)
        # print("Matches after index drop:\n'{}'".format(matches))
        # # match_lis
        # print("Ranks are:\n'{}'".format(matches['Rank'].tolist()))
        # print ("Matches: Typeof: '{}'".format(type(matches)))
        # # matches.set_index('Rank', inplace=True)
        # print ("Columns are: '{}'".format(matches.columns))
        # # print ("Matches: '{}'".format(matches))
        # this_rank = matches['Rank']
        # print("Info is: '{}'".format(matches.info()))
        # print ("Type ofs: '{}'".format(type(this_rank)))
        # print ("Ranks are: '{}'".format(matches['Rank']))
        # #print (counts_df[(counts_df['Ingredient'] == c_target_ingredient.upper())])
        # print ()
#This construct to allow functions in any order:
if __name__ == '__main__':
    main()