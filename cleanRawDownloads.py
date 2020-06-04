"""
cleanRawDownloads.py

This cleans up the worse of the dross and duplication from the raw scraped data and places them into a 'cleaned'
directory.  Existing files are not overwritten.

The style used is more functional than Object Orientated: the same results could be achieved with (g)awk, sed and cut.

Heavy use of Pandas from the dataframe operations.

"""
import re
import sys
import os

# Until we get these into a separate file:
columns_to_drop = ["web-scraper-order", "productsonpage",
                   "web-scraper-start-url", "nut-html", "description", "pages", "pages-href"]

new_column_order = ["id", "name", "product-href", "ingredients", "allergens", "weight", "comments"]
new_column_names = ["Product ID", "Product Name", "URL", "Ingredients", "Allergens", "Weight", "Comments"]

# Target: https://www.XXXX./groceries/en-GB/products/305983890 gives $1 = 305983890
sku_re = re.compile('\/(\d*)$')
contains_re = re.compile('(also )*([Cc]ontain)s* *(trace)*s* *(of)*:*')
contains_result_str = 'Contain:'
delimter_re = re.compile('(and )|(\& )')
delimter_result_str = ', '

weight_re = re.compile('(?P<weight>[\d.]+)(?P<units>[kK]*[Gg])')


def main():
    print("Loading Pandas and dependencies:")
    try:
        import pandas as pd
    except:
        sys.exit("Could not load pandas module - check installation and environment is active")

    # Set / Test the output directory; stop if it doesn't exist:
    outdir = os.getcwd() + "\\Cleaned"
    if not os.path.isdir(outdir):
        sys.exit("Could not find output directory: '{}'".format(outdir))
    print("LOG: Outputing to:\t'" + outdir + "'")

    # Do file work:
    print("Current WD: '{}'".format(os.getcwd()))
    # Assume the path to the Data files is in the directory named "./Data"
    dataLocation = os.getcwd() + "\\Data"
    print("Location of data files: {}".format(dataLocation))

    # Use a list comprehension to get all the CSV - hence Data - files, then count them:
    csv_list = [x for x in os.listdir(dataLocation) if x.endswith(".csv")]
    n_csv_files = len(csv_list)
    if n_csv_files > 0:
        print("Are [{0}] Files: {1}".format(len(csv_list), csv_list))
    else:
        print("No CSV Files found")

    # Do something more interesting - or at least pretend to:
    for c_file in range(0, n_csv_files):
        # Build the file paths - including .txt instead of .csv for the output file so it opens in Excel easier
        c_file_name = csv_list[c_file]
        c_file_ip_path = dataLocation + "\\" + c_file_name
        c_file_op_path = outdir + "\\" + c_file_name
        c_file_op_path = re.sub('\.csv$', '.txt', c_file_op_path)
        print("Processing #{0} of {1}\t: '{2}'".format(c_file + 1, n_csv_files, c_file_name))
        # Is the file new? (no if the output version exists already, so we skip it)s
        if os.path.exists(c_file_op_path):
            print("Already exists, so skipping")
            continue
        print("Processing into '{}'".format(c_file_op_path))

        # Read the data in:
        raw_results_df = pd.read_csv(c_file_ip_path)

        # Start our clean...many of these for loops could likely be converted to list comprehensions
        ######
        # 1) Standardise all columns on lower case:
        for c_column in raw_results_df.columns:
            raw_results_df = raw_results_df.rename(columns={c_column : str(c_column).lower()})

        # 2) Add a "Comments" column if one doesn't exist; otherwise preserve the existing one
        if not 'comments' in raw_results_df.columns:
            raw_results_df['comments'] = ''

        # 3) Drop the useless (for now) columns:
        #Probably this could be done with a list comprehension - but this is an improvements
        for c_column in columns_to_drop:
            if c_column in raw_results_df.columns:
                raw_results_df = raw_results_df.drop(c_column, axis=1)

        # 4) Standardise the 'product-href' column name (called 'ProductsonPage-href' if from a multi-page run)
        if 'productsonpage-href' in raw_results_df.columns:
            raw_results_df = raw_results_df.rename(columns={'productsonpage-href': 'product-href'})

        # 5) Extract the SKU / Product ID from the product URL and insert it as the first column:
        raw_results_df.insert(0, 'id', raw_results_df['product-href'].str.extract(sku_re))

        # 6) Re-order & retitle columns:
        raw_results_df = raw_results_df[new_column_order]
        raw_results_df.columns = new_column_names

        # 7) Standardise to "May contain:" in the Allergens columns
        raw_results_df['Allergens'] = raw_results_df['Allergens'].apply(clean_allergens)

        # 8) Convert all weights to grams: (kg = g * 1000)
        raw_results_df['Weight'] = raw_results_df['Weight'].apply(convert_weight)

        # 9) Clean the Ingredients up a bit:
        raw_results_df['Ingredients'] = raw_results_df['Ingredients'].apply(clean_ingredients)

        # 10) Now save the cleaned version of the file:
        raw_results_df.to_csv(c_file_op_path, sep='\t', index=False)

