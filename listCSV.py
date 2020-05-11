"""
listCSV.py
A very simple initial commit to test git connection
List all the CSV files in the directory -printing the CWD on the way past:
"""
import os
print ("Current WD: '{}'".format(os.getcwd()))
#Assume the path to the Data files is in the directory named "./Data"
dataLocation = os.getcwd()+"\\Data"
print ("Location of data files: {}".format(dataLocation))

#Use a list comprehension to get all the CSV - hence Data - files, then count them:
CSVList = [x for x in os.listdir(dataLocation) if x.endswith(".csv")]
N_CSVFiles = len(CSVList)
if N_CSVFiles >0:
    print("Are [{0}] Files: {1}".format(len(CSVList), CSVList))
else:
    print ("No CSV Files found")

#Do something more interesting - or at least pretend to:
for CFile in range(0,N_CSVFiles):
    CFile_Name = CSVList[CFile]
    print ("Processing #{0} of {1}\t: '{2}':".format(CFile+1,N_CSVFiles, CFile_Name))
