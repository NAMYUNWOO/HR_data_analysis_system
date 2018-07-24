from django.contrib import admin
from index.models import EmployeeBiography, Reward_log, Flow, Score, EmployeeGrade, Education, Survey, Trip, EmailData, EmailLog, IMSData, IMS_log, ApprovalData, Approval_log, Portable_out_Data, Portable_out_log, PC_out_Data,PC_control_Data,PC_out_log, PC_control_log, Thanks_Data, Thanks_log, VDI_indi_Data,VDI_share_Data ,VDI_indi_log, VDI_share_log, ECMData, ECM_log, CafeteriaData, Cafeteria_log, BlogData, Blog_log
# Register your models here.

admin.site.register(EmployeeBiography)
admin.site.register(EmployeeGrade)
admin.site.register(Education)
admin.site.register(Survey)
admin.site.register(Trip)
admin.site.register(EmailLog)
