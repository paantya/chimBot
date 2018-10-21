#!/usr/bin/python3

import pandas
import xlrd
import sys
import os

bgErr = 0.01
fOutput = open('output.txt', 'w')

def sts(file):
    df = pandas.read_excel(file,header = None)

    A = df[0].values
    B = df[1].values
    minB = min(B)
    maxB = max(B)

    bgs = [i for i in B if i <= (minB + bgErr)]
    bg = sum(bgs) / len(bgs)
    
    BdBG = B - bg
    
    def B300(x):
        k = 0
        while x[k]<300:
            k+=1
        return k

    def BBg(x,bg):
        k = 0
        while x[k] <= (bg + bgErr):
            k+=1
        return k

    trs = [(BdBG[i+1]+BdBG[i])*(A[i+1]-A[i])/2 for i in range(BBg(B,bg),B300(A))]
    trSum = sum(trs)
    fOutput.write("{}: \ntrsum = {},\t maxB = {}, sr = {}\n".format(file,trSum,maxB, bg))
    print("{}: \ntrsum = {},\t maxB = {}, sr = {}".format(file,trSum,maxB, bg))


if (len (sys.argv) > 1):
    sts(sys.argv[1])
else:    
    files_xls = sorted([file for file in os.listdir() if file.rfind(".xls")!= -1])

    for file in files_xls:
        sts(file)

input("Done!\nPress Enter")
