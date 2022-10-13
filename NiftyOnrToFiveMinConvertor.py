import csv
import os
import sys
from glob import glob


def convert(rawfile,outputFile):

    with open(rawfile, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    result=[]
    row_5min=[]
    row_count,open_price,close,high,low=0,0,0,0,0
    for row in data:
        if row[2]== '09:08' or row[2]== '15:31' or row[2]== '15:32':
            continue
        row_count+=1

        if row_count==1:
            open_price=row[3]
            high=row[4]
            low=row[5]
            continue

        if high < row[4]:
            high=row[4]
        if low > row[5]:
            low=row[5]
        
        if row_count == 5:
            close=row[6]
            row_5min=[row[0],row[1],row[2],open_price,high,low,close]
            result.append(row_5min)
            row_count,open_price,close,high,low=0,0,0,0,0
        
    with open(outputFile,'w+',newline='')as file :
        writer = csv.writer(file)
        writer.writerows(result)
        

def createOutputFile(filename:str):
    name=filename.split('.')[0]
    name+=' 5mins.txt'
    folder_path, file_name = "/".join(name.split("/")[:-1]), name.split("/")[-1]
    return folder_path + "/output/" + file_name


def createOutputDirectory(input_path):
    os.makedirs(input_path + "/output/")


if __name__ == '__main__':
    input_path = sys.argv[1]
    createOutputDirectory(input_path)
    for a_file in glob(input_path + "*.txt"):
        if a_file[-4:] == ".txt" and 'NIFTY' in a_file:
            output_file = createOutputFile(a_file)
            print(a_file, output_file)
            convert(a_file, output_file)
