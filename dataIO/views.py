#-*- coding: utf-8 -*-
from django.shortcuts import render
from dataIO.forms import *
from functools import reduce
import django_excel as excel
import pandas as pd
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from index.models import *
from .fillData import  FillData,PreprocessData
import datetime
from django.db.models import Q
from urllib import parse
from .models import *
from django import db
import subprocess,re

MODELS_TO_ANALYSIS = [EmployeeBiography, EmailData,Flow,EmployeeGrade, Education, Survey, Trip, IMSData,
                ApprovalData, Portable_out_Data, PC_out_Data, PC_control_Data, Thanks_Data, VDI_indi_Data,
                VDI_share_Data, ECMData, CafeteriaData, BlogData]



def getDatelist(Model):
    if Model.__name__.endswith('log'):
        dt_= Model.objects.order_by("-eval_date")
        if dt_.count() == 0:
            return ["0개의 업데이트"]
        return [dt_.first().eval_date,dt_.last().eval_date]
    elif Model.__name__.endswith('EmailLog'):
        if EmailLog.objects.count() == 0:
            return [datetime.datetime(1,1,1),"0개의 업데이트"]
        return [EmailDateBeginEnd.objects.last().eval_date,"total " + str(EmailLog.objects.count())+" 개의 로그"]
    return list(Model.objects.order_by("-eval_date").values_list('eval_date', flat=True).distinct())


def lastUpdateDates(ModelList):
    zeroLenprocess = lambda x: ["0개의 업데이트"] if len(x) == 0 else x


    updateMat = [list(
                    map(lambda x: x if type(x) == str else str(x)[:10],
                        zeroLenprocess(
                            getDatelist(Model)
                        )
                    )
                )for Model in ModelList
    ]
    # maximum length of element
    maxL = max(map(lambda x: len(x),updateMat))
    updateMatRslt = list(map(lambda x: x + ["-" for _ in range(maxL - len(x))] ,updateMat))
    return updateMatRslt

def getRecentUpdateDates():


    updateMat = lastUpdateDates(modelList())


    modelName = list(map(lambda x:x.__name__, modelList()))

    return [(name_i,date_i) for name_i,date_i in zip(modelName,updateMat)]





def getSingleModelFields(model,empObj,start_date, eval_date):

    if model == Employee:
        modelObj = empObj
    else:
        modelObj = model.objects.filter(Q(employeeID=empObj)& Q(start_date=start_date) & Q(eval_date=eval_date)).order_by("-eval_date").first()
    fieldNotUsing = ['id', 'employeeID', 'employeeID_confirm', 'eval_date','start_date', 'created_at']
    fieldNames = [mf.name for mf in model._meta.fields if mf.name not in fieldNotUsing]
    field_val_dic = {i:None for i in fieldNames}
    if modelObj == None:
        return field_val_dic
    for name_i in fieldNames:
        field_val_dic[name_i] = eval("modelObj."+name_i)
    if model == EmployeeBiography:
        field_val_dic.update({"rewardyn":modelObj.rewardyn})
    return field_val_dic

def getAllModelFields(models,empObj,start_date, eval_date):
    allModelFieldValue = list(map(lambda x: getSingleModelFields(x,empObj,start_date, eval_date),models))
    baseDic = {}
    for dic_i in allModelFieldValue:
        baseDic.update(dic_i)
    return {empObj.id:baseDic}

def getTable(models,start_date, eval_date,target=False):
    if target:
        employeeObject = Employee.objects.filter(istarget=True)
    else:
        employeeObject = Employee.objects.all()
    allEmployeeModelFieldValue = list(map(lambda x:getAllModelFields(models,x,start_date, eval_date),employeeObject))
    baseDic = {}
    for dic_i in allEmployeeModelFieldValue:
        baseDic.update(dic_i)
    empId = baseDic.keys()
    empId_values = list(baseDic.values())

    header = list(empId_values[0].keys())
    dfmat = [[row[col] for col in header ] for row in empId_values]
    df = pd.DataFrame(dfmat)
    df.columns = header
    df["id"] = list(empId)
    return df


def get_Bu_buUrl():
    bu = [list(i.values())[0] for i in list(EmployeeBiography.objects.values("bu").distinct()) if
          list(i.values())[0] != None]
    buUrl = [parse.quote(i) for i in bu]
    bu_buUrl = [(i, j) for i, j in zip(bu, buUrl)]
    return bu_buUrl

def placeencode(x):
    if x == "판교":
        return "pangyo"
    elif x == "포항":
        return "pohang"
    elif x == "광양":
        return "gwangyang"
    elif x == "센터":
        return "center"
    else:
        return "etc"

