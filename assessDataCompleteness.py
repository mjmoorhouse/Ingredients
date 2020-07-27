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
import seaborn as sb
import matplotlib.pyplot as plt
import ingredients as ind
import collections # Because not Perl and Hash Arrays...
print ("]....Done")
#User servicable parts:
manual_ingredients_tag = "Manual Ingredients"
combined_matrix_fname = "all_products.txt"
raw_counts_html_fname = "product_ingredients_status.html"
ingredients_status_graph_fname = "ingredients_status.png"
top_ingred_counts_fname = "ingredients_counts.html"
ingredients_counts_graph_fname = "ingredients_counts.png"
ingredients_rankorder_graph_fname = "ingredients_rank_order.png"
#Note this is just a simple CSV / TXT not HTML: we have 'top_ingred_counts_fname' for the top 'n' (top_n_ingredients)
ingredients_rankorder_table_fname = "ingredients_rank_order.txt"
#The number of items to report from the head and 'tail' of the ingredient usage count table:
top_n_ingredients = 10

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
                             "Number of Products": int(n_ingredients),
                             "Ingredients Found Automatically": int(complete_ingredients),
                             "Ingredients Added Manually": int(n_corrected_ingredients),
                             "Missing": int(n_ingredients-complete_ingredients)})

    # Create the DataFrame for ease of printing and manipulation:
    group_counts_df = pd.DataFrame(group_counts,
                    columns=["Product Class", "Number of Products", "Ingredients Found Automatically",
                             "Ingredients Added Manually", "Missing"])

    #I.e. the absent products:
    # group_counts_df["Absent"] = (group_counts_df["Number of Products"] - \
    #                          group_counts_df["Ingredients Present"])
    print("Ultimately:")
    print(group_counts_df)

    """
    Pretty Print 1/3: The HTML formatted table of the data as downloaded and cleaned.
    These are simple counts - and the absent products
    """

    # Send off the data for rendering to HTML in the 'House Style'
    if ind.write_df_to_pretty_table(group_counts_df, raw_counts_html_fname,
                                    "Completeness of Downloaded Ingredients"):
        print ("ERROR: in HTML table rendering to: '{}'".format(raw_counts_html_fname))

    """
    Pretty Print 2/3: A stacked graph of the same as the above table:
    If without the total column as we want the components.
    
    [Note that this code is very similar to that found in highlightIngredientFrequenct.py - it came from here.
    Ultimately we should factorise this out - but not today.]
    """
    #Delete the 'total' count:
    group_counts_df.drop(columns="Number of Products", inplace=True)

    # Clean up the product labels for plotting:
    group_counts_df["Product Class"] = group_counts_df["Product Class"].apply(clean_up)

    #Prep the graph canvas:
    sb.set(style="whitegrid")
    bar_colors = ["#80dd80", "#5555FF", "#888888"]
    axis_gtp = group_counts_df.plot.bar(x="Product Class",
                                    y=["Ingredients Found Automatically", "Ingredients Added Manually", "Missing"],
                                    stacked=True,
                                    title="Completeness of Product Category Datasets Ingredient Lists",
                                    position=0.7,
                                    figsize=(10, 6),
                                    color=bar_colors)

    axis_gtp.set_ylabel("Number of Products")
    axis_gtp.set_xlabel("")
    plt.subplots_adjust(bottom=0.4)
    plt.savefig(ingredients_status_graph_fname)

    # For kicks we might as well have a look:
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
    #Create the tally:
    ingredients_tally = collections.Counter()
    #In Perl this would be built in?

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

    #Take the filtered data and create a dataframe out of it:
    ingredients_count_df = pd.DataFrame(columns=["Ingredient", "Count"])
    ingredients_count_df['Ingredient'] = ingredients_tally.keys()
    ingredients_count_df['Count'] = ingredients_tally.values()
    ingredients_count_df.sort_values(by=['Count'],inplace=True, ascending=False, ignore_index=True)

    """
    Prepare the 'Top 10 graph':
    (and associated table first as HTML)
    """

    top_ingredients_df = ingredients_count_df[0:top_n_ingredients]
    print (top_ingredients_df)
    n_total_ingredients = len(ingredients_count_df)
    #Output 1/2: HTML rendered to FS in the 'House Style'
    if ind.write_df_to_pretty_table(top_ingredients_df, top_ingred_counts_fname,
                                    "Counts of "+ str(top_n_ingredients) + " Most Frequently Observed Ingredients"
                                    + " (of " + str(n_total_ingredients) + " total)"):
        print ("ERROR: in HTML table rendering to: '{}'".format(top_ingred_counts_fname))

    #Output 2/2: As a graph:
    sb.set(style="whitegrid")
    bar_colors = ["#80dd80"]
    top_ing_axs = top_ingredients_df.plot.bar(x="Ingredient",
                                    y="Count",
                                    title="Counts of the " + str(top_n_ingredients) +
                                    " Most Frequently Observed Ingredients (cf. " + str(n_total_ingredients) + " total)",
                                    position=0.7,
                                    figsize=(10, 6),
                                    color=bar_colors)

    top_ing_axs.set_ylabel("Count")

    plt.subplots_adjust(bottom=0.4)
    plt.savefig(ingredients_counts_graph_fname)

    all_ing_axs = ingredients_count_df.reset_index().plot(x="index", y="Count",
                            title="Frequency of All Ingredients in Rank Order (" + str(n_total_ingredients) + " of)")
    # Adapt the plot - titles & ticks:
    plt.yscale("log")
    plt.yticks([1,10,50,100,200,500,1000])
    from matplotlib.ticker import ScalarFormatter
    all_ing_axs.yaxis.set_major_formatter(ScalarFormatter())
    all_ing_axs.set_ylabel("Count")
    all_ing_axs.set_xlabel("Rank Order")
    #Save the graph:
    plt.savefig(ingredients_rankorder_graph_fname)
    #Save the underlying dataframe (though as CSV as probably nobody cares):
    print("Writing out rank order table as : '{}'".format(ingredients_rankorder_table_fname))
    ingredients_count_df.to_csv(ingredients_rankorder_table_fname, sep='\t', index=True)

    """
    Now an x-y plot of all the ingredients.
    """

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