def clean_ingredients(ingredients_list):
    """
    Mostly applies regexs to remove the worse of the non-standard markup making keyword searches easier.
    Very similar to Clean_Allergen() in concept and operation

    In brief the Regexs:
    *) Remove INGREDIENTS: or similar parsing artifacts
    *) Remove leading spaces
    *) Remove leading trailing spaces and full stops
    *) Remove spaces around commas
    *) Remove ingredient percentages (i.e. beef (12%)) -> beef
    *) Convert most brackets [] & () in lists to commas
    *) Remove "(from " allergen markup (i.e. Lactose (from Milk) -> Lactose (Milk) - should leave only left bracket
    *) Remove "(in varying... proportions)"
    *) Remove "(of which...)"
    *) Remove ("From sustainable organic production")
    *) Remove trailing commas, full stops, spaces
    *) Remove all ":" and "*"
    *) Remove "LIST:\n\n\n" noise:

    """
    # Check whether it is a string to attempt matching (might be NaN) - return if not
    if not isinstance(ingredients_list, str):
        return ""
    #print ("Before\t: {}"*.format(ingredients_list))
    #Apply the regex to clean out "Ingredients:" type things:
    ingrid_re = re.compile('(Ingredients)|(INGREDIENTS) *(LIST)*:*', re.IGNORECASE)
    ingredients_list = re.sub(ingrid_re, "", str(ingredients_list))
    ingredients_list = re.sub(re.compile("LIST:* *[\n\r]+"), "", ingredients_list)
    #Also spaces before / after commas: just annoying:
    ingredients_list = re.sub(re.compile(" ,|, "), ",", ingredients_list)
    #Any percentages we suppress: Beef Mince (12%)
    ingredients_list = re.sub(re.compile(" *\([\d.]+%\)"), "", ingredients_list)

    #Convert brackets to commas: , Sundried Tomato Sauce (2%) [Sundried Tomatoes, Toma...
    ingredients_list = re.sub(re.compile(" *(\[).*?,"), ",", ingredients_list)
    ingredients_list = re.sub(re.compile("(\])"), ",", ingredients_list)
    ingredients_list = re.sub(re.compile("\]"), ",", ingredients_list)
    #Convert opening brackets to commas: ...r, Beef Powder (Cooked Beef Fat,...
    ingredients_list = re.sub(re.compile(" *?(\()(?!from)([\w ]+?),"),",\g<2>,", ingredients_list)
    # Same - but the end bracket ...High Oleic Sunflower Oil),..
    ingredients_list = re.sub(re.compile(",(?!from)([\w ]+?)\),"), ",", ingredients_list)
    #Decompose lists into their component parts:
    #ingredients_list = re.sub(re.compile("(.*? *\()(?:.*?,.*?\))"), "", ingredients_list)
    # Suppress common phrases:
    #   (in varying proportions - XXX, YYY, ZZZ)
    ingredients_list = re.sub(re.compile("(\(in varying proportions *-*) *",re.IGNORECASE), "", ingredients_list)
    #   (from XXX)
    ingredients_list = re.sub(re.compile("(\(from )(\w+)\)",re.IGNORECASE), "(\g<2>)", ingredients_list)
    #(of which xxx is Blah):
    ingredients_list = re.sub(re.compile("\(of which.{0,6}? is.{0,15}?\)",re.IGNORECASE),"", ingredients_list)

    #(*From Sustainable Organic production)
    ingredients_list = re.sub(re.compile("From Sustainable Organic production",re.IGNORECASE), "", ingredients_list)
    #Final cleanup of basic punctuation
    ingredients_list = re.sub(re.compile(",$"), "", ingredients_list)
    ingredients_list = re.sub(re.compile(",{2,}"), ",", ingredients_list)
    # Remove any leading spaces or trailing 'full stops', spaces, colons etc:
    ingredients_list = re.sub(re.compile("^ *?"), "", ingredients_list)
    ingredients_list = re.sub(re.compile("\ *\.$"), "", ingredients_list)
    ingredients_list = re.sub(re.compile("\*"), "", ingredients_list)
    """
    
    """
    #print ("After\t: {}".format(ingredients_list))
    return ingredients_list

