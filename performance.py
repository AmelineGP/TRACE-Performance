'''import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import argparse
import json
import uuid
import time'''
import os
'''import re
import geojson
from geojson import Feature, Point, FeatureCollection, Polygon
import pdb'''


def openlogfile(name):
    file_path="./"
    file_name=name
    complete_list = os.listdir(file_path)
    content=[]
    lname=len(file_name)
    for file in complete_list:
        if file[0:lname]==file_name:
            print(file," log file will be used for the test")
            writePerfFile(PERF_FILE,str(file)+" log file will be used for the test")
            f=open(file,'r')
            if f.mode=="r":
                content.append(f.readlines())

    return content

def writePerfFile(file,line):
    print(line)
    f=open(file,'w')
    if f.mode=="w":
        f.write(line)
    return

def getLineTime(text):
    dict=[]
    linenum=0
    for logfile in text:
        for line in logfile:
            try:
                timetext=line[0:12]
                timesec=float(timetext[0:2])*360+float(timetext[3:5])*60+float(timetext[6:8])+float(timetext[9:12])/1000
                dict.append({'id':linenum,"timetext":timetext,"timesec":timesec,"text":line[20:]})
                linenum+=1
            except:
                #print("No time in the line:", line)
                continue
    return dict

def getTimeLogWrittenBefore(log,str,start,end): #look for the string in the log line from start to end
    str_t=0
    for line in log[start:end]:
        if str in line["text"]:
            str_t=line["timesec"]

    return str_t



def getDelay(log,action_str,result_str):
    action=True #set to 'true' when we are looking for the log corresponding to the input, and 'fqlse' when we are looking for the one for the output

    action_t=0 #time of the action
    result_t=0 #time of the result

    delays=[]
    for line in log:
        if action :
            if len(action_str)==1 and action_str[0] in line["text"]:#we are looking for one simple string
                print("action:",line)
                action_t=line["timesec"]
                action=False
                continue
            if len(action_str)>1 and action_str[0] in line["text"]: #we are looking for two strings
                action_t=getTimeLogWrittenBefore(log,action_str[1], line["id"]-20,line["id"])#looking for the second string written
                if action_t==0:continue #the second string was not found
                action=False
                continue
        if action==False:
            if len(result_str)==1 and result_str[0] in line["text"]:#we are looking for one simple string
                print("result:",line)
                action=True
                result_t=line["timesec"]
                delays.append(result_t-action_t)
                action_t=result_t=0
                continue
            if len(result_str)>1 and result_str[0] in line["text"]: #we are looking for two strings
                result_t=getTimeLogWrittenBefore(log,result_str[1], line["id"]-20,line["id"])#looking for the second string written
                action=True
                if action_t==0:continue #the second string was not found
                result_t=line["timesec"]
                delays.append(result_t-action_t)
                action_t=result_t=0



    return delays

def delayRoleOpening(logs):
    avDelay=0 #average delay of role opening
    for role in ROLE_NAMES:
        delays=getDelay(logs,[ROLE_OPEN_ACTION+role,ROLE_OPEN_ACION_2],[ROLE_OPEN_RESULT+role])
        if len(delays)>0: #if there is at least one time calculated
            writePerfFile(PERF_FILE,"Delays to open the role "+role+": "+str(delays))
            for delay in delays:
                avDelay=(avDelay+delay)/2
    writePerfFile(PERF_FILE,"the average delay for role opening is:"+ str(avDelay))

    return

'''def delayRoleChange(logs):
    avDelay=0 #average delay of role opening
    for role in ROLE_NAMES:
        delays=getDelay(logs,[role+ROLE_CHANGE_ACTION],[ROLE_OPEN_RESULT+role])
        if len(delays)>0: #if there is at least one time calculated
            writePerfFile(PERF_FILE,"Delays to activate the role "+role+": "+str(delays))
            for delay in delays:
                avDelay=(avDelay+delay)/2
    writePerfFile(PERF_FILE,"the average delay to activate an already open role is:"+ str(avDelay))

    return'''

##### Global Variable#######
ROLE_NAMES={'CLD_1','SPVR','GRO_1','GRO_2','ADC_1','ADC_2','ADC_3','DEP_1','DEP_2','FIN_1','FIN_2','FIN_3','APW_1','APW_2'}
ROLE_OPEN_ACTION="UIS:  activation of Role by client "
ROLE_OPEN_RESULT= "set role on front: "
ROLE_OPEN_ACION_2="Button OK_BUTTON pressed."
ROLE_CHANGE_ACTION=" change status ACTIVE_AND_SHOWN"

PERF_FILE='performance.txt'
##### Global Variable#######

logs=openlogfile('client')
dictLogs=getLineTime(logs)
delayRoleOpening(dictLogs)
#delayRoleChange(dictLogs)
