# Illumio

This is the take home assignment for Illumio. 

## Problem Statement
Write a program that can parse a file containing flow log data and maps each row to a tag based on a lookup table. The lookup table is defined as a csv file, and it has 3 columns, dstport,protocol,tag.   The dstport and protocol combination decide what tag can be applied. 

The program should generate an output file containing the following: 

- Count of matches for each tag, sample o/p shown below 
- Count of matches for each port/protocol combination 

## Solution
This solution is implemented in Python 3.

Assumptions:
- The input file consists of AWS VPC flow logs in default format (version 2 only). If log data from version 3 and above are added, the program will fail.
- Since the problem statement states that the log data is in default formast version 2, the protocol will be in number format, so a lookup file from the official AWS website has been added to allow easier mapping. It can be found here: https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
- The lookup file is in the same directory as the program file.
- The lookup file is in csv format, the input and output files are stored as plain .txt files.
- The protocol table downloaded from AWS is also in csv format.

## How to run
1. Clone the repository
2. Run the program in the root directory with the following command:
```
python main.py <lookup_table> <input_file> <output_file>
```