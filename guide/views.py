from django.shortcuts import render
from index.views import get_Bu_buUrl
from urllib import parse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
# Create your views here.

def guide(request):
    if request.method == 'GET':
        search_query = request.GET.get('search_box', None)
        if search_query != None:
            return HttpResponseRedirect(reverse('employee', args=[search_query]))

    return render(request,"guide.html",context={"bu":get_Bu_buUrl()})