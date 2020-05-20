"""
assessDataCompleteness.py

Supplied with the make data matrix this prepares various summaries of the data completeness
This includes assessing which ingredients are missing and which are noted as being corrected.

The markup tag denoting ingredients have been entered manually it:
manual_ingredients_tag = "Manual Ingredients"
n_corrected_ingredients = int(this_group["Comments"].str.count("Manual Ingredients").sum())

"""
import pandas as pd

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
#Group the data by 'source' (i.e. food type)
grouped_by_source = products_df.groupby(['Source'])

#Split into groups for easy iteration (key: object reference to group)
groups = dict (list(grouped_by_source))
#Main results store; we create a DF from this ultimately
group_counts = []

#For all the groups:
for c_group in groups:
    #Get the group we are interested in along with columns: Ingredients & Comments
    this_group = grouped_by_source[["Ingredients", "Comments"]].get_group(c_group)

    #Count the ingredients and determine which we have data for:
    n_ingredients = len(this_group["Ingredients"])
    missing_ingredients = this_group["Ingredients"].isna().sum()
    complete_ingredients = n_ingredients - missing_ingredients

    #Count the comments noting manual entry of ingredients "Manual Ingredients"
    n_corrected_ingredients = int(this_group["Comments"].str.count("Manual Ingredients").sum())
    print ("Complete(of which corrected): total : \t{}\t({}) : \t{}".format(complete_ingredients, n_corrected_ingredients,
                                                                        n_ingredients))
    #Note down this information into a list (cf. DataFrame - which we build from the list ultimately for performance)
    group_counts.append({"Name" : str(c_group),
                         "Total Products" : int(n_ingredients),
                         "Ingredients" : int(complete_ingredients),
                         "Corr. Ingredients" : int(n_corrected_ingredients)})

group_counts_df = pd.DataFrame (group_counts,
                                columns=["Name", "Total Products", "Ingredients", "Corr. Ingredients"]  )

#Printout locally prior to pretty graphing:
print ("Ultimately:")
print (group_counts_df)