def convert_weight(weight):
    """
    Filters the worst of the junk from the weight column returning "" on a bad match for grams or kilograms (g or kg)
    Also converts kilo grams to grams and returns this value.
    Is case insensitive for G == g or KG == kg == kG typically, but check the current pattern used:
    expect it to be similar to this:
    weight_re = re.compile('(?P<weight>[\d.]+)(?P<units>[kK]*[Gg])')
    """
    # Check whether it is a string to attempt matching (might be NaN) - return if not
    if not isinstance(weight, str):
        return ""

    # Try the match: (hoping to get the numbers and units split from each other that convert to a float)
    match_result = weight_re.search(weight)
    return_weight = 0.0
    try:
        return_weight = float(match_result.group("weight"))
    except:
        return ""

    if match_result != None:
        # So we matched a weight, was it g or kg?
        # If kg x 1000 and return to rounded gram
        if re.match("[Kk]", match_result.group("units")):
            return (int(return_weight * 1000))
        else:
            return int(return_weight)
    else:
        # If we don't recognise the weight - return empty:
        return ""


def clean_allergens(al_string):
    """
    Remember these - check the program start (or config file if implemented) need setting defined.
    (these can't be passed easily)
    Neither of these are perfect, but clean up the worst abuses on defined language:
    contains_re = re.compile('(?:also )*[Cc](?:ontain)*s* *(?:trace)*s* *(?:of)*:*')
    contains_result_str = 'Contain: '
    delimter_re = re.compile('(?:and *)|(?:\& *)')
    delimter_result_str = ", "
    Extra spaces and full stops are removed also

    """
    # Reality check: this is a string we were passed correct?  Return empty if not:
    if not isinstance(al_string, str):
        return ""
    # Run the general regexs: first cleans up "Contains also:" the second the list of Allergens;
    # (we aren't interested in logic here, just running them)
    al_string = re.sub(contains_re, contains_result_str, str(al_string))
    al_string = re.sub(delimter_re, delimter_result_str, str(al_string))

    # Basic punctuation cleanup/out:
    al_string = re.sub(re.compile(', *'), ",", str(al_string))
    al_string = re.sub(re.compile('\.$'), "", str(al_string)) #Not working?  "GardenPeas." is coming through?
    al_string = re.sub(re.compile(': *'), ": ", str(al_string))

    return al_string

#This construct to allow functions in any order:
if __name__ == '__main__':
    main()
