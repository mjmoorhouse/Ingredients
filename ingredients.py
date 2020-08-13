"""
Ingredients module: useful, common routines for general use including:

    get_CSS_table_styles_dictionary()  ; #Returns the dictionary containing the current CSS styles for

"""
import re
import pandas as pd

def example_product_list():
    """
    Really simple helper function to fix/fake the search terms:
    - but something to demonstrate operation on i
    """
    #return ["Salt"]
    return ["milk", "whey", "Lactose","Salt","'Salt'"]
    #return ["milk","Salt"]

def get_CSS_table_styles_dictionary():
    styles = [
        dict(selector="table", props =[("table-layout","fixed"),
                                       ("width","100%"),
                                       ("border-spacing", "0"),
                                       ("padding","0"),
                                       ("border-collapse","collapse")]),
        dict(selector="td", props =[("text-align", "center"),
                                    ("padding","0px"),
                                    ("font-family", "\"Lucida Console\", Courier, monospace"),
                                    ("border-right","2px solid #000")]),
        dict(selector="span.ingtxt", props=[("background-color", "Yellow"),
                                      ("color", "Blck"),
                                      ("font-weight","bold"),
                                      ("font-family", "\"Lucida Console\", Courier, monospace")]),
        dict(selector=".col0",props=[("background-color", "DarkOrange"),
                                     ("color", "White"),
                                     ("font-size", "120%"),
                                     ("padding-left", "2px"),
                                     ("text-align", "left"),
                                     ("width","6em"),
                                     ("font-family", "\"Times New Roman\", Times, serif")]),
        dict(selector="tr:nth-child(even)",props = [("background-color","#f2f2f2")]),
        dict(selector=".row_heading", props =[("border-right", "2px solid #000"),
                                              ("font - size", "110 %"),
                                              ("text-align","left"),
                                              ("width", "10em"),
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
                                             ("text-align", "center")]),
        #Product ID we have done above and is very special being the row header, but set the columns widths
        dict(selector=".col1", props=[("width", "20em")]), #Product Name
        dict(selector=".col2", props=[("width", "3em")]), #URL
        dict(selector=".col3", props=[("width", "10em")]), #Allergens
        dict(selector=".col4", props=[("width", "4em")]),  # Weight
        dict(selector=".col5 .col6", props=[("width", "10em")]), # Source
        dict(selector=".col5.data .col6.data", props=[("font-size", "75%")]),
        # col 7 and higher are ingredient matches:...so we create this tag to let the Python code to fill them in:
        dict(selector=".COL_REPLACE_TAG.data", props=[("background-color", "oldlace")])  # Weight
        # dict(selector=".col3.data", props=[("font-size", "50%"),
    ]
    return styles


def get_CSS_table_styles_dictionary():
    styles = [
        dict(selector="table", props =[("table-layout","fixed"),
                                       ("width","100%"),
                                       ("border-spacing", "0"),
                                       ("padding","0"),
                                       ("border-collapse","separate")]),
        dict(selector="td", props =[("text-align", "center"),
                                    ("padding","0px"),
                                    ("font-family", "\"Lucida Console\", Courier, monospace"),
                                    ("border-right","2px solid #000")]),
        dict(selector="span.ingtxt", props=[("background-color", "Yellow"),
                                      ("color", "Blck"),
                                      ("font-weight","bold"),
                                      ("font-family", "\"Lucida Console\", Courier, monospace")]),
        dict(selector=".col0",props=[("background-color", "DarkOrange"),
                                     ("color", "White"),
                                     ("font-size", "120%"),
                                     ("padding-left", "2px"),
                                     ("text-align", "left"),
                                     ("width","6em"),
                                     ("font-family", "\"Times New Roman\", Times, serif")]),
        dict(selector="tr:nth-child(even)",props = [("background-color","#f2f2f2")]),
        dict(selector=".row_heading", props =[("border-right", "2px solid #000"),
                                              ("font - size", "110 %"),
                                              ("text-align","left"),
                                              ("width", "10em"),
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
                                             ("text-align", "center")])
    ]
    return styles

def get_table_id(html_table):
    """
    parses the table id out of text strings like this: 
    <style  type="text/css" >
    #T_26afb0c8_a753_11ea_844b_28f10e424db7 {
    
    returns either the ID string or empty 
    """
    # First get the Weird Table ID:
    URL_colindex_groups = re.search(r'>\n\s+#(.*?)\s+{', html_table)
    if URL_colindex_groups:
        return URL_colindex_groups.group(1)
    else:
        return ""

