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
                                  ("font-family", "\"Lucida Console\", Courier, monospace")]),
    dict(selector=".col0",props=[("background-color", "DarkOrange"),
                                 ("color", "White"),
                                 ("font-size", "120%"),
                                 ("text-align", "left"),
                                 ("border-right", "2px solid #000"),
                                 ("font-family", "\"Times New Roman\", Times, serif")]),
    dict(selector=".col1,.col2,.col3", props = [("text-align","center")]),
    dict(selector="tr:nth-child(even)",props = [("background-color","#f2f2f2")]),
    dict(selector=".row_heading", props =[("border-right", "2px solid #000"),
                                ("font - size", "120 %"),
                                ("text-align","left"),
                                ("width", "5em"),
                                ("background-color","DarkOrange"),
                                ("color","White")]),
    dict(selector="caption", props=[("caption-side", "bottom"),
                                    ("color", "#bbb")]),
    dict(selector=".col_heading", props=[("font-size", "120%"),
                                              ("text-align", "center"),
                                              ("background-color", "DarkOrange"),
                                              ("color", "White"),
                                              ("border-bottom", "2px solid #000"),
                                              ("width", "10em"),
                                              ("text-align", "center")])
   ]
df_style_obj.set_table_styles(styles)
#df_style_obj.format("{:,.0f}")
df_style_obj.hide_index()
print (df_style_obj.render())
file2 = open(r"table_example.html","w+")
file2.write(df_style_obj.render())
file2.close()
#print (df.style)