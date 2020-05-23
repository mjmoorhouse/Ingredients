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

"""
import pandas as pd
import sys
import re
import matplotlib.pyplot as plt
import ingredients as ind

#User servicable parts:
manual_ingredients_tag = "Manual Ingredients"
combined_matrix_fname = "all_products.txt"
html_output_file_name = "product_ingredients_status.html"
Ingredients_Status_fname = "Ingredients_Status.png"

# Couple of Helper functions
def clean_up(name):
    """
    Changes the "_" to spaces and capitalises the string to titlecase:
    "foo_bar" becomes: "Foo Bar"
    """
    #Convert undersco
    name = re.sub(re.compile('_'),' ', name)
    return name.title()

def hack_CSS_table (css):
    """
    Swaps over the location of the table tag and the CSS ID
    "# CSSIDandlongwithit table {"
    """
    return (re.sub("#(.*?) table", r"#\1", css))



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

    # Render to a string first as we need to back-hack the table CSS (yuck, yuck):
    table_as_html = hack_CSS_table(df_style_obj.render())

    # Now write the file out as HTML
    file2 = open(html_output_file_name, "w+")
    file2.write(table_as_html)
    # For neatnees
    file2.close()

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

    # Plot the chart:
    bar_colors = ["#80dd80", "#5555FF", "#888888"]
    axis_gtp = graph_table.plot.bar(x="Product Class",
                                    y=["Parsed Automatically", "Ingredients Added Manually", "Absent"],
                                    stacked=True,
                                    title="Completeness of Ingredient List Datasets",
                                    position=0.8,
                                    figsize=(7, 6),
                                    color=bar_colors)

    # Tweak the axeses:
    axis_gtp.set_ylabel("Number of Products")
    plt.subplots_adjust(bottom=0.3)
    plt.savefig(Ingredients_Status_fname)

    # For kicks we might as well have the
    plt.show(block=True)



    print ("All done, bye-bye")


#This construct to allow functions in any order:
if __name__ == '__main__':
    main()