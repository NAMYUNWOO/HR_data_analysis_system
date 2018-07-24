from django.shortcuts import render
from index.views import Index

# Create your views here.
class Region(Index):
    def get(self,request,region):
        isGet = self.getRequestSearch(request)
        if isGet != None:
            return isGet
        context = self.getContext(region=region)
        return render(request,'region.html',context)
