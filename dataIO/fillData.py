#-*- coding: utf-8 -*-
import pandas as pd
from django.db.models import Q,F, Sum, Count, Case, When, Avg, Func,ExpressionWrapper,DurationField
from index.models import *
import datetime
import re,os,time
import numpy as np
from django.db.models.functions import TruncMonth, TruncDay
from sklearn.cluster import KMeans
from inspect import ismethod
from django import db
import networkx as nx
import  copy
TEMPEVAL_DATE = datetime.datetime.today()

class EmailGraphProcess:
    networksJson = {}
    centralityJson = {}

    def __init__(self,start_date,eval_date):
        self.start_date = start_date
        self.eval_date = eval_date
        self.setNetworks()
        self.setCentralities()

    def getGraph(self,querySet):
        emailcount = querySet.values("sendID","receiveID").annotate(weight = Count("sendID")).values("sendID","receiveID","weight")
        g = nx.DiGraph()
        for em in emailcount:
            node1 = em["sendID"]
            node2 = em["receiveID"]
            weight = em["weight"]
            g.add_edge(node1,node2,weight=weight)
        return g
    def setNetworks(self):
        self.emplevels = sorted(list(Employee.objects.values_list("level", flat=True).distinct()))
        emailCnctObj = EmailLog.objects.filter(Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))
        g_all = self.getGraph(emailCnctObj)
        self.networksJson.update({"all":g_all})
        for empLevel in self.emplevels:
            emailCnctObj_sangsa = EmailLog.objects.filter(((Q(receiveID__level=empLevel) & Q(sendID__level__lt=empLevel)) | (Q(sendID__level=empLevel) & Q(receiveID__level__lt=empLevel))) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))
            emailCnctObj_dongryo = EmailLog.objects.filter(Q(receiveID__level=empLevel) & Q(sendID__level=empLevel) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))
            emailCnctObj_buha = EmailLog.objects.filter(((Q(receiveID__level=empLevel) & Q(sendID__level__gt=empLevel)) | (Q(sendID__level=empLevel) & Q(receiveID__level__gt=empLevel))) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))

            g_s = self.getGraph(emailCnctObj_sangsa)
            g_d = self.getGraph(emailCnctObj_dongryo)
            g_b = self.getGraph(emailCnctObj_buha)
            self.networksJson.update({str(empLevel)+"_sangsa": g_s})
            self.networksJson.update({str(empLevel) + "_dongryo": g_d})
            self.networksJson.update({str(empLevel) + "_buha": g_b})

    def getCentrality(self,cenType,g):
        """
        nodeSize = 500
        if g.number_of_nodes() < nodeSize:
        """
        nodeSize = g.number_of_nodes()
        if nodeSize == 0:
            return {"-1":0}
        if cenType == "betweenness":
            return nx.betweenness_centrality(g,nodeSize)
        if cenType == "eigenvector":
            return nx.eigenvector_centrality(g,max_iter=1000)


    def setCentralities(self):
        groups = ["sangsa","dongryo","buha"]
        centralityType = ["betweenness","eigenvector"]
        for group in groups:
            for empLevel in self.emplevels:
                for centrality_i in centralityType:
                    cen_i = self.getCentrality(centrality_i,self.networksJson[str(empLevel)+"_"+group])
                    self.centralityJson.update({str(empLevel)+"_"+group+"_"+centrality_i:cen_i})

        for centrality_i in centralityType:
            cen_i = self.getCentrality(centrality_i, self.networksJson["all"])
            self.centralityJson.update({"all_"+centrality_i:cen_i})



