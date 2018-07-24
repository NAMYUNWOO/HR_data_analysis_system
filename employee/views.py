from django.shortcuts import render
from index.views import get_Bu_buUrl
from index.models import EmployeeBiography, Reward_log, Flow, Score, EmployeeGrade, Education, Survey, Trip, EmailData, IMSData, ApprovalData, Portable_out_Data, PC_out_Data,PC_control_Data, Thanks_Data, VDI_indi_Data,VDI_share_Data,  ECMData, CafeteriaData, BlogData
from index.views import LineChart
from django.db.models import F
from django.urls import reverse
from django.http import HttpResponseRedirect

# Create your views here.


def lineChartGen(Model,empobj,fields,labels):
    the_counts={"the_count"+str(idx+1):F(i) for idx,i in enumerate(fields)}
    modelVals = list(the_counts.keys()) +['eval_date']
    modelObj = Model.objects.filter(employeeID = empobj).annotate(**the_counts).values(*modelVals).order_by('eval_date')
    lineChart = LineChart()
    lineChart.getXdataYdata(modelObj,labels)
    return lineChart

def getScore(id):
    empScores = Score.objects.filter(employeeID = id).order_by('-eval_date')
    if empScores.count() == 0:
        return [None]*4
    recentScore = list(empScores.values_list('score1','score2','score3','score4'))[0]
    scores = list(map(lambda x:'%.1f' % round(x, 2),recentScore))
    return scores

def employee(request,id):
    # search
    if request.method == 'GET':
        search_query = request.GET.get('search_box', None)
        if search_query != None:
            return HttpResponseRedirect(reverse('employee', args=[search_query]))


    # error 처리 and 결과 없음 처리
    try:
        empobj = EmployeeBiography.objects.get(pk=id)

    except:
        return render(request, 'employee.html',{"fail":id,})






    email_lineChart= lineChartGen(EmailData,empobj,
                                  ["email_between_1904_mean_send", "email_month_var_receive", "email_day_mean_receive",
                                   "email_between_0709_daycnt_send", "email_between_1904_daycnt_send", "email_day_mean_send",
                                    "sna_closeness", "buha_closeness", "dongryo_closeness",
                                   "sangsa_eigenvector"],
                                        ["19-04 메일사용평균","수신분산(월)","수신평균(일)",
                                         "07-09 메일사용","19-04 메일사용횟수","발신평균(일)",
                                         "근접중심성","부하 근접중심성","동료 근접중심성",
                                         "상사 위세중심성"])

    score_avgLineChart = lineChartGen(Score,empobj,
                                           ['score1','score2','score3','score4'],
                                           ['몰입', '성과', '핵심', '업무'])

    grade_lineChart= lineChartGen(EmployeeGrade,empobj,
                                        ['grade_1', 'grade_r2_avg', 'grade_co_y', 'grade_sv_r2_avg'],
                                        ['성과평가-1', '성과2년평균', '동료평가', '상사평가 2년평균'])

    edu_lineChart= lineChartGen(Education,empobj,
                                        ['edu_nbr','edu_credit','lang_nbr'],
                                        ['과정수','이수학점','외국어점수보유'])

    survey_lineChart= lineChartGen(Survey,empobj,
                                        ['cct1','cct2','cct3','cct4','cct5'],
                                        ['13번질문','14번질문','15번질문','16번질문','17번질문'])

    trip_lineChart= lineChartGen(Trip,empobj,
                                        ['btrip_nbr'],
                                        ['1년간 출장일수'])

    holiday_lineChart= lineChartGen(Trip,empobj,
                                        ['off_use_pct_permon'],
                                        ['월평균 연차소진률'])

    ims_lineChart= lineChartGen(IMSData,empobj,
                                        ["ims_tot_enroll", "ims_tot_opinion_enroll"],
                                        ['IMS 등록수', 'IMS 의견등록수'])

    approval_lineChart= lineChartGen(ApprovalData,empobj,
                                        ["approve_tot_request", "approve_tot_sign"],
                                        ['결재요청 수', '결재사인 수'])

    portable_lineChart= lineChartGen(Portable_out_Data,empobj,
                                        ["porta_tot_request"],
                                        ["휴대장치반출 요청"])

    pcout_lineChart= lineChartGen(PC_out_Data,empobj,
                                        ["pcout_tot_request"],
                                        ["PC반출 요청"])

    pccontrol_lineChart= lineChartGen(PC_control_Data,empobj,
                                        ["pccontrol_mean_timeh"],
                                        ["PC컨트롤 요청 응답시간(H)"])

    thank_lineChart= lineChartGen(Thanks_Data,empobj,
                                        ["thank_letter_tot_receive","thank_receive"],
                                        ['감사편지수신', '감사수신'])

    vdishare_lineChart= lineChartGen(VDI_share_Data,empobj,
                                        ["vdi_share_mean_time"],
                                        ['공용vdi사용'])
    vdiindi_lineChart= lineChartGen(VDI_indi_Data,empobj,
                                        ["vdi_indi_mean_timem"],
                                        ['개인vdi사용'])
    ecm_lineChart= lineChartGen(ECMData,empobj,
                                        ["ecm_before_in79"],
                                        ['AM 07~09 ECM사용'])
    cafe_lineChart= lineChartGen(CafeteriaData,empobj,
                                        ["food_tot_spend"],
                                        ['카페사용총액'])

    blog_lineChart= lineChartGen(BlogData,empobj,
                                        ["blog_tot_visit"],
                                        ['블로그방문횟수'])


    context = {"bu":get_Bu_buUrl(),
               "scoreAvg":getScore(id),
               "empID":id, "name":empobj.empname,
               "score": score_avgLineChart,
               "place":empobj.place,"coreyn":empobj.coreyn,
               "sex":empobj.sex,
               "bu_emp":empobj.bu,"age":int(empobj.age),
               "workduration":int(empobj.work_duration),
               "pmlevel":empobj.pmlevel, "istarget":empobj.istarget,
               "emailaddr":empobj.email,"포상":empobj.rewardyn,
               "grade":grade_lineChart,
               "edu":edu_lineChart,
               "survey":survey_lineChart,
               "trip":trip_lineChart,
               "holiday":holiday_lineChart,
               "email":email_lineChart,
               "ims":ims_lineChart,
               "approval":approval_lineChart,
               "portable":portable_lineChart,
               "pcout":pcout_lineChart,
               "pccontrol":pccontrol_lineChart,
               "thank":thank_lineChart,
               "ecm": ecm_lineChart,
               "vdiShare":vdishare_lineChart,
               "vdiIndi":vdiindi_lineChart,
               "cafe":cafe_lineChart,
               "blog":blog_lineChart
               }
    return render(request, 'employee.html',context)