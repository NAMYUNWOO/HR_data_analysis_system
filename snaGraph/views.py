"""
from django.shortcuts import render
from dateutil.relativedelta import relativedelta
import json
import networkx as nx
from math import log
from networkx.readwrite import json_graph
from itertools import  chain
import pandas as pd
import time
from django.views.generic import View
from index.models import Employee,EmployeeBiography,EmailLog,SNAGraph
from django.db.models import F, Sum, Count, Case, When, Avg, Func, Max, Min
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.db.models import Q
import datetime,random
from django.http import HttpResponseRedirect, HttpResponse
from random import randint as rand


def getAreaColor(id):
    emp = EmployeeBiography.objects.filter(emoidN=id).distinct()[0]
    if emp.place == "포항":
        color = "#FF00FF"
    elif emp.place == "광양":
        color = "#ffb266"
    else:
        color = "#171796"
    return color


def getGraph(lastestDate_min,lastestDate_max):
    emailCount = EmailLog.objects.filter(Q(eval_date__gte = lastestDate_min) & Q(eval_date__lte = lastestDate_max)).values("sendID", "receiveID").annotate(weight=Count("sendID"))
    minval = list(emailCount.aggregate(Min("weight")).values())[0]
    emailCount = emailCount.filter(weight__gt= minval)
    node_size = {}
    G = nx.DiGraph()

    for em in emailCount:
        node1=em["sendID"]
        node2=em["receiveID"]
        weight = em["weight"]
        G.add_edge(node1, node2, weight=weight)


    G = G.to_undirected(reciprocal=True)

    # takes a lot of time
    pos_ = SNAGraph.objects.filter(Q(eval_date1=lastestDate_min) & Q(eval_date2=lastestDate_max))\
                           .values('employeeID_confirm', 'x', 'y')
    if pos_.count() != 0:
        pos = {i['employeeID_confirm']:[i['x'],i['y']] for i in pos_}
    else:
        pos =  nx.spring_layout(G,k=0.2)
        for key in pos:
            xy = pos[key]
            x = xy[0]
            y = xy[1]
            employeeID = Employee.objects.get(pk=key)
            snaG = SNAGraph(employeeID=employeeID,employeeID_confirm=key,eval_date1=lastestDate_min,
                            eval_date2=lastestDate_max,x=x,y=y)
            snaG.save()

    for source,target in G.edges:
        try:
            node_size[source] +=1
        except:
            node_size[source] = 1
        try:
            node_size[target] +=1
        except:
            node_size[target] = 1


    for n in node_size:
        node_size[n] = min(max(log(node_size[n]),1),10)

    fixNG = json_graph.node_link_data(G)

    g = {"nodes":[],"edges":[]}
    for n in fixNG["nodes"]:
        try:
            node_size_i = node_size[n["id"]]
            color = getAreaColor(n['id'])
            #x = rand(0, 100) / float(100)
            #y = rand(0, 100) / float(100)
            x = pos[n["id"]][0]
            y = pos[n["id"]][1]
            g["nodes"].append({"id": n["id"], "label": str(n["id"]), "x": x, "y": y,"size": node_size_i,"color":color,"borderColor":color})
        except:
            pass

    for link in fixNG["links"]:
        try:
            g["edges"].append({"source": link["source"], "target": link["target"], "id": str(link["source"])+"_to_"+str(link["target"]), "size": link["weight"]})
        except:
            pass

    return g

def snaGraph(request):

    date_min = request.POST.get('date_min', None)
    date_max = request.POST.get('date_max', None)
    if date_min == None and date_max == None:
        if EmailLog.objects.count() == 0:
            return HttpResponse({"nodes":[],"edges":[]}, content_type="application/json")
        lastestDate = EmailLog.objects.last().eval_date
        latest_year = lastestDate.year
        latest_month = lastestDate.month
        latest_day = lastestDate.day
        g = getGraph(lastestDate-datetime.timedelta(days=1),lastestDate)

        context = {"g": g,"latest_year":latest_year,"latest_month":latest_month,"latest_day":latest_day}
        return render(request, 'snaGraph.html', context)
    else:
        date_max = datetime.datetime.strptime(date_max[:15],"%a %b %d %Y")
        date_min = datetime.datetime.strptime(date_min[:15], "%a %b %d %Y")
        g = getGraph(date_min,date_max+datetime.timedelta(days=1))

    return HttpResponse(json.dumps(g), content_type="application/json")

"""