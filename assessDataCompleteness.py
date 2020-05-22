"""
assessDataCompleteness.py

Supplied with the make data matrix this prepares various summaries of the data completeness
This includes assessing which ingredients are missing and which are noted as being corrected.

The markup tag denoting ingredients have been entered manually it:
manual_ingredients_tag = "Manual Ingredients"
n_corrected_ingredients = int(this_group["Comments"].str.count("Manual Ingredients").sum())

"""
import pandas as pd
import sys

#User servicable parts:
manual_ingredients_tag = "Manual Ingredients"
combined_matrix_fname = "all_products.txt"
html_output_file_name = "product_ingredients_status.html"
Ingredients_Status_fname = "Ingredients_Status.png"

#Read the data in:
try:
    products_df = pd.read_csv(combined_matrix_fname, sep="\t")
except:
    #If we can't load the basic data, we can't continue:
    print ("Could not load data from '{}', exiting".format (combined_matrix_fname))
    sys.exit(1)

#Print the first few lines, convince us it works:
print (products_df.head())

#Main results store; we create a DF from this ultimately
group_counts = []

#For all the groups:
for c_group, this_group in products_df.groupby(['Source']):
    #Count the ingredients and determine which we have data for:
    n_ingredients = len(this_group["Ingredients"])
    missing_ingredients = this_group["Ingredients"].isna().sum()
    complete_ingredients = n_ingredients - missing_ingredients

    #Count the comments noting manual entry of ingredients "Manual Ingredients"
    n_corrected_ingredients = int(this_group["Comments"].str.count("Manual Ingredients").sum())
    print ("Complete(of which corrected): total : \t{}\t({}) : \t{}".
           format(complete_ingredients, n_corrected_ingredients, n_ingredients))
    #Note down this information into a list (cf. DataFrame - which we build from the list ultimately for performance)
    group_counts.append({"Product Class" : str(c_group),
                         "Total Products" : int(n_ingredients),
                         "Ingredients" : int(complete_ingredients),
                         "Corr. Ingredients" : int(n_corrected_ingredients)})

#Create the DataFrame for ease of printing and manipulation:
group_counts_df = pd.DataFrame (group_counts,
                                columns=["Product Class", "Total Products", "Ingredients", "Corr. Ingredients"]  )

group_counts_df.columns = ["Product Class", "Number of Products", "Ingredients Present", "Ingredients Added Manually"]
#Printout locally prior to pretty graphing:
print ("Ultimately:")
print (group_counts_df)


"""
Pretty Print 2/3: The HTML formatted table

"""

figure_caption = "Completeness of Data Download of Ingredients"

#As we work a lot with the style object - create a short cut:
df_style_obj = group_counts_df.style
df_style_obj.set_caption(figure_caption)
styles = [
    dict(selector="table", props =[("border-spacing", "0"),
                                   ("padding","0"),
                                   ("border-collapse","collapse")]),
    dict(selector="td", props =[("text-align", "center"),
                                ("padding","0px"),
                                  ("font-family", "\"Lucida Console\", Courier, monospace"),
                                ("border-right","2px solid #000")]),
    dict(selector=".col0",props=[("background-color", "DarkOrange"),
                                 ("color", "White"),
                                 ("font-size", "120%"),
                                 ("padding-left", "2px"),
                                 ("text-align", "left"),
                                 ("font-family", "\"Times New Roman\", Times, serif")]),
    dict(selector=".col1,.col2,.col3", props = [("text-align","center")]),
    dict(selector="tr:nth-child(even)",props = [("background-color","#f2f2f2")]),
    dict(selector=".row_heading", props =[("border-right", "2px solid #000"),
                                ("font - size", "110 %"),
                                ("text-align","left"),
                                ("width", "5em"),
                                ("background-color","DarkOrange"),
                                ("color","White")]),
    dict(selector="caption", props=[("caption-side", "bottom"),
                                    ("color", "#bbb")]),
    dict(selector=".col_heading", props=[("font-size", "110%"),
                                              ("text-align", "center"),
                                              ("background-color", "DarkOrange"),
                                              ("color", "White"),
                                              ("border-right", "2px solid #000"),
                                              ("border-bottom","2px solid #000"),
                                              ("width", "8em"),
                                              ("text-align", "center")])
   ]
df_style_obj.set_table_styles(styles)
#df_style_obj.format("{:,.0f}")
df_style_obj.hide_index()
import re
#Render to a string first as we need to back-hack the table CSS:
table_as_html = (df_style_obj.render())
table_as_html = re.sub("#(.*?) table", r"#\1", table_as_html)
import matplotlib.pyplot as plt

# group_counts_df.columns =
# ["Product Class", "Number of Products", "Ingredients Present", "Ingredients Added Manually"]
graph_table = pd.DataFrame (group_counts,
              columns=["Product Class", "Parsed Automatically", "Ingredients Added Manually", "Absent"])


graph_table.index = group_counts_df.index
#Populate the table for graph:
graph_table["Product Class"] = group_counts_df["Product Class"]
graph_table["Parsed Automatically"] = group_counts_df["Ingredients Present"]# - group_counts_df["Ingredients Present"])
graph_table["Ingredients Added Manually"] = group_counts_df["Ingredients Added Manually"]
graph_table["Absent"] = (group_counts_df["Number of Products"] - \
                                    group_counts_df["Ingredients Present"] -
                                    group_counts_df["Ingredients Added Manually"])
print (graph_table)

#Plot the chart:
bar_colors = ["#80dd80", "#5555FF", "#888888"]
axis_gtp = graph_table.plot.bar(x="Product Class",
            y=["Parsed Automatically", "Ingredients Added Manually", "Absent"],
            stacked=True,
            title="Completeness of Ingredient List Datasets",
            figsize=(7,6),
            color=bar_colors)
#Tweak the axises:
axis_gtp.set_ylabel("Count")
axis_gtp.set_xlabel("Product")

plt.savefig(Ingredients_Status_fname)
plt.show(block=True)

print ("All done, bye-bye")


#Now write the file out:
file2 = open(html_output_file_name,"w+")
file2.write(table_as_html)
#For neatnees
file2.close()