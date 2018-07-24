from django.db import models
from index.models import *
# Create your models here.
def modelList():
    modellist = [EmployeeBiography, Reward_log, Flow, Score, EmployeeGrade, Education, Survey, Trip,
                 EmailData, EmailLog, IMSData, IMS_log, ApprovalData, Approval_log, Portable_out_Data,
                 Portable_out_log, PC_out_Data, PC_control_Data, PC_out_log, PC_control_log, Thanks_Data,
                 Thanks_log, VDI_indi_Data, VDI_share_Data, VDI_indi_log, VDI_share_log, ECMData, ECM_log,
                 CafeteriaData, Cafeteria_log, BlogData, Blog_log]

    return modellist


def getDatelist2(Model):
    if Model.__name__.endswith('log'):
        dt_= Model.objects.order_by("-eval_date")
        if dt_.count() == 0:
            return ["0개의 업데이트"]
        return [str(dt_.last().eval_date)[:10] +" ~ "+ str(dt_.first().eval_date)[:10]]
    elif Model.__name__.endswith('EmailLog'):
        if EmailLog.objects.count() == 0:
            return ["0개의 업데이트"]
        return [str(EmailDateBeginEnd.objects.first().eval_date)[:10] +" ~ "+ str(EmailDateBeginEnd.objects.last().eval_date)[:10]]
    evaldate_startdate = Model.objects.order_by("-eval_date").values_list('eval_date','start_date').distinct()
    return list(map(lambda x: str(x[1])[:10] + " ~ " + str(x[0])[:10], evaldate_startdate))


def lastUpdateDates2(ModelList):
    zeroLenprocess = lambda x: ["0개의 없데이트"] if len(x) == 0 else x
    updateMat = [zeroLenprocess(getDatelist2(Model)) for Model in ModelList]
    return updateMat


def getRecentUpdateDates2():
    modelName = list(map(lambda x: x.__name__, modelList()))
    updateMat = lastUpdateDates2(modelList())
    logData = []
    hrData = []
    processedData = []
    scoreData = []
    for name_i, date_i in zip(modelName, updateMat):
        if 'score' in name_i.lower():
            scoreData.append((name_i, date_i))
            continue
        if name_i.endswith('log') or name_i.endswith('EmailLog'):
            logData.append((name_i, date_i))
        else:
            if 'data' in name_i.lower() or 'flow' in name_i.lower():
                processedData.append((name_i, date_i))
            else:
                hrData.append((name_i,date_i))
    return (logData,processedData,hrData,scoreData)


