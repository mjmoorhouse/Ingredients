"""
Ingredients module: useful, common routines for general use including:

    get_CSS_table_styles_dictionary()  ; #Returns the dictionary containing the current CSS styles for

"""
import re

def get_CSS_table_styles_dictionary():
    styles = [
        dict(selector="table", props =[("border-spacing", "0"),
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
                                             ("text-align", "center"),
                                             ("foo", "bar")])
    ]
    return styles

def render_df_to_html(df_passed, caption=None):
    """
    Just render the Data frame passed to HTML and return it (hacking it so the styles work properly):

    :param df_passed: The Pandas dataframe to be rendered
    :param caption: Optional caprion for the table
    :return: a text string of HTML or None:
    """
    internal_df = df_passed.copy(deep=True)
    internal_df.fillna("")
    internal_styler = internal_df.style
    get_CSS_table_styles_dictionary()
    internal_styler.set_table_styles(get_CSS_table_styles_dictionary())
    #Truncate the weight column values to 0 d.p. for output
    internal_styler.format({'Weight':'{:g}'})

    internal_styler.hide_index()
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