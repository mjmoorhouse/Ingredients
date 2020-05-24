"""
assessDataCompleteness.py

Supplied with the make data matrix this prepares various summaries of the data completeness
This includes assessing which ingredients are missing and which are noted as being corrected.

The markup tag denoting ingredients have been entered manually it:
manual_ingredients_tag = "Manual Ingredients"
n_corrected_ingredients = int(this_group["Comments"].str.count("Manual Ingredients").sum())

It produces two tables of the completeness of the counts (raw) and a stacked bar graph showing the data
specificallly for each product category:
*) The counts for the number of ingredients present parsed directly
*) Those that were added in manually
*) Those 'Absent' (currently no tag as to whether it is because nobody they aren't avaialable
 or haven't had an attempt to  correct them).

A tally of the ingredients is done by splitting on commas (possibly naively given:
"WheatFlour[WheatFlour,CalciumCarbonate,...etc]" and the top 'n' (tails) printed items and values printed.

Ingredients >x and <y characters in length are excluded as are missing values (nan).


"""
print ("Loading modules:...[", end="")
import pandas as pd
import sys
import re
import seaborn
import matplotlib.pyplot as plt
import ingredients as ind
import collections # Because not Perl and Hash Arrays...
print ("]....Done")
#User servicable parts:
manual_ingredients_tag = "Manual Ingredients"
combined_matrix_fname = "all_products.txt"
raw_counts_html_fname = "product_ingredients_status.html"
Ingredients_Status_fname = "Ingredients_Status.png"
ingredient_counts_html_fname = "ingredients_counts"

tails = 6

