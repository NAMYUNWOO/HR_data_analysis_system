from django.shortcuts import render
import time
import random
from django.views.generic import View
from index.models import *
from django.db.models import F, Sum, Count, Case, When, Avg, Func
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.db.models import Q
import datetime
from django.http import HttpResponseRedirect, HttpResponse
from jchart import Chart
from jchart.config import Axes, DataSet, rgba
from dataIO.views import getRecentUpdateDates
from urllib import parse
# Create your views here.





def get_Bu_buUrl():
    bu = [list(i.values())[0] for i in list(EmployeeBiography.objects.values("bu").distinct()) if
          list(i.values())[0] != None]
    buUrl = [parse.quote(i) for i in bu]
    bu_buUrl = [(i, j) for i, j in zip(bu, buUrl)]
    return bu_buUrl

class LineChart(Chart):
    chart_type = 'line'
    scales = {
        'xAxes': [Axes(type='time', position='bottom')],
    }

    def getXdataYdata(self,querySet,labels):
        if querySet.count() == 0:
            self.myLabel = labels
            self.ydataArr = [[0]]
            self.xdata = [0]
            return 0
        self.myLabel = labels
        n = len(querySet[0])
        self.ydataArr = [[j["the_count" + str(1 + i)] for j in querySet] for i in range(n - 1)]
        self.xdata = [i['eval_date'] for i in querySet]
        return 0

    def get_datasets(self, **kwargs):
        colors = [
            (255, 99, 132),
            (54, 162, 235),
            (255, 206, 86),
            (75, 192, 192),
            (153, 102, 255),
            (255, 159, 64),
            (142, 68, 173),
            (23, 165, 137),
            (241, 196, 15),
            (51, 255, 66),
            (255, 51, 249)
        ]
        dataSetArr = []
        def roud_None(y):
            try:
                return '%.1f' % round(y, 2)
            except:
                None

        for ydata,label,color in zip(self.ydataArr,self.myLabel,colors[:len(self.myLabel)]):
            data_i = []
            for x,y in zip(self.xdata,ydata):
                data_i.append({"y": roud_None(y), "x": str(x)})

            DataSet_i = DataSet(type='line',
                                label = label,
                                data=data_i,
                                color=color,
                                fill=False)
            dataSetArr.append(DataSet_i)
        return dataSetArr



class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 0)'

class PieChartdata:
    def __init__(self,querySet,queryset_objects,label = {},numToStr = None):
        self.qs = querySet
        self.qsobj = queryset_objects
        self.xdata,self.ydata = self.__getXdataYdata(label,numToStr)

    def __getXdataYdata(self,label,numToStr):
        xy_data = [[i[self.qsobj], int(i["the_count"])] for i in self.qs]
        if label != {} and numToStr != None :
            xdata = list(map(lambda x: str(label[x[0]]) + numToStr, xy_data))
        elif label != {} and numToStr == None :
            xdata = list(map(lambda x: label[x[0]], xy_data))
        elif label == {} and numToStr != None :
            xdata = list(map(lambda x: str(int(x[0])) + numToStr, xy_data))
        else:
            xdata = list(map(lambda x: x[0], xy_data))
        ydata = list(map(lambda x: x[1], xy_data))
        return xdata,ydata

    def getchartDataType(self):
        extra_serie = {"tooltip": {"y_start": "", "y_end": " 명"}}
        chartdata = {'x': self.xdata, 'y1': self.ydata, 'extra1': extra_serie}
        charttype = "pieChart"
        return chartdata,charttype



def getRecentUpdateDate_str():
    dateList = getRecentUpdateDates()
    arr = []
    for name_dt in dateList:
        if name_dt[1][0] == "0개의 업데이트":
            continue
        dt = datetime.datetime.strptime(name_dt[1][0],"%Y-%m-%d")
        arr.append(dt)
    if len(arr) == 0:
        return "0개의 업데이트"
    else:
        recentDt = max(arr)
    return str(recentDt)

class Index(View):

    def get(self,request):
        isGet = self.getRequestSearch(request)
        if isGet != None:
            return isGet
        context = self.getContext()
        return render(request,'index.html',context)

    def lineChartGen(self,Model, fields, labels):
        the_counts = {"the_count" + str(idx + 1): Avg(i) for idx, i in enumerate(fields)}
        modelObj = Model.values("eval_date").annotate(**the_counts).order_by("eval_date")
        lineChart = LineChart()
        lineChart.getXdataYdata(modelObj, labels)
        return lineChart

