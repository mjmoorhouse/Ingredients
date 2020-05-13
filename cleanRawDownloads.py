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
columns_to_drop = ["web-scraper-order", "ProductsonPage",
                   "web-scraper-start-url", "Nut-HTML", "Description", "Pages", "Pages-href"]

new_column_order = ["ID", "name", "ProductsonPage-href", "Ingredients", "Allergens", "weight"]
new_column_names = ["Product ID", "Product Name", "URL", "Ingredients", "Allergens", "Weight"]

# new_column_order = ["ID", "name", "ProductsonPage-href", "Ingredients", "Allergens", "weight"]
# new_column_names = ["Product ID", "Product Name", "URL", "Weight", "Ingredients", "Allergens"]
# Target: https://www.tesco.com/groceries/en-GB/products/305983890 gives $1 = 305983890
SKU_re = re.compile('\/(\d*)$')
contains_re = '(also )*([Cc]ontain)s* *(trace)*s* *(of)*:*'
contains_result_str = 'Contain:'
delimter_re = '(and )|(\& )'
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
    CSVList = [x for x in os.listdir(dataLocation) if x.endswith(".csv")]
    N_CSVFiles = len(CSVList)
    if N_CSVFiles > 0:
        print("Are [{0}] Files: {1}".format(len(CSVList), CSVList))
    else:
        print("No CSV Files found")

    # Do something more interesting - or at least pretend to:
    for CFile in range(0, N_CSVFiles):
        #Build the file paths - including .txt instead of .csv for the output file so it opens in Excel easier
        c_file_name = CSVList[CFile]
        c_file_ip_path = dataLocation + "\\" + c_file_name
        c_file_op_path = outdir + "\\" + c_file_name
        c_file_op_path = re.sub('\.csv$','.txt', c_file_op_path)
        print("Processing #{0} of {1}\t: '{2}'".format(CFile + 1, N_CSVFiles, c_file_name))
        #Is the file new? (no if the output version exists already, so we skip it)s
        if os.path.exists(c_file_op_path):
            print("Already exists, so skipping")
            continue
        print("Processing into '{}'".format(c_file_op_path))


        #Read the data in:
        raw_results_df = pd.read_csv(c_file_ip_path)
        #Start our clean...
        ######
        # 1) Drop the useless (for now) columns:
        raw_results_df = raw_results_df.drop(columns_to_drop, axis=1)

        # 2) Extract the SKU / Product ID from the product URL and insert it as the first column:
        raw_results_df.insert(0, 'ID', raw_results_df['ProductsonPage-href'].str.extract(SKU_re))

        # 3) Re-order & retitle columns:
        raw_results_df = raw_results_df[new_column_order]
        raw_results_df.columns = new_column_names

        # 4) Standardise to "May contain:" in the Allergens columns
        raw_results_df['Allergens'] = raw_results_df['Allergens'].apply(Clean_Allergen)

        # 5) Convert all weights to grams: (kg = g * 1000)
        raw_results_df['Weight'] = raw_results_df['Weight'].apply(Convert_Weight)

        #Now save the new file:
        #df.to_csv('new_file.csv', sep='\t', index=False)
        raw_results_df.to_csv(c_file_op_path, sep='\t', index=False)
        #df.to_csv(c_file_op_path, sep='\t', index=False)

def Convert_Weight(weight):
    """
    Filters the worst of the junk from the weight column returning "" on a bad match for grams or kilograms (g or kg)
    Also converts kilo grams to grams and returns this value.
    Is case insensitive for G == g or KG == kg == kG typically, but check the current pattern used:
    expect it to be similar to this:
    weight_re = re.compile('(?P<weight>[\d.]+)(?P<units>[kK]*[Gg])')
    """
    #Check whether it is a string to attempt matching (might be NaN) - et
    if not isinstance(weight, str):
        return ""

    #Try the match: (hoping to get the numbers and units  split from each other
    match_result = weight_re.search(weight)
    return_weight = 0
    if match_result != None:
        #So we matched a weight, was it g or kg?
        if re.match("[Kk]",match_result.group("units")):
            return(match_result.group("weight")*1000)
        else:
            return match_result.group("weight")
    else:
        # If we don't recognise the weight - return empty:
        return ""



def Clean_Allergen(al_string):
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
    #Reality check: this is a string we were passed correct?  Return empty if not:
    if not isinstance(al_string, str):
        return ""
    # Run the general regexs: first cleans up "Contains also:" the second the list of Allergens;
    #(we aren't interested in logic here, just running them)
    al_string = re.sub(re.compile(contains_re), contains_result_str, str(al_string))
    al_string = re.sub(re.compile(delimter_re), delimter_result_str, str(al_string))
    #Basic punctuation cleanup/out:
    al_string = re.sub(re.compile(' *, *'), ",", str(al_string))
    al_string = re.sub(re.compile('\.$'), "", str(al_string))
    al_string = re.sub(re.compile(': *'), ": ", str(al_string))
    print (al_string)
    return al_string


if __name__ == '__main__':
    # contains_result_str = "Fluffy"
    # al_string = re.sub(r"Contains",  contains_result_str, "Contains Nothing")
    # print ("Result: '{}'".format(al_string))
    # sys.exit(0)
    main()
