"""

"""



def increment_dict(tally_dict, level_1_key, level_2_key):
    """
    Because in Python we have dictionaries that don't auto-vivify their sub level keys
    (Perl has to be better at something)
    :param tally_dict: the dictionary to increment
    :param level_1_key: dict[THIS ONE][]
    :param level_2_key: dict[][THIS ONE]
    :return:
    """
    #Initialise the base (1st level key) if it doesn't exist:
    if tally_dict.get(level_1_key) == None:
        print ("Base key doesn't exist; so adding...")
        tally_dict[level_1_key] = dict()

    #Initilise the second level key now?
    if tally_dict.get(level_1_key).get(level_2_key) == None:
        tally_dict[level_1_key][level_2_key] = 0
        print ("Key init: {}".format(tally_dict[level_1_key][level_2_key]))

    print ("Now (should be both keys): '{}'".format(tally_dict))

    #Increment the tally now both keys levels exist:
    tally_dict[level_1_key][level_2_key] = tally_dict[level_1_key][level_2_key] + 1
    print ("After increment: '{}'".format(tally_dict))
    return 0


#Main program start proper:
tally =dict()
print ("When empty: '{}'".format(tally))
increment_dict(tally,"A","2")
print ("Tally: '{}'".format((tally)))
increment_dict(tally,"A","2")
print ("Tally: '{}'".format((tally)))
increment_dict(tally,"B","2nd")
increment_dict(tally,"B","2nd")
increment_dict(tally,"B","2nd")
increment_dict(tally,"B","2nd")
print ("Tally: '{}'".format((tally)))

