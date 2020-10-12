'''import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import argparse
import json
import uuid'''
import time
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
            writePerfFile(PERF_FILE,str(file)+" log file will be used for the test")
            f=open(file,'r')
            if f.mode=="r":
                content.append(f.readlines())

    return content

def writePerfFile(title,line):
    print(line)
    file=title+"_"+time.strftime("%Y%m%d")+".txt"
    f=open(file,'a')
    if f.mode=="a":
        f.write(line+"\n")
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

def allValInstring(values,str):
    for val in values:
        if val not in str: return False
    return True


def getDelay(log,action_str,result_str,action_str2='',result_str2=''):
    action=True #set to 'true' when we are looking for the log corresponding to the input, and 'fqlse' when we are looking for the one for the output

    action_t=0 #time of the action
    result_t=0 #time of the result

    delays=[]
    for line in log:
        if action :
            if allValInstring(action_str,line["text"]):
                if action_str2=='':  #we are looking for a string containing all the strings in action_str
                    action_t=line["timesec"]
                    action=False
                    continue
                if action_str2!='': #we are looking for two strings
                    action_t=getTimeLogWrittenBefore(log,action_str2, line["id"]-20,line["id"])#looking for the second string written
                    if action_t==0:continue #the second string was not found
                    action=False
                    continue
        if action==False:
            if allValInstring(result_str,line["text"]):
                if result_str2=='':#we are looking for one simple string
                    action=True
                    result_t=line["timesec"]
                    delays.append(result_t-action_t)
                    action_t=result_t=0
                    continue
                if result_str2!='': #we are looking for two strings
                    result_t=getTimeLogWrittenBefore(log,result_str2, line["id"]-20,line["id"])#looking for the second string written
                    action=True
                    if action_t==0:continue #the second string was not found
                    result_t=line["timesec"]
                    delays.append(result_t-action_t)
                    action_t=result_t=0

    return delays

def delayRoleOpening(logs):
    avDelay=0 #average delay of role opening
    for role in ROLE_NAMES:
        delays=getDelay(logs,[ROLE_OPEN_ACTION+role],[ROLE_OPEN_RESULT+role],ROLE_OPEN_ACION_2)
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
def getDelayStringWithCallsign(logs, action_str,result_str,action_sep='',):
    delays=[]
    for line in logs: #looking for the callsign contained in the ligne "action_str"+callsign
        if action_str in line['text']:
            callsign=''
            for letter in line['text'][len(action_str):]:
                if letter!=action_sep:callsign+=letter
                else: break
            delays+=getDelay(logs,[action_str,callsign],[result_str,callsign])

    return delays

def delayCLDForward(logs):
    avDelay=0
    delays=getDelayStringWithCallsign(logs,CLD_FORWARD_ACTION,CLD_FORWARD_RESULT,')')
    writePerfFile(PERF_FILE,"Delays to move a FS from the wait list to the ground zone: "+str(delays))
    for delay in delays:
        avDelay=(avDelay+delay)/2
    writePerfFile(PERF_FILE,"the average delay to move a FS from the wait liste to the ground zone:"+ str(avDelay))
    return

def delayTakeOff(logs):
    avDelay=0
    delays=getDelayStringWithCallsign(logs,TAKE_OFF_ACTION,TAKE_OFF_RESULT,')')
    writePerfFile(PERF_FILE,"Delays to move a FS from the ground zone to the departed zone: "+str(delays))
    for delay in delays:
        avDelay=(avDelay+delay)/2
    writePerfFile(PERF_FILE,"the average delay to move a FS from the ground zone to the departed zone:"+ str(avDelay))
    return

def delayWaitListe(logs):
    avDelay=0
    delays=getDelayStringWithCallsign(logs,WAIT_LISTE_ACTION,WAIT_LISTE_RESULT,'/')
    writePerfFile(PERF_FILE,"Delays to move a FS from the wait liste to the ground zone: "+str(delays))
    for delay in delays:
        avDelay=(avDelay+delay)/2
    writePerfFile(PERF_FILE,"the average delay to move a FS from the wait liste to the ground zone:"+ str(avDelay))
    return

##### Global Variable#######
ROLE_NAMES={'CLD_1','SPVR','GRO_1','GRO_2','ADC_1','ADC_2','ADC_3','DEP_1','DEP_2','FIN_1','FIN_2','FIN_3','APW_1','APW_2'}
ROLE_OPEN_ACTION="UIS:  activation of Role by client "
ROLE_OPEN_RESULT= "set role on front: "
ROLE_OPEN_ACION_2="Button OK_BUTTON pressed."
ROLE_CHANGE_ACTION=" change status ACTIVE_AND_SHOWN"

CLD_FORWARD_ACTION="    LMB pressed on CLD_FORWARD (strip "
CLD_FORWARD_RESULT="CLD_1 - Candidate visible strips in site.eStripboard.ifr.twr.CldGroundZone:"

TAKE_OFF_ACTION="    LMB pressed on TAKE_OFF_BUTTON (strip "
TAKE_OFF_RESULT="DepartedZone:"

WAIT_LISTE_ACTION="    Double click on "
WAIT_LISTE_RESULT="CLD_1 - Candidate visible strips in site.eStripboard.ifr.twr.CldWaitListZone:"

PERF_FILE='performance'
##### Global Variable#######

logs=openlogfile('client')
dictLogs=getLineTime(logs)
#delayRoleOpening(dictLogs)
delayWaitListe(dictLogs)
delayCLDForward(dictLogs)
delayTakeOff(dictLogs)
#delayRoleChange(dictLogs)