"""
Start Code Proper
================================
Read the data in from - presumably - the combined tables.
"""
def main():
    # Read the data in:
    try:
        products_df = pd.read_csv(combined_matrix_fname, sep="\t")
    except:
        # If we can't load the basic data, we can't continue:
        print("Could not load data from '{}', exiting".format(combined_matrix_fname))
        sys.exit(1)

    # Print the first few lines, convince us it works:
    print(products_df.head())

    # Main results store; we create a DF from this ultimately
    group_counts = []

    # For all the groups:
    for c_group, this_group in products_df.groupby(['Source']):
        # Count the ingredients and determine which we have data for:
        n_ingredients = len(this_group["Ingredients"])
        missing_ingredients = this_group["Ingredients"].isna().sum()
        complete_ingredients = n_ingredients - missing_ingredients

        # Count the comments noting manual entry of ingredients "Manual Ingredients"
        n_corrected_ingredients = int(this_group["Comments"].str.count("Manual Ingredients").sum())
        print("Complete(of which corrected): total : \t{}\t({}) : \t{}".
              format(complete_ingredients, n_corrected_ingredients, n_ingredients))
        # Note down this information into a list (cf. DataFrame - which we build from the list ultimately for performance)
        group_counts.append({"Product Class": str(c_group),
                             "Total Products": int(n_ingredients),
                             "Ingredients": int(complete_ingredients),
                             "Corr. Ingredients": int(n_corrected_ingredients)})

    # Create the DataFrame for ease of printing and manipulation:
    group_counts_df = pd.DataFrame(group_counts,
                                   columns=["Product Class", "Total Products", "Ingredients", "Corr. Ingredients"])

    group_counts_df.columns = ["Product Class", "Number of Products", "Ingredients Present", "Ingredients Added Manually"]
    # Printout locally prior to pretty graphing:
    print("Ultimately:")
    print(group_counts_df)

    """
    Pretty Print 1/3: The HTML formatted table of the data as downloaded and cleaned.
    These are simple counts.
    """
    figure_caption = "Completeness of Data Download of Ingredients"

    # As we work a lot with the style object - create a short cut:
    df_style_obj = group_counts_df.style
    df_style_obj.set_caption(figure_caption)

    # Use the styles defined in our common module:
    df_style_obj.set_table_styles(ind.get_CSS_table_styles_dictionary())
    df_style_obj.hide_index()
    if ind.write_df_to_pretty_table(group_counts_df, raw_counts_html_fname, figure_caption):
        print ("Error in HTML table rendering to: '{}'".format(raw_counts_html_fname))
    # Render to a string first as we need to back-hack the table CSS (yuck, yuck):
    # table_as_html = hack_CSS_table(df_style_obj.render())
    #
    # # Now write the file out as HTML
    # file2 = open(raw_counts_html_output_fname, "w+")
    # file2.write(table_as_html)
    # # For neatnees
    # file2.close()
    sys.exit(0)
    """
    Pretty Print 3/3: The HTML table of the processed count data and a chart to go with it:
    """

    # Declare the raw, empty table:
    graph_table = pd.DataFrame(group_counts,
                               columns=["Product Class", "Parsed Automatically", "Ingredients Added Manually", "Absent"])

    # Populate the table to graph from:
    # Ensure the indexes are the same so we can copy columns across:
    graph_table.index = group_counts_df.index

    graph_table["Product Class"] = group_counts_df["Product Class"]
    graph_table["Parsed Automatically"] = group_counts_df[
        "Ingredients Present"]  # - group_counts_df["Ingredients Present"])
    graph_table["Ingredients Added Manually"] = group_counts_df["Ingredients Added Manually"]
    graph_table["Absent"] = (group_counts_df["Number of Products"] - \
                             group_counts_df["Ingredients Present"] -
                             group_counts_df["Ingredients Added Manually"])
    # Clean up the product labels:
    graph_table["Product Class"] = graph_table["Product Class"].apply(clean_up)

    ind.write_df_to_pretty_table(graph_table, ingredient_counts_html_fname)

    # Plot the chart:
    bar_colors = ["#80dd80", "#5555FF", "#888888"]
    axis_gtp = graph_table.plot.bar(x="Product Class",
                                    y=["Parsed Automatically", "Ingredients Added Manually", "Absent"],
                                    stacked=True,
                                    title="Completeness of Ingredient List Datasets",
                                    position=0.8,
                                    figsize=(7, 6),
                                    color=bar_colors)

    # Tweak the axises:
    axis_gtp.set_ylabel("Number of Products")
    plt.subplots_adjust(bottom=0.3)
    plt.savefig(Ingredients_Status_fname)

    # For kicks we might as well have the
    #plt.show(block=True)

    """
    Phase II: Summarise Ingredients
    Computes simple counts of the ingredients to produce a list
    
    To stop dictionary / count pollution there are two limits set on the max & min limit of the ingredients
    in the data set; this prevents mis-parsings being entered into the main dictionary 
    max_key_length = 3
    max_key_length = 40  
    """

    max_key_length = 30
    min_key_length = 3
    #In Perl this would be built in?

    #Create the tally:
    ingredients_tally = collections.Counter()
    #Iterate through all the products:
    for c_product in products_df['Ingredients']:
        #Split on comma into a list - with some filtering on the way past::
        these_ingredients = [x for x in str(c_product).split(",")
                             if x != "nan" and
                             len(x) <= max_key_length and
                             len(x) >= min_key_length]
        #Add those in the list to the dictionary for counting
        #(can't be done as a list comprehension which is a pity)
        for c_ingredient in these_ingredients:
            ingredients_tally[c_ingredient] += 1

    #So what we get: print the number of tails, top and bottom?

    """
    #Really this code has been superceeded already:
    tails = 10
    #Top:
    print ("Top {} ingredients are:".format(tails))
    [print (("{:<"+str(max_key_length)+"} =\t {}").format(c_ingrid,count))  for (c_ingrid,count)
        in ingredients_tally.most_common(tails)]
    print ("....then for the bottom {2}: ({0} to {1}): ".format(
        len(ingredients_tally)-tails,
        len(ingredients_tally),
        tails))
    #Bottom
    [print (("{:<"+str(max_key_length)+"} =\t {}").format(c_ingrid,count)) for (c_ingrid, count)
        in ingredients_tally.most_common()[:-tails-1:-1]]
    #print (output_list)
    """
    #Same again, but in an easier to plot DataFrame:
    ingredients_count_df = pd.DataFrame(columns=["Ingredient", "Count"])

    for (c_ingrid, count) in ingredients_tally.most_common(tails):
        print ("{} {}".format(c_ingrid,count))
        ingredients_count_df = ingredients_count_df.append({'Ingredient':c_ingrid, 'Count':count}, ignore_index=True)
    for (c_ingrid, count) in ingredients_tally.most_common()[:-tails - 1:-1]:
        ingredients_count_df = ingredients_count_df.append({'Ingredient':c_ingrid, 'Count':count}, ignore_index=True)
    print (ingredients_count_df)
    #....render to html prsumably at some point.

    #Plot a bar chart of the data:
    # ax_ics = ingredients_count_df.bar(x='Ingredient', y='Count', rot=0)
    # plt.show()


    sys.exit(0)

    print ("All done, bye-bye")


#Helper functions

def clean_up(name):
    """
    Changes the "_" to spaces and capitalises the string to titlecase:
    "foo_bar" becomes: "Foo Bar"
    """
    #Convert undersco
    name = re.sub(re.compile('_'),' ', name)
    return name.title()

#This construct to allow functions in any order:
if __name__ == '__main__':
    main()