def _fillScoreData(df,start_date,eval_date):
    for i in range(len(df)):
        df_instance = df.iloc[i, :]
        employeeID_ = df_instance.id
        try:
            employeeID = Employee.objects.get(id=employeeID_)
        except:
            continue
        employeeID_confirm = df_instance.id
        score1 = df_instance.score1
        score2 = df_instance.score2
        score3 = df_instance.score3
        score4 = df_instance.score4
        empScore = Score(employeeID=employeeID, employeeID_confirm=employeeID_confirm,
                           score1=score1, score2=score2, score3=score3, score4=score4,start_date=start_date,
                           eval_date=eval_date)

        empScore.save()
    return True


def updateEmailDateBeginEnd():
    emailDateBegin = EmailDateBeginEnd.objects.get(pk=0).eval_date
    emailDateEnd = EmailDateBeginEnd.objects.get(pk=1).eval_date
    emailOrderby = EmailLog.objects.order_by("-eval_date")
    if emailOrderby.count() == 0:
        emailDateBegin = datetime.datetime.now()+datetime.timedelta(days=1)
        emailDateEnd = datetime.datetime(1900,1,1)
    else:
        emailDateBegin = min(emailOrderby.last().eval_date, emailDateBegin)
        emailDateEnd = max(emailOrderby.first().eval_date, emailDateEnd)
    EmailDateBeginEnd(pk=0, eval_date=emailDateBegin).save()
    EmailDateBeginEnd(pk=1, eval_date=emailDateEnd).save()

def dateRangeStr2datetime(dateRangeStr):
    start_date, eval_date = [datetime.datetime.strptime(dt, "%Y-%m-%d") for dt in map(lambda x: x.strip(), dateRangeStr.split("~"))]
    return [start_date, eval_date]

def getModelInstanceWithDateRange(Model,dateRangeStr=None,dateRange=None):
    if dateRangeStr:
        start_date, eval_date = dateRangeStr2datetime(dateRangeStr)
        modelInstances = Model.objects.filter(Q(start_date=start_date) & Q(eval_date=eval_date))
    if dateRange:
        start_date, eval_date = dateRange
        print(start_date,eval_date)
        print(Model)
        modelInstances = Model.objects.filter(Q(eval_date__gte=start_date) & Q(eval_date__lte=eval_date))

    return modelInstances

def preprocess2Analysis(start_date,end_date):
    modelsToPreprocess = []
    for model in MODELS_TO_ANALYSIS:
        if model.objects.filter(Q(start_date=start_date) & Q(eval_date=end_date)).count() == 0:
            modelsToPreprocess.append(model)
    for model in modelsToPreprocess:
        PreprocessData(model, start_date, end_date).runPreprocess()


