from django.shortcuts import render
from index.views import Index
# Create your views here.
class BuGroup(Index):
    def get(self,request,bu):
        isGet = self.getRequestSearch(request)
        if isGet != None:
            return isGet
        context = self.getContext(bu=bu)
        return render(request,'buGroup.html',context)