def render_df_to_html(df_passed, caption=None):
    """
    Just render the Data frame passed to HTML and return it (hacking it so the styles work properly):

    :param df_passed: The Pandas dataframe to be rendered
    :param caption: Optional caption for the table
    :return: a text string of HTML or None:
    """
    #Take a copy to work on (deep ensures it is a 'copy by value' so we can't hurt the original)
    internal_df = df_passed.copy(deep=True)
    #Remove the index column:
    #internal_df.reset_index(drop=True, inplace=True)
    if "index" in internal_df.columns:
        internal_df.drop(columns="index",inplace=True)

    #As we use this a lot:
    internal_styler = internal_df.style
    #Set the table styles to the default
    internal_styler.set_table_styles(get_CSS_table_styles_dictionary())

    #Truncate the numeric column values to 0 d.p. for integer output - this includes the Product ID
    #Cache the types as a list specifically (in use we only care about the number...but OK)
    column_types = list(internal_df.dtypes)
    print ("Column types are: '{}'".format(column_types))
    # print ("Column names are: {}".format(internal_df.columns))
    #Iterate through these: - just a little too complicated for a neat list comprehension:
    style_dict = dict()
    for c_col_indx in range(0,len(column_types)):
        c_col_type = column_types[c_col_indx]
        col_name = internal_df.columns[c_col_indx]
        print ("Column {} has type {}".format(col_name,c_col_type))
        # Is the column flagged as a integer?
        if c_col_type == "int64" or c_col_type == "Int64":
            print ("Column '{}' to change to *integer*".format(col_name))
            style_dict[col_name]='{:.0f}'
        # Is the columne flagged as a float (if so: allow a couple of Dec. Places)
        if c_col_type == "float64":
            print ("Column '{}' changed to 2 d.p. *float*".format(col_name))
            style_dict[col_name]='{:.2f}'
        if c_col_type == "O":
            print ("Column '{}' changed to *general* as mixed".format(col_name))
            style_dict[col_name]='{:}'
    internal_styler.format(style_dict,  na_rep='')
    print ("Styles being applied are: {}".format(style_dict))
    #Hide the index column:
    internal_styler.hide_index()

    #If there is a coption, set it:
    if caption != None:
        internal_styler.set_caption(caption)

    # Render to a string first as we need to back-hack the table CSS (yuck, yuck):
    table_as_html = hack_CSS_table(internal_styler.render())
    return table_as_html

def write_item_to_file(text, out_fname):
    """
    This is a simple file output routine that hides the exception handling away.
    :param text: String to write out
    :param out_fname: the file name to do so:
    :return: non-zero on failure
    """
    # Now write the file out as HTML
    try:
        file2 = open(out_fname, "w+")
        file2.write(text)
        # For neatness
        file2.close()
    except:
        return 1
    return 0

def build_ingredient_search_regex (term = None):
    """
    Handles the building of Regexs with surrounding '' to mean exact match or a liberal just-match-somewhere:
    :param term:
    :return: a regex object, fully built is ready to apply with a construct like:



    Typical usage:
    result = search_re.search(c_ingredient)

    or

    match_bool_array = (passed_df[search_in_column].str.match(search_re))
    """
    #Simple param check:
    if term == None:
        return None
    # Should we use exact matching or partial matching: (Yes: if the the target in enclosed in ' ie. 'Salt')
    if re.match(r"^'.*?'$", term):
        # i.e. exact match:
        local_re = re.compile(str('^' + term[1:-1] + '$'), re.IGNORECASE)
    else:
        # Allow partial, fancy matches:
        local_re = re.compile('(?<![(])' + term + '(?![)])', re.IGNORECASE)
    return local_re

def match_df_column(passed_df = None, search_in_column = None, ingredient = None):
    """
    When called with a dataframe, a column name and an ingredient it returns the sub-set dataframe with matches to
    that ingredient.
    On failure, returns none.  A check is done for the existence of the column in the df - returns none if not found.

    If the ingredient is surrounded in '' then an exact match is required.
    Typical useage:
    interesting_stuff_df = ind.match_df_column(counts_df, 'Ingredient', c_target_ingredient)

    :param df_passed: The dataframe to be subset
    :param column: The column in the df to subset
    :param ingredient: The ingredient tag - will be converted into a Regex
    :return: a subset dataframe or None on failure
    """
    # Basic parameter checking: did we get a Dataframe and two strings?
    if not (isinstance(passed_df, pd.DataFrame)
            and isinstance(search_in_column, str)
            and isinstance(ingredient, str)):
        return None
    search_re = build_ingredient_search_regex(ingredient)
    # This is an intermediate step: if you want to see the matching effects:
    match_bool_array = (passed_df[search_in_column].str.match(search_re))
    # print ("Number of matches of '{}' is '{}'; details:\n'{}'".
    #        format(ingredient, sum(match_bool_array), match_bool_array))
    # Hence sub-set of dataframe is:

    # Select based on the Boolean opperation for inspection purposes:
    subset_def = passed_df[match_bool_array]

    return subset_def

def write_df_to_pretty_table(df_passed, out_fname, caption=None):
    """
    Pass a dataframe and a filename and this routine writes it to the file system.
    It calls the rendering routine - that also hacks the resultant HTML too.
    """
    table_as_html = render_df_to_html(df_passed, caption=caption)
    if write_item_to_file(table_as_html,out_fname):
        return 1
    else:
        return 0

def hack_CSS_table (css):
    """
    Swaps over the location of the table tag and the CSS ID
    "# CSSIDandlongwithit table {"
    """
    return (re.sub("#(.*?) table", r"#\1", css))