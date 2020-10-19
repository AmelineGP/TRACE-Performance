
import time
import os


##### Global Variable#######
#Role opening
ROLE_NAMES={'CLD_1','SPVR','GRO_1','GRO_2','ADC_1','ADC_2','ADC_3','DEP_1','DEP_2','FIN_1','FIN_2','FIN_3','APW_1','APW_2'}
ROLE_OPEN_ACTION="UIS:  activation of Role by client "
ROLE_OPEN_RESULT= "set role on front: "
ROLE_OPEN_ACION_2="Button OK_BUTTON pressed."
ROLE_OPEN_EXP_DELAY=0.2

CLD_FORWARD_CALLSIGN="    LMB pressed on CLD_FORWARD (strip "
CLD_FORWARD_ACTION="    LMB pressed on CLD_FORWARD (strip "
CLD_FORWARD_RESULT="CldGroundZone:"
CLD_FORWARD_EXP_DELAY=0.8

TAKE_OFF_ACTION="    LMB pressed on TAKE_OFF_BUTTON (strip "
TAKE_OFF_RESULT="DepartedZone:"
TAKE_OFF_EXP_DELAY=0.5

WAIT_LISTE_ACTION="    Double click on "
WAIT_LISTE_RESULT="CldWaitListZone:"
WAIT_LISTE_EXP_DELAY=0.3


LANDING_ACTION="    LMB pressed on LANDING_BUTTON (strip "
LANDING_RESULT="LandedZone:"
LANDING_EXP_DELAY=0.5

PERF_FILE='performance'
LOG_PATH='./'
##### Global Variable#######

def openlogfile(name):
    file_path=input("Enter the path to the logs: ")
    if file_path=='':file_path=LOG_PATH
    file_name=name
    complete_list = os.listdir(file_path)
    content=[]
    lname=len(file_name)
    for file in complete_list:
        if file[0:lname]==file_name:
            writePerfFile(str(file)+" log file will be used for the test")
            f=open(file,'r')
            if f.mode=="r":
                content.append(f.readlines())

    return content

def writePerfFile(line,title=PERF_FILE):
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

def testResult(result,expect):
    if result==0:
        writePerfFile("*********** NO DATA, TEST INVALID *************")
        return
    if result<=expect:
        writePerfFile("*********** TEST PASSED **********" )
        writePerfFile(' Average delay inferior to: '+str(expect)+"s")
        return
    else:
        writePerfFile("*********** TEST FAILED **********")
        writePerfFile(' Average delay supperior to: '+str(expect)+"s")
        return
    return

def getAverageDelay(delays):
    if delays==[]:return 0
    return sum(delays)/len(delays)

def delayRoleOpening(logs):
    avDelay=0 #average delay of role opening
    for role in ROLE_NAMES:
        delays=getDelay(logs,[ROLE_OPEN_ACTION+role],[ROLE_OPEN_RESULT+role],ROLE_OPEN_ACION_2)
        if len(delays)>0: #if there is at least one time calculated
            #writePerfFile("Delays to open the role "+role+": "+str(delays))
            avDelay=getAverageDelay(delays)
    writePerfFile("The average delay for role opening is:"+ str(avDelay))
    testResult(avDelay,ROLE_OPEN_EXP_DELAY)

    return


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

def delayMoveFS(logs,dictMoveFS):
    for move in dictMoveFS:
        avDelay=0
        delays=getDelayStringWithCallsign(logs,move["action"],move["result"],move["separator"])
        #writePerfFile("Delays to move a FS from the "+move['Zone1']+" to the "+move["Zone2"]+': '+str(delays))
        avDelay=getAverageDelay(delays)
        writePerfFile("The average delay to move a FS from the "+move['Zone1']+" to the "+move["Zone2"]+' is: '+ str(avDelay))
        testResult(avDelay,move["ExpDelay"])
    return

def creactDictMoveFS():
    dict=[]
    dict.append({'name':'CLD_FORWARD','action':CLD_FORWARD_ACTION,'result':CLD_FORWARD_RESULT,'separator':')','ExpDelay':CLD_FORWARD_EXP_DELAY,'Zone1':'wait liste','Zone2':'ground Zone'})
    dict.append({'name':'TAKE_OFF','action':TAKE_OFF_ACTION,'result':TAKE_OFF_RESULT,'separator':')','ExpDelay':TAKE_OFF_EXP_DELAY,'Zone1':'Ground zone','Zone2':'Departed zone'})
    dict.append({'name':'LANDING','action':LANDING_ACTION,'result':LANDING_RESULT,'separator':')','ExpDelay':LANDING_EXP_DELAY,'Zone1':'landing zone','Zone2':'Landed zone'})
    dict.append({'name':'WAIT_LISTE','action':WAIT_LISTE_ACTION,'result':WAIT_LISTE_RESULT,'separator':'/','ExpDelay':WAIT_LISTE_EXP_DELAY,'Zone1':'CLD First page','Zone2':'Wait liste'})

    return dict



######## MAIN #########


logs=openlogfile('client')
dictLogs=getLineTime(logs)

delayRoleOpening(dictLogs)

dictMoveFS=creactDictMoveFS()
delayMoveFS(dictLogs,dictMoveFS)
