"""
highlightIngredientFrequency.py


In the log plot of ingredient frequency, highlights the location of the ingredients in the 'decay curve' specificied
in the config.ini.

Outputs a PNG graphic of high quality to either the 'tag' file name or that specified in config.ini

"""

import ingredients as ind

import pandas as pd
import sys
import seaborn as sb
import matplotlib.pyplot as plt
import argparse as argparser
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
    # The ingredients we are going to search for (populate later) Get a product list locally for now from a function
    # (ultimately likely a tab delimited or JSON file):
    # As all these might be set in the config file, declare them in first in the wider scope:
    query_ingredients_list = list()
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
        counts_df = pd.read_csv(rankOrderFile, sep='\t')
    except Exception as error_recvd:
        print("ERROR: Cannot read the counts of ingredient ranks '{}'".format(rankOrderFile))
        print(error_recvd)
        sys.exit(1)

    for c_target_ingredient in query_ingredients_list:
        graph_fname = c_target_ingredient[0:4]+"highcount.png"
        print("Drawing  graphand highlighting ingredient '{}'".format(c_target_ingredient))

        result = draw_count_graph_with_highlighting(counts_df, c_target_ingredient, graph_fname)

    """
    So break here: loading routines above, graph below of the original 
    """


def draw_count_graph_with_highlighting(passed_df=None, hlight_ingredient=None, outfile_name=None):
    """

    :param passed_df: The dataframe of the rank of, the ingredient and its count with an index column called
        "Unnamed: 0"
        as this seems to be the
    :param hlight_ingredient: which ingredient to be highlighted as defined by ind.match_df_column() - so
        likely honours '' around the string to denote 'exact match'
    :param outfile_name: this is the name the
    :return: None or 1 on failure

    dataframe has a structure like this:
       Unnamed: 0   Ingredient  Count
    0           0         Salt    650
    1           1        Sugar    512
    2           2        Water    425
    3           3      Thiamin    353
    4           4  Wheat Flour    344
    """
    # If we are loading from FS then reseting column names and the index might be useful
    print("DCGwH: Starting: Ingredient\t'{}', FName: '{}'".format(hlight_ingredient, outfile_name))
    if 'Unnamed: 0' in passed_df.columns:
        print("Resetting column name to 'Rank' and reindexing ")
        passed_df.rename(columns={'Unnamed: 0': 'Rank'}, inplace=True)
        passed_df.reset_index(drop=True, inplace=True)

    print("Raw table has = '{}' rows (length is)".format(len(passed_df)))
    print(passed_df.columns)

    print(passed_df.head())
    # Everything to Upper case for comparison / matching:
    passed_df['Ingredient'] = [x.upper() for x in passed_df['Ingredient']]

    # If you are interested in looking at the top of the DF passed:
    # print(passed_df.head())
    """
    We are trying to mimic this line:
    if len(mega_data_df.loc[(mega_data_df['Product ID'] == c_id_value)]) == 0:
    """
    # Utterly fake this if we just want to test the top 'hits'
    # query_ingredients_list = ['Salt']

    print("Testing ingredient: '{}'".format(hlight_ingredient))
    ingredient_matches_df = ind.match_df_column(passed_df, 'Ingredient', hlight_ingredient)
    print(" : {} hits returned: '{}'".format(len(ingredient_matches_df),
                ingredient_matches_df['Ingredient'].tolist()))
    """
    Plot a graph....similar to the ingredients counts - but with the extra 'layer' / series. 
    """
    ingredient_matches_df.reset_index(drop=True, inplace=True)
    print(ingredient_matches_df.head())
    sb.set(style="whitegrid")
    # Get the Axis(es)
    top_ing_axs = plt.gca()
    top_ing_axs = passed_df.plot(x="Rank",
                        y="Count", kind="line", ax=top_ing_axs,
                        title="Counts for Ingredient '" + hlight_ingredient + "'",
                        marker="None",
                        color="grey", linestyle='-')
    print("'{}'".format(ingredient_matches_df.Rank))
    top_ing_axs.set_ylabel("Count")
    # plt.subplots_adjust(bottom=0.4)

    # Adapt the plot - titles & ticks:
    plt.yscale("log")
    # So we have the full range in on the tick marks:
    min_val = min(passed_df['Count'])
    max_val = max(passed_df['Count'])
    # Terrible hard coded values for the tick axises here...a point for improvement.
    # First is the locations, second are the values - specified as not be converted to standard form:
    plt.yticks([min_val, 2, 5, 10, 50, 100, 200, 500, 1000, max_val],
               [min_val, 2, 5, 10, 50, 100, 200, 500, 1000, max_val])
    # Name the axes:
    top_ing_axs.set_ylabel("Count")
    top_ing_axs.set_xlabel("Rank Order")
    # Plot the second dataset: the specific matches of the ingredients:
    ingredient_matches_df.plot(kind="line", x="Rank", ax=top_ing_axs,
                                linestyle="None", marker="o", figsize=(8, 6))
    # Add the point labels - in title case and their counts e.g.: "Milk in Powder Form (n)"
    for x, y, text in zip(ingredient_matches_df.Rank, ingredient_matches_df.Count, ingredient_matches_df.Ingredient):
        # Just build the separately for now:
        point_label = text.title() + " (" + str(y) + ")"
        plt.annotate(point_label, (x, y), rotation=45,
                     fontsize=10, xytext=(4, 5), textcoords='offset points')
    top_ing_axs.legend(["All Ingredient Counts", "Counts for '" + hlight_ingredient + "'"])
    # plt.show(block=True)
    print("Saving graph as: '{}'".format(outfile_name))
    plt.savefig(outfile_name)
    plt.clf()
    # sys.exit(0)


if __name__ == '__main__':
    main()
