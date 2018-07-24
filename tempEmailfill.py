import pandas as pd
from index.models import *
import datetime

def insertEmail():
    email= pd.read_csv("../etc/emaildata.csv",sep=";",header=None,usecols=[1,2,4])
    email.columns = ["sendID","receiveID","eval_date"]
    emaillogs= []
    earlyDate = EmailDateBeginEnd.objects.get(pk=0).eval_date
    recentDate = EmailDateBeginEnd.objects.get(pk=1).eval_date
    for i in range(0,len(email)):
        instance_i = email.iloc[i,:]
        sendID = instance_i.sendID
        receiveID = instance_i.receiveID
        eval_date = instance_i.eval_date
        print("%d sends to %d at %s"%(sendID,receiveID,str(eval_date)),end="\t")
        try:
            sendID = Employee.objects.get(id=sendID)
            receiveID = Employee.objects.get(id=receiveID)
        except:
            continue
        eval_date = datetime.datetime.strptime(eval_date,"%Y-%m-%d %H:%M:%S")
        emaillogs.append(EmailLog(sendID =sendID,receiveID =receiveID, eval_date = eval_date))
        earlyDate = min(earlyDate,eval_date)
        recentDate = max(eval_date,recentDate)
        print("valid",end="\r")
        if i%10000 == 0:
            EmailLog.objects.bulk_create(emaillogs)
            emaillogs = []
            emailDateBegin = EmailDateBeginEnd.objects.get(pk=0)
            emailDateEnd = EmailDateBeginEnd.objects.get(pk=1)
            emailDateBegin.eval_date = earlyDate
            emailDateEnd.eval_date = recentDate
            emailDateBegin.save()
            emailDateEnd.save()
    EmailLog.objects.bulk_create(emaillogs)
    emailDateBegin = EmailDateBeginEnd.objects.get(pk=0)
    emailDateEnd = EmailDateBeginEnd.objects.get(pk=1)
    emailDateBegin.eval_date = earlyDate
    emailDateEnd.eval_date = recentDate
    emailDateBegin.save()
    emailDateEnd.save()

if __name__ == "__main__":
    main()
