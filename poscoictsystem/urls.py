"""poscoictsystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from index.views import Index
from employee.views import employee
from region.views import Region
#from snaGraph.views import snaGraph
from dataIO.views import dataIO
from guide.views import guide
from bu_group.views import BuGroup
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',Index.as_view(),name='index'),
    url(r'^id=(?P<id>.*)/$',employee,name='employee'),
    url(r'^region_(?P<region>.*)/$',Region.as_view(),name='region'),
    #url(r'^snaGraph/$',snaGraph,name='snaGraph'),
    url(r'^dataIO/$',dataIO,name='dataIO'),
    url(r'^guide/$',guide,name='guide'),
    url(r'^bu_(?P<bu>.*)/$',BuGroup.as_view(),name='buGroup'),
]