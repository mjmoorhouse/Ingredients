"""
cleanRawDownloads.py

This cleans up the worse of the dross and duplication from the raw scraped data and places them into a 'cleaned'
directory.  Existing files are not overwritten.


The style used is more functional than Object Orientated: the same results could be achieved with (g)awk, sed and cut.

"""


def main():
    import os
    import sys
    print ("Loading Pandas and dependencies:")
    try:
        import pandas as pd
    except:
        sys.exit("Could not load pandas module - check installation and environment is active")

    #Set / Test the output directory; stop if it doesn't exist:
    outdir = os.getcwd()+"\\Cleaned"
    if not os.path.isdir(outdir):
        sys.exit("Could not find output directory: '{}'".format(outdir))
    print ("LOG: Outputing to:\t'" + outdir + "'")

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

    for CFile in range(0, N_CSVFiles):
        c_file_name = CSVList[CFile]
        c_file_ip_path = dataLocation + "\\Data\\" + c_file_name
        c_file_op_path = outdir + "\\" + c_file_name
        print ("Processing #{0} of {1}\t: '{2}'".format(CFile + 1, N_CSVFiles, c_file_name))
        #print ("From: '{}' into '{}'".format(c_file_ip_path, c_file_op_path))
        print ("Testing: '{}'".format(c_file_op_path))
        if os.path.exists(c_file_op_path):
            print ("Already exists, so skipping")
            continue
        print ("Processing into '{}'".format(c_file_op_path))


    #Do file work:
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
        c_file_name = CSVList[CFile]
        c_file_ip_path = dataLocation + "\\" + c_file_name
        c_file_op_path = outdir + "\\" + c_file_name
        print("Processing #{0} of {1}\t: '{2}'".format(CFile + 1, N_CSVFiles, c_file_name))
        raw_results_df = pd.read_csv(c_file_ip_path)
        print (raw_results_df.head())

if __name__ == '__main__':
    main()