class PreprocessData:


    def __init__(self,inputModel, start_date, eval_date):

        self.start_date = start_date
        self.eval_date = eval_date
        self.log_data = {Approval_log:ApprovalData,
                        Blog_log:BlogData,
                        Cafeteria_log:CafeteriaData,
                        ECM_log:ECMData,
                        EmailLog:EmailData,
                        IMS_log:IMSData,
                        PC_control_log:PC_control_Data,
                        PC_out_log:PC_out_Data,
                        Portable_out_log:Portable_out_Data,
                        Thanks_log:Thanks_Data,
                        VDI_indi_log:VDI_indi_Data,
                        VDI_share_log:VDI_share_Data,
                        Meeting_log:MeetingData,
                        EP_log:EPData,
                        M_EP_log:M_EPData,
                        PCM_log:PCMData,
                        TMS_log:TMSData,
                        GatePass_log : GatePassData}


        if inputModel in self.log_data.values():
            self.Model = inputModel
        else:
            self.Model = self.log_data[inputModel]
        if self.Model == EmailData:
            self.egp = EmailGraphProcess(start_date=start_date,eval_date=eval_date)

    def getSnaData(self, empId, myDict=None, graph=None):
        closeness_indegree_outDegree = [None, None, None]
        if graph != None:
            try:
                closeness_indegree_outDegree[0] = nx.closeness_centrality(graph, empId)
            except:
                pass
            try:
                closeness_indegree_outDegree[1] = graph.in_degree(empId)
            except:
                pass

            try:
                closeness_indegree_outDegree[2] = graph.out_degree(empId)
            except:
                pass

            return closeness_indegree_outDegree

        try:
            rslt = myDict[empId]
            return rslt
        except:
            return None

    def runPreprocess(self):
        instance_i_list = []
        empList = list(Employee.objects.all().order_by("level").values_list('id', flat=True))
        for id_i in empList:
            print(id_i, end="\r")
            empObj = Employee.objects.get(pk=id_i)

            isExists = self.Model.objects.filter(Q(employeeID=empObj) & Q(eval_date=self.eval_date) & Q(start_date=self.start_date))
            if isExists.count() != 0:
                isExists.delete()
            if self.Model != EmailData:
                instance_i = self.Model(employeeID=empObj, employeeID_confirm=id_i, start_date=self.start_date, eval_date=self.eval_date)
            else:
                cls_ind_outd_all = self.getSnaData(id_i, graph=self.egp.networksJson["all"])
                cls_ind_outd_sangsa = self.getSnaData(id_i, graph=self.egp.networksJson[str(empObj.level) + "_sangsa"])
                cls_ind_outd_dongryo = self.getSnaData(id_i, graph=self.egp.networksJson[str(empObj.level) + "_dongryo"])
                cls_ind_outd_buha = self.getSnaData(id_i, graph=self.egp.networksJson[str(empObj.level) + "_buha"])
                instance_i = self.Model(employeeID=empObj, employeeID_confirm=id_i, start_date=self.start_date,
                                        eval_date=self.eval_date
                                        , sna_closeness=cls_ind_outd_all[0]
                                        , sna_betweenness=self.getSnaData(id_i, myDict=self.egp.centralityJson["all_betweenness"])
                                        , sna_eigenvector=self.getSnaData(id_i, myDict=self.egp.centralityJson["all_eigenvector"])
                                        , sna_indegree=cls_ind_outd_all[1]
                                        , sna_outdegree=cls_ind_outd_all[2]

                                        , buha_closeness=cls_ind_outd_buha[0]
                                        , buha_betweenness=self.getSnaData(id_i, myDict=self.egp.centralityJson[str(empObj.level) + "_buha_betweenness"])
                                        , buha_eigenvector=self.getSnaData(id_i, myDict=self.egp.centralityJson[str(empObj.level) + "_buha_eigenvector"])
                                        , buha_indegree=cls_ind_outd_buha[1]
                                        , buha_outdegree=cls_ind_outd_buha[2]

                                        , dongryo_closeness=cls_ind_outd_dongryo[0]
                                        , dongryo_betweenness=self.getSnaData(id_i, myDict=self.egp.centralityJson[ str(empObj.level) + "_dongryo_betweenness"])
                                        , dongryo_eigenvector=self.getSnaData(id_i, myDict=self.egp.centralityJson[str(empObj.level) + "_dongryo_eigenvector"])
                                        , dongryo_indegree=cls_ind_outd_dongryo[1]
                                        , dongryo_outdegree=cls_ind_outd_dongryo[2]

                                        , sangsa_closeness=cls_ind_outd_sangsa[0]
                                        , sangsa_eigenvector=self.getSnaData(id_i, myDict=self.egp.centralityJson[ str(empObj.level) + "_sangsa_betweenness"])
                                        , sangsa_betweenness=self.getSnaData(id_i, myDict=self.egp.centralityJson[str(empObj.level) + "_sangsa_eigenvector"])
                                        , sangsa_indegree=cls_ind_outd_sangsa[1]
                                        , sangsa_outdegree=cls_ind_outd_sangsa[2])
            attrs = []
            for name in dir(instance_i):
                try:
                    attrs.append(getattr(instance_i, name))
                except:
                    continue
            __methods = list(filter(lambda x: ismethod(x), attrs))
            methods = list(filter(lambda x: x.__name__.startswith("posco_set"), __methods))
            for method in methods:
                method()
            instance_i_list.append(instance_i)
        self.Model.objects.bulk_create(instance_i_list)
        return True


