from django import forms
from django.forms.extras.widgets import SelectDateWidget
from index.models import *
from .models import *


MODELNAMES = list(map(lambda x:x.__name__,modelList()[1:]))


class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

class DateRangePickForm(forms.Form):
    start_date = forms.DateField(label="기준일 선택",widget=SelectDateWidget(years=range(2016, 2024)))


class remove_choice_Form(forms.Form):
    MODELZ = [
        (i, (name_i))
        for i,name_i in enumerate(MODELNAMES)
    ]
    prefix = forms.ChoiceField(label="데이터",choices=MODELZ)
    start_date = forms.DateField(label="From",widget=SelectDateWidget(years=range(2016, 2024)))
    end_date = forms.DateField(label="To", widget=SelectDateWidget(years=range(2016, 2024)))



'''
    Log 데이터 form
    LogDataSelect0 ~ LogDataSelect12
'''

class LogDataSelect(forms.Form):


    def __init__(self,*args,**kwargs):
        model = kwargs.pop('model')
        modelname = model.__name__
        super(LogDataSelect,self).__init__(*args,**kwargs)
        DATARANGE = [(i,(name_i)) for i,name_i in  enumerate(getDatelist2(model))]
        self.fields['prefix'].choices = DATARANGE
        self.fields['prefix'].label = modelname
        self.dataRange = DATARANGE[0][1]

    dataRange = ""
    prefix = forms.ChoiceField(label="", choices=[])
    start_date = forms.DateField(label="From",widget=SelectDateWidget(years=range(2016, 2024)))
    end_date = forms.DateField(label="To", widget=SelectDateWidget(years=range(2016, 2024)))




class StructuredDataSelect(forms.Form):
    def __init__(self,*args,**kwargs):
        model = kwargs.pop('model')
        modelname = model.__name__
        super(StructuredDataSelect,self).__init__(*args,**kwargs)
        DATARANGE = [(i,(name_i)) for i,name_i in  enumerate(getDatelist2(model))]
        self.fields['prefix'].choices = DATARANGE
        self.fields['prefix'].label = modelname

    prefix = forms.ChoiceField(label="",choices=[])
    start_date = forms.DateField(label="From",widget=SelectDateWidget(years=range(2016, 2024)))
    end_date = forms.DateField(label="To", widget=SelectDateWidget(years=range(2016, 2024)))