def dataIO(request):
    processedModels = [Flow, EmailData, IMSData, ApprovalData, Portable_out_Data, PC_out_Data, PC_control_Data,
                       Thanks_Data, VDI_indi_Data, VDI_share_Data, ECMData, CafeteriaData, BlogData,MeetingData,EPData,M_EPData,PCMData,TMSData,GatePassData]
    hrModels = [EmployeeBiography, EmployeeGrade, Education, Trip]
    logModels = [Reward_log, EmailLog, IMS_log, Approval_log, Portable_out_log, PC_out_log, PC_control_log,
                 Thanks_log, VDI_indi_log, VDI_share_log, ECM_log, Cafeteria_log, Blog_log,Meeting_log,EP_log,M_EP_log,PCM_log,TMS_log,GatePass_log]
    if request.method == 'GET':
        search_query = request.GET.get('search_box', None)
        if search_query != None:
            return HttpResponseRedirect(reverse('employee', args=[search_query]))

    if request.method == "POST":
        """
        form1 = UploadFileForm(request.POST, request.FILES)
        form1_1 = DateRangePickForm(request.POST)
        form2 = DateRangePickForm(request.POST)
        form3 = DateRangePickForm(request.POST)
        form4 = remove_choice_Form(request.POST)

        processedDataSelects = [ProcessedDataSelect(request.POST,model=processedModel) for processedModel in processedModels]

        logDataSelects = [LogDataSelect(request.POST,model=logmodel) for logmodel in logModels]

        hrDataSelects = [HRDataSelect(request.POST,model=hrmodel) for hrmodel in hrModels]

        scoreDataSelects = [ScoreDataSelect(request.POST,model=Score)]
        """
        reqDict = dict(request.POST)
        reqKeyString = "&".join(list(reqDict.keys()))


        if 'input_' in reqKeyString:
            modelname = re.findall(r"input_([A-Z|a-z|_]*)",reqKeyString)[0]
            files = request.FILES.getlist('file')
            print(modelname+str(files))
            listHasEmailFile = False
            for idx, filehandle in enumerate(files):
                print(str(filehandle))
                if "email" in modelname.lower():
                    listHasEmailFile = True
                fd = FillData(modelname, filePathName=filehandle)
                fd.fillDB()
            if listHasEmailFile:
                updateEmailDateBeginEnd()
            return HttpResponseRedirect(reverse('dataIO'))
        elif 'inputWithDatetime_' in reqKeyString:
            modelname = re.findall(r"inputWithDatetime_([A-Z|a-z|_]*)", reqKeyString)[0]
            files = request.FILES.getlist('file')
            start_date = datetime.datetime(int(reqDict["start_date_year"][0]),int(reqDict["start_date_month"][0]),int(reqDict["start_date_day"][0]))
            end_date = datetime.datetime(int(reqDict["end_date_year"][0]),int(reqDict["end_date_month"][0]),int(reqDict["end_date_day"][0]))
            #print(modelname + str(files))
            for idx, filehandle in enumerate(files):
                print(str(filehandle))
                fd = FillData(modelname, filePathName=filehandle, start_date=start_date, end_date=end_date)
                fd.fillDB()
            return HttpResponseRedirect(reverse('dataIO'))

        elif 'output_' in reqKeyString:
            modelname = re.findall(r"output_([A-Z|a-z|_]*)",reqKeyString)[0]
            updateList = getDatelist2(eval(modelname))
            selectedDate = int(reqDict['prefix'][0])
            dateRangeStr = updateList[selectedDate]
            start_date, eval_date = [datetime.datetime.strptime(dt, "%Y-%m-%d") for dt in
                                     map(lambda x: x.strip(), dateRangeStr.split("~"))]
            df = getTable([eval(modelname)],start_date,eval_date)
            df = df.fillna("NA")
            filename = modelname+"_"+dateRangeStr
            df.reindex_axis(sorted(df.columns), axis=1).to_csv("./static/excels/"+filename,encoding='cp949')
            filetosend = open("./static/excels/"+filename, 'r', encoding='cp949')
            response = HttpResponse(filetosend, content_type="text/csv", charset='cp949')
            response['Content-Disposition'] = "attachment; filename=%s.csv" % (filename)
            return response


        elif 'remove_' in reqKeyString:
            modelname = re.findall(r"remove_([A-Z|a-z|_]*)", reqKeyString)[0]
            updateList = getDatelist2(eval(modelname))
            selectedDate = int(reqDict['prefix'][0])
            if modelname == "EmployeeBiography":
                for hrmodel in hrModels:
                    modelname_i = hrmodel.__name__
                    modelInstances = getModelInstanceWithDateRange(eval(modelname_i), dateRangeStr=updateList[selectedDate])
                    modelInstances.delete()
            else:
                modelInstances = getModelInstanceWithDateRange(eval(modelname),dateRangeStr=updateList[selectedDate])
                modelInstances.delete()

        elif 'removeWithDatetime_' in reqKeyString:
            modelname = re.findall(r"removeWithDatetime_([A-Z|a-z|_]*)", reqKeyString)[0]
            start_date = datetime.datetime(int(reqDict["start_date_year"][0]),int(reqDict["start_date_month"][0]),int(reqDict["start_date_day"][0]))
            end_date = datetime.datetime(int(reqDict["end_date_year"][0]),int(reqDict["end_date_month"][0]),int(reqDict["end_date_day"][0]))
            modelInstances = getModelInstanceWithDateRange(eval(modelname),dateRange=[start_date,end_date+datetime.timedelta(days=1)])
            modelInstances.delete()
            if modelname == "EmailLog":
                updateEmailDateBeginEnd()

        elif 'preprocess_' in reqKeyString:
            modelname = re.findall(r"preprocess_([A-Z|a-z|_]*)", reqKeyString)[0]
            start_date = datetime.datetime(int(reqDict["start_date_year"][0]),int(reqDict["start_date_month"][0]),int(reqDict["start_date_day"][0]))
            end_date = datetime.datetime(int(reqDict["end_date_year"][0]),int(reqDict["end_date_month"][0]),int(reqDict["end_date_day"][0]))
            print("preprocess "+modelname + " from " + str(start_date) + " to " + str(end_date))
            PreprocessData(eval(modelname),start_date,end_date).runPreprocess()

        elif 'analysis_' in reqKeyString:
            modelname = re.findall(r"analysis_([A-Z|a-z|_]*)", reqKeyString)[0]
            start_date = datetime.datetime(int(reqDict["start_date_year"][0]),int(reqDict["start_date_month"][0]),int(reqDict["start_date_day"][0]))
            end_date = datetime.datetime(int(reqDict["end_date_year"][0]),int(reqDict["end_date_month"][0]),int(reqDict["end_date_day"][0]))
            updateList = getDatelist2(eval(modelname))
            print(updateList)
            dfs = []
            """
            scoreDatetime = [dateRangeStr2datetime(dateRangeStr) for dateRangeStr in updateList]
            for start_date_, end_date_ in scoreDatetime:
                if start_date != start_date_ and end_date != end_date_:
                    preprocess2Analysis(start_date_, end_date_)
                    df_i = getTable(MODELS_TO_ANALYSIS, start_date, end_date, target=True)
                    dfs.append(df_i)
            """
            print("analysis_ "+modelname + " from " + str(start_date) + " to " + str(end_date))
            preprocess2Analysis(start_date,end_date)
            df_i = getTable(MODELS_TO_ANALYSIS, start_date,end_date, target=True)
            dfs.append(df_i)
            df = pd.concat(dfs, axis=0)
            df = df.fillna("NA")
            df.place = df.place.map(lambda x: placeencode(x))
            df.reindex_axis(sorted(df.columns), axis=1).to_csv("./static/excels/input_new.csv", encoding='cp949')
            subp = subprocess.call(["C:\\Program Files\\R\\R-3.4.1\\bin\\Rscript", "--vanilla",
                                    "C:\\Program Files\\poscoictdashboard\\xxxICTv2\\poscoictsystem\\static\\Analaysis_R_code.R"],
                                   shell=True)

            scoredf = pd.read_csv("./static/excels/output.csv")
            _fillScoreData(scoredf, start_date,end_date)
        print(request.POST)
        return HttpResponseRedirect(reverse('dataIO'))



    else:
        db.connections.close_all()
        form1 = UploadFileForm()
        form1_1 = DateRangePickForm()
        form2 = DateRangePickForm()
        form3 = DateRangePickForm()
        form4 = remove_choice_Form()



        processedDataSelects = [StructuredDataSelect(model=processedModel) for processedModel in processedModels]

        logDataSelects = [LogDataSelect(model=logmodel) for logmodel in logModels]

        hrDataSelects = [StructuredDataSelect(model = hrmodel)  for  hrmodel in hrModels ]


        scoreDataSelects = [StructuredDataSelect(model = Score)]
        surveyDataSelects = [StructuredDataSelect(model=Survey)]

    context = {  'bu': get_Bu_buUrl(),
                 'form1': form1,
                 'form2': form2,
                 'form1_1': form1_1,
                 'form3': form3,
                 'form4':form4,
                 "recentUpdateDate": getRecentUpdateDates(),
                 'processedDataSelects':processedDataSelects,
                 'hrDataSelects':hrDataSelects,
                 'scoreDataSelects':scoreDataSelects,
                 'logDataSelects':logDataSelects,
                 'surveyDataSelects':surveyDataSelects,
                 'title': 'Excel file upload and download example',
                 'header': ('Please choose any excel file ' +
                            'from your cloned repository:')
                 }
    return render(request,'dataIO.html',context)
























def deleteErrorInput(fileName, t1, t2):
    fileName = fileName.lower()
    if fileName.startswith("biography"):
        EmployeeBiography.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("grade"):
        EmployeeGrade.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("trip"):
        Trip.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("educa"):
        Education.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("approval"):
        Approval_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        ApprovalData.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("blog"):
        Blog_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        BlogData.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("ecm"):
        ECM_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        ECMData.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("ims"):
        IMS_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        IMSData.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("pccontrol"):
        PC_control_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        PC_control_Data.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("pcout"):
        PC_out_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        PC_out_Data.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("portableout"):
        Portable_out_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        Portable_out_Data.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("reward"):
        Reward_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("survey"):
        Survey.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("thanks"):
        Thanks_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        Thanks_Data.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("vdi_indi"):
        VDI_indi_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        VDI_indi_Data.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("vdi_share"):
        VDI_share_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        VDI_share_Data.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("cafeteria"):
        Cafeteria_log.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        CafeteriaData.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("email"):
        EmailLog.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
        EmailData.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
    elif fileName.startswith("score"):
        Score.objects.filter(Q(created_at__gte=t1) & Q(created_at__lte=t2)).delete()