class FillData:
    """
     LOG Data Input
    """
    def __init__(self,modelName,filePathName=None,start_date=None,end_date=None):


        db.connections.close_all()
        fileStr = str(filePathName).split(".")
        self.modelName = modelName
        self.fileType = fileStr[1]
        self.isDF = False
        self.eval_date = end_date
        self.start_date = start_date
        self.filePathName = filePathName
        if filePathName and self.__dataframeSetter(filePathName,self.modelName.lower().startswith("email")):
            self.isDF = True
        else:
            print("incorrect Input")

    def fillDB(self):
        if self.filePathName and not self.isDF:
            print("DataFrame is not loaded")
            return False

        modelname_method = {
         "Approval_log": self._fillApprovalData

        , "Blog_log":  self._fillBlogData

        , "Cafeteria_log": self._fillCafeteriaData

        , "ECM_log": self._fillEcmData
        , "Education": self._fillEducationData
        , "EmailLog": self._fillEmailData

        , "EmployeeBiography": self._fillHRdata
        , "EmployeeGrade": self._fillGradeData

        , "IMS_log": self._fillImsData

        , "PC_control_log": self._fillPcControlData

        , "PC_out_log": self._fillPcOutData

        , "Portable_out_log": self._fillPortableOutData
        , "Reward_log": self._fillRewardData
        , "Score": self._fillScoreData
        , "Survey": self._fillSurveyData

        , "Thanks_log": self._fillThanksData
        , "Trip": self._fillTripData

        , "VDI_indi_log": self._fillVdiIndiData

        , "VDI_share_log": self._fillVdiShareData
        , "Meeting_log":self._fillMeetingData
        ,'EP_log':self._fillEPData
        ,'M_EP_log':self._fillMEPData
        ,'PCM_log':self._fillPCMData
        , 'TMS_log':self._fillTMSData
        , 'GatePass_log':self._fillGatePassData}

        methodToProcessData = modelname_method[self.modelName]
        methodToProcessData()

    def csvfileToDataFrame(self,filePathName):
        encodings = ["cp949","utf-8","euc-kr"]
        filePathName_ = copy.copy(filePathName)
        file_read = filePathName_.read()
        for encoding_i in encodings:
            try:
                file_data = file_read.decode(encoding_i)
                lines = file_data.split("\n")
                lines = list(map(lambda row: row.strip().split(","), lines))
                header = lines[0]
                rows = lines[1:]
                df = pd.DataFrame(data=rows, columns=header)
                print(header)
                return df
            except:
                pass
        return  pd.DataFrame([])

    def __dataframeSetter(self,filePathName,isemail):
        if isemail:
            try:
                self.df = pd.read_csv(filePathName, index_col=False,encoding="utf-8")
                return True
            except:
                self.df = pd.read_csv(filePathName, index_col=False,encoding='cp949')
                return True
        try:
            if self.fileType.startswith("xls"):
                self.df = pd.read_excel(filePathName,encoding="utf-8")
                self.df = self.df.where((pd.notnull(self.df)), None)
            elif self.fileType == "csv":
                self.df = self.csvfileToDataFrame(filePathName)
                #self.df = pd.read_csv(filePathName,encoding="utf-8")
                #self.df = self.df.where((pd.notnull(self.df)), None)
            return True
        except:
            pass

        try:
            if self.fileType.startswith("xls"):
                self.df = pd.read_excel(filePathName, encoding="cp949")
                self.df = self.df.where((pd.notnull(self.df)), None)
            elif self.fileType == "csv":
                self.df = pd.read_csv(filePathName, encoding="cp949")
                self.df = self.df.where((pd.notnull(self.df)), None)
            return True
        except:
            pass

        try:
            if self.fileType.startswith("xls"):
                self.df = pd.read_excel(filePathName, encoding="euc-kr")
                self.df = self.df.where((pd.notnull(self.df)), None)
            elif self.fileType == "csv":
                self.df = pd.read_csv(filePathName, encoding="euc-kr")
                self.df = self.df.where((pd.notnull(self.df)), None)
            return True
        except:
            return False

    def _fillHRdata(self):
        self._fillBiographyData()
        self._fillEducationData()
        self._fillGradeData()
        self._fillTripData()

    def __strEval_date_converter(self,eval_date):
        global TEMPEVAL_DATE
        try:
            eval_date = re.sub("/","-",eval_date)
            try:
                eval_date_ = re.findall("[0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}", eval_date)[0]
            except:
                eval_date_ = re.findall("[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}[.]*", eval_date)[0]
        except:
            return TEMPEVAL_DATE


        if len(eval_date_) >= 11:
            TEMPEVAL_DATE = datetime.datetime.strptime(eval_date_.strip(), "%Y-%m-%d %H:%M:%S")
            return datetime.datetime.strptime(eval_date_.strip(), "%Y-%m-%d %H:%M:%S")
        else:
            TEMPEVAL_DATE = datetime.datetime.strptime(eval_date_.strip(), "%Y-%m-%d")
            return datetime.datetime.strptime(eval_date_.strip(), "%Y-%m-%d")


    def _fillBiographyData(self):
        noneisZero = lambda x:0 if x == None else x
        def placeExtract(place):
            place = str(place)
            if "센" in place:
                return "센터"
            if "판교" in place:
                return "판교"
            if "분당" in place:
                return "판교"
            if "포항" in place:
                return "포항"
            if "광양" in place:
                return "광양"
            if "서울" in place:
                return "서울"
            return "etc"

        EmployeeBiography_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            id_ = int(df_instance.id)
            bu = df_instance.bu
            place = placeExtract(df_instance.place)
            name = df_instance['name']
            age = df_instance.age
            coreyn = bool(df_instance.coreyn)
            sex = df_instance.sex.startswith("남")
            work_duration = df_instance.work_duration
            try:
                level = int(re.findall('[0-9]{1}',df_instance.level)[0])
            except:
                level = 0
            email = df_instance.email
            istarget = bool(df_instance.istarget)
            pmlevel = noneisZero(df_instance.pmlevel)
            employee_i = Employee.objects.filter(pk=id_)
            if employee_i.count() == 0:
                emp = Employee(id= id_,bu=bu, place=place,empname=name,coreyn=coreyn,age=age,sex = sex,work_duration = work_duration,
                               pmlevel=pmlevel,level = level,email=email,istarget=istarget)
                emp.save()
            else:
                emp = Employee.objects.get(pk=id_)
                emp.level = level
                emp.age = age
                emp.bu = bu
                emp.coreyn = coreyn
                emp.work_duration = work_duration
                emp.pmlevel = pmlevel
                emp.istarget = istarget
                emp.save()
            empBio = EmployeeBiography(employeeID = Employee.objects.get(pk=id_),employeeID_confirm = id_ ,bu=bu, place=place,empname=name,coreyn=coreyn,age=age,sex = sex,work_duration = work_duration,
                                      start_date= self.start_date ,eval_date = self.eval_date,pmlevel=pmlevel,level = level,email=email,istarget=istarget)
            EmployeeBiography_list.append(empBio)
        EmployeeBiography.objects.bulk_create(EmployeeBiography_list)

        return True



    def _fillGradeData(self):
        employeeGrade_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            employeeID_ = df_instance.id
            gradeHash1 = {"s":6,"a":5,"b+":4,"b-":3,"c":2,"d":1,"S":6,"A":5,"B+":4,"B-":3,"C":2,"D":1,None:None}
            try:
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue
            employeeID_confirm = df_instance.id
            grade_sv_y_1 = df_instance.grade_sv_y_1
            grade_sv_y_2 = df_instance.grade_sv_y_2
            grade_co_y = df_instance.grade_co_y
            grade_1 = gradeHash1[df_instance.grade_1]
            grade_2 = gradeHash1[df_instance.grade_2]
            grade_3 = gradeHash1[df_instance.grade_3]
            grade_4 = gradeHash1[df_instance.grade_4]

            empGrade = EmployeeGrade(employeeID=employeeID, employeeID_confirm=employeeID_confirm,
                                     grade_sv_y_1=grade_sv_y_1, grade_sv_y_2=grade_sv_y_2, grade_co_y=grade_co_y,
                                     grade_1=grade_1,grade_2=grade_2,grade_3=grade_3,grade_4=grade_4,eval_date=self.eval_date, start_date = self.start_date)
            empGrade.posco_set_grade_r2_avg()
            empGrade.posco_set_grade_sv_r2_avg()
            employeeGrade_list.append(empGrade)
        EmployeeGrade.objects.bulk_create(employeeGrade_list)
        return True


    def _fillEducationData(self):
        education_list = []
        noneIsZero = lambda x: 0 if x == None else x
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            employeeID_ = df_instance.id
            try:
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue
            employeeID_confirm = df_instance.id
            edu_credit_in = noneIsZero(df_instance.edu_credit_in)
            edu_credit_out = noneIsZero(df_instance.edu_credit_out)
            edu_nbr = noneIsZero(df_instance.edu_nbr)
            toeic = df_instance.toeic != None
            opic = df_instance.opic != None
            tsc = df_instance.tsc != None
            sjpt = df_instance.sjpt != None
            empEdu = Education(employeeID=employeeID, employeeID_confirm=employeeID_confirm,
                               edu_credit_out=edu_credit_out, edu_credit_in=edu_credit_in,edu_nbr=edu_nbr,
                               toeic=toeic, opic=opic,tsc=tsc,sjpt=sjpt,eval_date=self.eval_date, start_date = self.start_date)
            empEdu.posco_set_edu_credit()
            empEdu.posco_set_lang_nbr()
            education_list.append(empEdu)
        Education.objects.bulk_create(education_list)
        return True

    def _fillSurveyData(self):
        survey_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            employeeID_ = df_instance.id
            try:
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue
            employeeID_confirm = df_instance.id
            cct1 = df_instance.cct1
            cct2 = df_instance.cct2
            cct3 = df_instance.cct3
            cct4 = df_instance.cct4
            cct5 = df_instance.cct5
            empSurvey = Survey(employeeID=employeeID, employeeID_confirm=employeeID_confirm,
                               cct1=cct1, cct2=cct2, cct3=cct3, cct4=cct4,cct5=cct5,
                               eval_date=self.eval_date,start_date = self.start_date)
            survey_list.append(empSurvey)
        Survey.objects.bulk_create(survey_list)
        self._fillFlow()
        return True


    def _fillTripData(self):
        noneIsZero = lambda x: 0 if x == None else x
        Trip_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            employeeID_ = df_instance.id
            try:
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue
            employeeID_confirm = df_instance.id

            trip_domestic = noneIsZero(df_instance.trip_domestic)
            trip_town = noneIsZero(df_instance.trip_town)
            trip_abroad = noneIsZero(df_instance.trip_abroad)
            if df_instance.annual_vacation_gen_dt == None:
                avgdt_ = "None"
            else:
                avgdt_ = str(int(df_instance.annual_vacation_gen_dt))
            if avgdt_ != "None":
                annual_vacation_gen_dt = datetime.date(int(avgdt_[:4]),int(avgdt_[4:]),1)
                annual_vacation_gen_amt = noneIsZero(df_instance.annual_vacation_gen_amt)
                annual_vacation_gen_usage = noneIsZero(df_instance.annual_vacation_gen_usage)
            else:
                annual_vacation_gen_dt = datetime.datetime.now()
                annual_vacation_gen_amt = 0
                annual_vacation_gen_usage = 0

            empTrip = Trip(employeeID=employeeID, employeeID_confirm=employeeID_confirm,
                                           trip_domestic=trip_domestic, trip_town=trip_town,trip_abroad=trip_abroad,
                                           annual_vacation_gen_dt=annual_vacation_gen_dt,
                                           annual_vacation_gen_amt=annual_vacation_gen_amt,
                                           annual_vacation_gen_usage=annual_vacation_gen_usage,start_date = self.start_date,
                                           eval_date=self.eval_date)
            empTrip.posco_set_btrip_nbr()
            empTrip.posco_set_off_use_pct_permon()
            Trip_list.append(empTrip)
        Trip.objects.bulk_create(Trip_list)
        return True

    def _fillMeetingData(self):
        meeting_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            employeeID_ = re.findall('PD([0-9]+)',df_instance.id)
            if len(employeeID_) == 0 : continue;
            try:
                employeeID = Employee.objects.get(id=int(employeeID_[0]))
            except:
                continue
            if type(df_instance.eval_date1) == str:
                eval_date = self.__strEval_date_converter(df_instance.eval_date1)
                eval_date2 = self.__strEval_date_converter(df_instance.eval_date2)
            else:
                eval_date = df_instance.eval_date1
                eval_date2 = df_instance.eval_date2

            meeting_i = Meeting_log(employeeID = employeeID,eval_date=eval_date,eval_date2=eval_date2)
            meeting_list.append(meeting_i)
            print(str(employeeID_[0])+str(eval_date)+str(eval_date2),end="\r")
        Meeting_log.objects.bulk_create(meeting_list)
        return True

    def _fillEPData(self):
        ep_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            try:
                employeeID_ = int(df_instance.id)
                employeeID = Employee.objects.get(id=int(employeeID_))
            except:
                continue
            accesstype = df_instance.accesstype
            if accesstype.lower() == "logoff":
                continue
            if type(df_instance.eval_date) == str:
                eval_date = self.__strEval_date_converter(df_instance.eval_date)
            else:
                eval_date = df_instance.eval_date

            ep_i = EP_log(employeeID = employeeID,eval_date=eval_date)
            ep_list.append(ep_i)
            print(str(employeeID_)+str(eval_date),end="\r")
        EP_log.objects.bulk_create(ep_list)
        return True

    def _fillGatePassData(self):
        gatepass_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            try:
                employeeID_ = int(df_instance.id)
                employeeID = Employee.objects.get(id=int(employeeID_))
            except:
                continue
            yyyymmdd = "-".join(re.findall('[0-9]+', df_instance.eval_date1))
            hhmmss = ":".join(re.findall("[0-9]+", df_instance.eval_date2))
            eval_date_ = yyyymmdd.strip()+" "+hhmmss.strip()
            eval_date = self.__strEval_date_converter(eval_date_)
            isIn = "입실" in df_instance.eventtype
            gpl = GatePass_log(employeeID = employeeID,eval_date = eval_date,isIn = isIn)
            gatepass_list.append(gpl)
        GatePass_log.objects.bulk_create(gatepass_list)


    def _fillTMSData(self):
        tms_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            try:
                employeeID_ = int(df_instance.id)
                employeeID = Employee.objects.get(id=int(employeeID_))
            except:
                employeeID = None

            try:
                employeeID2_ = int(df_instance.id2)
                employeeID2 = Employee.objects.get(id=int(employeeID2_))
            except:
                employeeID2 = None

            if employeeID2 == None and employeeID == None:
                continue


            if type(df_instance.eval_date) == str:
                eval_date = self.__strEval_date_converter(df_instance.eval_date)
            else:
                eval_date = df_instance.eval_date

            tms_i = TMS_log(employeeID = employeeID,employeeID2=employeeID2,eval_date=eval_date)
            tms_list.append(tms_i)
            print(str(employeeID_)+str(eval_date),end="\r")
        TMS_log.objects.bulk_create(tms_list)

    def _fillPCMData(self):
        pcm_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            try:
                employeeID_ = int(df_instance.id)
                employeeID = Employee.objects.get(id=int(employeeID_))
            except:
                continue
            if type(df_instance.eval_date) == str:
                eval_date = self.__strEval_date_converter(df_instance.eval_date)
            else:
                eval_date = df_instance.eval_date
            pcm_tot_enroll = df_instance.pcm_tot_enroll
            pcm_tot_remove = df_instance.pcm_tot_remove
            pcm_tot_check = df_instance.pcm_tot_check
            pcm_tot_checked = df_instance.pcm_tot_checked
            pcm_i = PCM_log(employeeID = employeeID,eval_date=eval_date,pcm_tot_enroll =pcm_tot_enroll, pcm_tot_remove= pcm_tot_remove,pcm_tot_check= pcm_tot_check,pcm_tot_checked= pcm_tot_checked)
            pcm_list.append(pcm_i)
            print(str(employeeID_)+str(eval_date),end="\r")
        PCM_log.objects.bulk_create(pcm_list)
        return True


    def _fillMEPData(self):
        mep_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            try:
                employeeID_ = int(df_instance.id)
                employeeID = Employee.objects.get(id=int(employeeID_))
            except:
                continue
            if type(df_instance.eval_date) == str:
                eval_date = self.__strEval_date_converter(df_instance.eval_date)
            else:
                eval_date = df_instance.eval_date

            mep_i = M_EP_log(employeeID = employeeID,eval_date=eval_date)
            mep_list.append(mep_i)
            print(str(employeeID_)+str(eval_date),end="\r")
        M_EP_log.objects.bulk_create(mep_list)
        return True


    def _fillEmailData(self):
        def emailextractor(x):
            try:
                x1 = re.sub("[가-힣|\>|\<|' '*|;]", " ", str(x))
                return re.findall("[^' ']*@[^' ']*", x1)
            except:
                return [""]
        emailHash = {i:j for i,j in list(Employee.objects.values_list("email","id").distinct())}
        success = False
        eval_date = datetime
        self.df.columns = ["col" + str(i) for i in range(len(self.df.columns))]
        self.df = self.df[self.df.col0 == "보낸메일함"]
        self.df.index = range(len(self.df))
        senders = self.df.col1
        seval_date = self.df.col2
        receivers = self.df[["col4", "col5", "col6"]]
        senders = senders.map(lambda x: emailextractor(x))
        receivers = receivers.applymap(lambda x: emailextractor(x))
        receivers = receivers.col4 + receivers.col5 + receivers.col6
        try:
            earlyDate = EmailDateBeginEnd.objects.get(pk=0).eval_date
            recentDate = EmailDateBeginEnd.objects.get(pk=1).eval_date
        except:
            earlyDate = EmailDateBeginEnd(id = 0, eval_date = datetime.datetime(9999,1,1))
            recentDate = EmailDateBeginEnd(id = 1, eval_date = datetime.datetime(1,1,1))
            earlyDate.save()
            recentDate.save()
            earlyDate = EmailDateBeginEnd.objects.get(pk=0).eval_date
            recentDate = EmailDateBeginEnd.objects.get(pk=1).eval_date

        if type(seval_date[0]) == str:
            seval_date = seval_date.map(lambda x: self.__strEval_date_converter(x))
        empEmailLog_list = []
        for i in range(len(senders)):
            if len(receivers[i]) == 0 or len(senders[i]) == 0:
                continue
            try:
                sendID_ = emailHash[senders[i][0].strip()]
            except:
                continue
            for receiver in receivers[i]:
                try:
                    receiveID_ = emailHash[receiver]
                except:
                    continue
                try:
                    sendID = Employee.objects.get(id=sendID_)
                    receiveID = Employee.objects.get(id=receiveID_)
                except:
                    continue
                eval_date = seval_date[i]
                #print(sendID,receiveID,eval_date)
                empEmailLog = EmailLog(sendID=sendID, receiveID=receiveID, eval_date=eval_date)
                empEmailLog_list.append(empEmailLog)
                earlyDate = min(earlyDate,eval_date)
                recentDate = max(eval_date,recentDate)
                print(str(sendID) + " send to "+str(receiveID), end='\r')
                success = True
        if not success:
            return 0
        EmailLog.objects.bulk_create(empEmailLog_list)
        emailDateBegin = EmailDateBeginEnd.objects.get(pk=0)
        emailDateEnd = EmailDateBeginEnd.objects.get(pk=1)
        emailDateBegin.eval_date = earlyDate
        emailDateEnd.eval_date = recentDate
        emailDateBegin.save()
        emailDateEnd.save()
        """
        timedelta_ = recentDate - earlyDate
        if timedelta_.days > 120:
             self.preprocessData(EmailData,eval_date)
        """
        return 1


    def _fillImsData(self):
        ims_log_list = []
        imsType_json = {"의견등록":"opinion","아이디어등록":"idea","임원창의":"board","임원창의의견":"board_opinion"}
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            employeeID_ = df_instance.id
            try:
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue

            imstype = imsType_json[df_instance.imstype.strip()]
            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)

            ims_log_obj = IMS_log(employeeID=employeeID, imstype=imstype, eval_date=eval_date)
            ims_log_list.append(ims_log_obj)
        IMS_log.objects.bulk_create(ims_log_list)
        return True


    def _fillApprovalData(self):
        approval_log_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            requesterID_ = df_instance.id1
            approverID_ = df_instance.id2
            try:
                requesterID = Employee.objects.get(id=requesterID_)
                approverID = Employee.objects.get(id=approverID_)
            except:
                continue

            eval_date = df_instance.eval_date
            approval_date = str(eval_date)[:5] + str(df_instance.approval_date)
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)
            if type(approval_date) == str:
                approval_date = self.__strEval_date_converter(approval_date)
            approval_log_obj = Approval_log(requesterID=requesterID, approverID=approverID, eval_date=eval_date,approve_date=approval_date)
            approval_log_list.append(approval_log_obj)
            print(requesterID_,end="\r")
        Approval_log.objects.bulk_create(approval_log_list)
        #self.preprocessData(ApprovalData)
        return True

    def _fillPcControlData(self):
        eval_date = datetime
        success = False
        pc_control_log_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            requesterID_ = df_instance.id
            try:
                requesterID = Employee.objects.get(id=requesterID_)
            except:
                continue

            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)

            approval_date = df_instance.approval_date
            if type(approval_date) == str:
                approval_date = self.__strEval_date_converter(approval_date)
            elif str(approval_date) == "None":
                print(approval_date)
                approval_date = datetime.datetime.now()
            pc_control_log_obj = PC_control_log(requesterID=requesterID, approval_date=approval_date, eval_date=eval_date)
            pc_control_log_list.append(pc_control_log_obj)
            success = True
        if not success:
            return False
        PC_control_log.objects.bulk_create(pc_control_log_list)
        #self.preprocessData(PC_control_Data)
        return True

    def _fillPcOutData(self):
        eval_date = datetime
        success = False
        pc_out_log_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            requesterID_ = df_instance.id
            try:
                requesterID = Employee.objects.get(id=requesterID_)
            except:
                continue

            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)

            pc_out_log_obj = PC_out_log(requesterID=requesterID, eval_date=eval_date)
            pc_out_log_list.append(pc_out_log_obj)
            success = True
        if not success:
            return False
        PC_out_log.objects.bulk_create(pc_out_log_list)
        #self.preprocessData(PC_out_Data)
        return True


    def _fillPortableOutData(self):
        eval_date = datetime
        success = False
        portable_out_log_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            requesterID_ = df_instance.id
            try:
                requesterID = Employee.objects.get(id=requesterID_)
            except:
                continue

            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)
            portable_out_log_obj = Portable_out_log(requesterID=requesterID, eval_date=eval_date)
            portable_out_log_list.append(portable_out_log_obj)
            success = True
        if not success:
            return False
        Portable_out_log.objects.bulk_create(portable_out_log_list)
        #self.preprocessData(Portable_out_Data)
        return True



    def _fillThanksData(self):
        thanks_log_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            thxs_sendID_ = df_instance.id_send
            thxs_receiveID_ = df_instance.id_receive
            thxs_follow_ = df_instance.id_follow
            thxType_ = {"감사노트":"thanksNote","감사문자":"thanksMsg","감사토큰":"thanksToken","감사편지":"thanksletter"}
            thxType  = thxType_[df_instance.type.strip()]
            followType_ = {"내용":"contents","공감":"like","댓글":"reply"}
            followType  = followType_[df_instance.followtype.strip()]
            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)
            try:
                sendID = Employee.objects.get(id = int(thxs_sendID_))
                thxSend = Thanks_log(employeeID=sendID, writerType = "send" ,thxType=thxType, followType=followType, eval_date=eval_date)
                thanks_log_list.append(thxSend)
                #print("sender %d \r"%int(thxs_sendID_))
            except:
                pass

            try:
                receiver_arr = re.findall("[0-9]+",thxs_receiveID_)
                for recieverid in  receiver_arr:
                    if Employee.objects.filter(id = recieverid).count() == 0:
                        continue
                    receiver =Employee.objects.get(id = recieverid)
                    thxreceiver = Thanks_log(employeeID=receiver,writerType = "receive" ,thxType=thxType, followType=followType, eval_date=eval_date)
                    thanks_log_list.append(thxreceiver)
                    #print("receiver %d \r"%int(recieverid))
            except:
                pass

            try:
                followerID = int(thxs_follow_)
                if Employee.objects.filter(id = followerID).count() == 0:
                    continue
                follower =Employee.objects.get(id = followerID)
                thxfollow= Thanks_log(employeeID=follower,writerType = "follow" ,thxType=thxType, followType=followType, eval_date=eval_date)
                thanks_log_list.append(thxfollow)
                #print("follower %d \r"%int(followerID))
            except:
                pass
        Thanks_log.objects.bulk_create(thanks_log_list)
        return True

    def _fillVdiIndiData(self):
        eval_date = datetime
        success = False
        vdi_indi_log_obj_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            user_indi_ID_ = df_instance.id
            useMinute = df_instance.useMinute
            try:
                user_indi_ID = Employee.objects.get(id=user_indi_ID_)
            except:
                continue

            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)

            vdi_indi_log_obj = VDI_indi_log(user_indi_ID=user_indi_ID,useMinute=useMinute,eval_date=eval_date)
            vdi_indi_log_obj_list.append(vdi_indi_log_obj)
            success = True

        if not success:
            return False
        VDI_indi_log.objects.bulk_create(vdi_indi_log_obj_list)
        #self.preprocessData(VDI_indi_Data)
        return True



    def _fillVdiShareData(self):
        eval_date = datetime
        success = False
        vdi_share_log_obj_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            user_share_ID_ = df_instance.id
            useMinute = df_instance.useMinute
            try:
                user_share_ID = Employee.objects.get(id=user_share_ID_)
            except:
                continue

            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)

            vdi_share_log_obj = VDI_share_log(user_share_ID=user_share_ID,useMinute=useMinute,eval_date=eval_date)
            vdi_share_log_obj_list.append(vdi_share_log_obj)
            success = True
        if not success:
            return False
        VDI_share_log.objects.bulk_create(vdi_share_log_obj_list)
        #self.preprocessData(VDI_share_Data)
        return True

    def _fillEcmData(self):
        eval_date = datetime
        success = False
        ecm_lig_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            userECMID_ = df_instance.id
            try:
                userECMID = Employee.objects.get(id=userECMID_)
            except:
                continue

            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)

            ecm_log_obj = ECM_log(userECMID=userECMID,eval_date=eval_date)
            ecm_lig_list.append(ecm_log_obj)
            success = True
        if not success:
            return True
        ECM_log.objects.bulk_create(ecm_lig_list)
        #self.preprocessData(ECMData)
        return True

    def _fillCafeteriaData(self):
        eval_date = datetime
        success = False
        cafeteria_log_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            buyerID_ = df_instance.id
            payment = df_instance.payment
            try:
                buyerID = Employee.objects.get(id=buyerID_)
            except:
                continue

            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = datetime.datetime.strptime(eval_date,"%Y-%m")

            cafeteria_log_obj = Cafeteria_log(buyerID=buyerID,payment=payment,eval_date=eval_date)
            cafeteria_log_list.append(cafeteria_log_obj)
            success = True
        if not success:
            return True
        Cafeteria_log.objects.bulk_create(cafeteria_log_list)
        #self.preprocessData(CafeteriaData)
        return True

    def _fillBlogData(self):
        eval_date = datetime
        success = False
        blog_log_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            blogID_ = df_instance.id
            try:
                blogID = Employee.objects.get(id=blogID_)
            except:
                continue

            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)

            blog_log_obj = Blog_log(blogID=blogID,eval_date=eval_date)
            blog_log_list.append(blog_log_obj)
            success = True
        if not success:
            return True
        Blog_log.objects.bulk_create(blog_log_list)
        #self.preprocessData(BlogData)
        return True


    def _fillCoreData(self):
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            coreID = df_instance.id
            try:
                empObj = Employee.objects.get(pk=coreID)
            except:
                continue
            empObj.coreyn = True
            empObj.save()
        return True


    def _fillRewardData(self):
        reward_log_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            rewardID_ = df_instance.id
            try:
                rewardID = Employee.objects.get(id=rewardID_)
            except:
                continue

            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)

            reward_log_obj = Reward_log(rewardID=rewardID,eval_date=eval_date)
            reward_log_list.append(reward_log_obj)
        Reward_log.objects.bulk_create(reward_log_list)
        return True



    def _fillScoreData(self):
        score_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
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
            eval_date = self.eval_date
            start_date = self.start_date
            empScore = Score(employeeID=employeeID, employeeID_confirm=employeeID_confirm,
                               score1=score1, score2=score2, score3=score3, score4=score4,
                               eval_date=eval_date,start_date=start_date)
            score_list.append(empScore)
        Score.objects.bulk_create(score_list)
        return True

    def _fillFlow(self):
        survey_day = Survey.objects.annotate(day=TruncDay('eval_date')).values('day')
        lastSurveyDate = survey_day.order_by("-day").first()["day"]
        df = pd.DataFrame(list(survey_day.filter(day = lastSurveyDate).values_list("employeeID_confirm","cct1","cct2","cct3","cct4","cct5")))
        df.columns = ["employeeID","cct1","cct2","cct3","cct4","cct5"]
        df.index = df.employeeID.values
        df["cctavg"] = (df.cct1 + df.cct4)/2
        df = df.drop(["employeeID","cct1","cct4"],1)
        df = df.dropna()
        y_pred = KMeans(n_clusters=3).fit_predict(df) + 1
        df["flow"] = y_pred
        flow_list = []
        for i in range(len(df)):
            df_instance = df.iloc[i, :]
            employeeID_ = df_instance.name
            try:
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue
            employeeID_confirm =  df_instance.name
            flow = int(df_instance.flow)
            eval_date = lastSurveyDate
            empFlow = Flow(employeeID=employeeID, employeeID_confirm=employeeID_confirm,
                            flow=flow,eval_date=eval_date,start_date = self.start_date)
            flow_list.append(empFlow)
        Flow.objects.bulk_create(flow_list)
        return True