################## refactoring target #########################################################
    def getEmpBioObj(self):
        if self.bu == None:
            empBioAll = Employee.objects.filter(istarget=True)
            if self.region == "all":
                return empBioAll
            elif self.region == "seoul_gyeongi":
                return empBioAll.filter(Q(place="서울")|Q(place="판교")|Q(place="센터"))
            elif self.region == "gwangyang":
                return empBioAll.filter(place="광양")
            else:
                return empBioAll.filter(place="포항")
        else:
            empBioAll = EmployeeBiography.objects.filter(bu=self.bu)
            return empBioAll

    def getEmpObj(self,Model):
        if self.bu == None:
            empObjAll = Model.objects.filter(employeeID__istarget=True)
            if self.region == "all":
                return empObjAll
            elif self.region == "seoul_gyeongi":
                return empObjAll.annotate(place=F('employeeID__place')).filter(Q(place="서울") | Q(place="판교") | Q(place="센터"))
            elif self.region == "gwangyang":
                return  empObjAll.annotate(place=F('employeeID__place')).filter(place="광양")
            else:
                return empObjAll.annotate(place=F('employeeID__place')).filter(place="포항")
        else:
            empBioAll = Model.objects.filter(employeeID__bu=self.bu)
            return empBioAll

################## refactoring target #########################################################


    def getRequestSearch(self,request):
        if request.method == 'GET':
            search_query = request.GET.get('search_box', None)
            if search_query != None:
                return HttpResponseRedirect(reverse('employee', args=[search_query]))
        return None


    def getContext(self,region="all",bu=None):
        self.region = region
        self.bu = bu
        ################## pieChart #########################################################
        empBioObj = self.getEmpBioObj()
        place_count = empBioObj.values("place").annotate(the_count=Count('place'))
        coreyn_count = empBioObj.values("coreyn").annotate(the_count=Count('coreyn'))
        sex_count = empBioObj.values("sex").annotate(the_count=Count('sex'))
        ageRange_count = empBioObj.values("age").annotate(ageRange=Round(F('age') / 10) * 10
                                                         ).values('ageRange').annotate(the_count=Count("ageRange"))

        chartdataPlace, charttypePlace = PieChartdata(place_count, "place").getchartDataType()

        chartdataCore, charttypeCore = PieChartdata(coreyn_count, "coreyn", {True: "핵심", False: "보통"}) \
            .getchartDataType()
        chartdataSex, charttypeSex = PieChartdata(sex_count, "sex", {False: "여자", True: "남자"}) \
            .getchartDataType()
        chartdataAge, charttypeAge = PieChartdata(ageRange_count, "ageRange", {}, " 대") \
            .getchartDataType()

        ################ PieChart End #######################################################

        ################ Get Scores #######################################################
        def rounding_none(x):
            if x == None:
                return x
            return '%.1f' % round(x, 2)

        scores_ = self.getEmpObj(Score).aggregate(score1 = Avg('score1'),score2 = Avg('score2'),score3 = Avg('score3'),score4 = Avg('score4'))
        scores = list(map(lambda x:rounding_none(x),[scores_['score1'],scores_['score2'],scores_['score3'],scores_['score4']]))



        ################ Scores End #######################################################



        ################## lineChart #########################################################
        email_avgLineChart = self.lineChartGen(self.getEmpObj(EmailData),
                                  ["email_between_1904_mean_send", "email_month_var_receive", "email_day_mean_receive",
                                   "email_between_0709_daycnt_send", "email_between_1904_daycnt_send", "email_day_mean_send",
                                    "sna_closeness", "buha_closeness", "dongryo_closeness",
                                   "sangsa_eigenvector"],
                                        ["19-04 메일사용평균","수신분산(월)","수신평균(일)",
                                         "07-09 메일사용","19-04 메일사용횟수","발신평균(일)",
                                         "근접중심성","부하 근접중심성","동료 근접중심성",
                                         "상사 위세중심성"])


        score_avgLineChart = self.lineChartGen(self.getEmpObj(Score),
                                           ['score1','score2','score3','score4'],
                                           ['몰입', '성과', '핵심', '업무'])



        grade_avgLineChart = self.lineChartGen(self.getEmpObj(EmployeeGrade),
                                           ['grade_1','grade_r2_avg','grade_co_y','grade_sv_r2_avg'],
                                           ['성과평가-1','성과2년평균', '동료평가','상사평가 2년평균'])



        edu_avgLineChart = self.lineChartGen(self.getEmpObj(Education),
                                        ['edu_nbr','edu_credit','lang_nbr'],
                                        ['과정수','이수학점','외국어점수보유'])




        survey_avgLineChart =  self.lineChartGen(self.getEmpObj(Survey),
                                        ['cct1','cct2','cct3','cct4','cct5'],
                                        ['13번질문','14번질문','15번질문','16번질문','17번질문'])

        trip_avgLineChart = self.lineChartGen(self.getEmpObj(Trip),
                                      ['btrip_nbr'],
                                      ['1년간 출장일수'])

        holiday_avgLineChart = self.lineChartGen(self.getEmpObj(Trip),
                                         ['off_use_pct_permon'],
                                         ['월평균 연차소진률'])
        ims_avgLineChart = self.lineChartGen(self.getEmpObj(IMSData),
                                     ["ims_tot_enroll", "ims_tot_opinion_enroll"],
                                     ['IMS 등록수', 'IMS 의견등록수'])

        approval_avgLineChart = self.lineChartGen(self.getEmpObj(ApprovalData),
                                          ["approve_tot_request", "approve_tot_sign"],
                                          ['결재요청 수', '결재사인 수'])

        portable_avgLineChart = self.lineChartGen(self.getEmpObj(Portable_out_Data),
                                          ["porta_tot_request"],
                                          ["휴대장치반출 요청"])

        pcout_avgLineChart = self.lineChartGen(self.getEmpObj(PC_out_Data),
                                       ["pcout_tot_request"],
                                       ["PC반출 요청"])

        pccontrol_avglineChart = self.lineChartGen(self.getEmpObj(PC_control_Data),
                                           ["pccontrol_mean_timeh"],
                                           ["PC컨트롤 요청 응답시간(H)"])

        thank_avgLineChart = self.lineChartGen(self.getEmpObj(Thanks_Data),
                                       ["thank_letter_tot_receive", "thank_letter_tot_send"],
                                       ['감사편지수신', '감사편지발신'])

        vdiShare_avgLineChart = self.lineChartGen(self.getEmpObj(VDI_share_Data),
                                          ["vdi_share_mean_time"],
                                          ['공용vdi사용'])
        vdiIndi_avgLineChart = self.lineChartGen(self.getEmpObj(VDI_indi_Data),
                                         ["vdi_indi_mean_timem"],
                                         ['개인vdi사용'])
        ecm_avgLineChart = self.lineChartGen(self.getEmpObj(ECMData),
                                     ["ecm_before_in79"],
                                     ['AM 07~09 ECM사용'])
        cafe_avgLineChart = self.lineChartGen(self.getEmpObj(CafeteriaData),
                                      ["food_tot_spend"],
                                      ['카페사용총액'])

        blog_avgLineChart = self.lineChartGen(self.getEmpObj(BlogData),
                                      ["blog_tot_visit"],
                                      ['블로그방문횟수'])
        ################ lineChart End #######################################################






        context = {
            "bu":get_Bu_buUrl(),
            "currentBu":self.bu,
            'scoreAvg':scores,
            "recentUpdateDate":  getRecentUpdateDate_str(),
            "employee_size": empBioObj.count(),
            "charttypePlace": charttypePlace,
            "chartdataPlace": chartdataPlace,
            "charttypeCore": charttypeCore,
            "chartdataCore": chartdataCore,
            "charttypeSex": charttypeSex,
            "chartdataSex": chartdataSex,
            "charttypeAge": charttypeAge,
            "chartdataAge": chartdataAge,
            "score":score_avgLineChart,
            "grade": grade_avgLineChart,
            "edu": edu_avgLineChart,
            "survey": survey_avgLineChart,
            "trip": trip_avgLineChart,
            "holiday": holiday_avgLineChart,
            "email": email_avgLineChart,
            "ims": ims_avgLineChart,
            "approval": approval_avgLineChart,
            "portable": portable_avgLineChart,
            "pcout": pcout_avgLineChart,
            "pccontrol": pccontrol_avglineChart,
            "thank": thank_avgLineChart,
            "vdiShare": vdiShare_avgLineChart,
            "vdiIndi": vdiIndi_avgLineChart,
            "ecm": ecm_avgLineChart,
            "cafe": cafe_avgLineChart,
            "blog": blog_avgLineChart

        }
        if self.region == "all":
            context["region"] = "POSCO ICT"
        elif self.region == "seoul_gyeongi":
            context["region"] = "센터.분당"
        elif self.region == "gwangyang":
            context["region"] = "광양"
        else:
            context["region"] = "포항"
        return context
