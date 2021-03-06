# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-20 15:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Approval_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateTimeField()),
                ('approval_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ApprovalData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('approve_tot_request', models.FloatField(default=0, null=True)),
                ('approve_tot_sign', models.FloatField(default=0, null=True)),
                ('approve_mean_timeh', models.FloatField(default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Blog_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BlogData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('blog_tot_visit', models.FloatField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cafeteria_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('eval_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='CafeteriaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('food_tot_spend', models.FloatField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ECM_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ECMData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('ecm_before_in79', models.FloatField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('edu_nbr', models.FloatField(default=0, null=True)),
                ('toeic', models.BooleanField()),
                ('opic', models.BooleanField()),
                ('tsc', models.BooleanField()),
                ('sjpt', models.BooleanField()),
                ('edu_credit_in', models.FloatField(default=0, null=True)),
                ('edu_credit_out', models.FloatField(default=0, null=True)),
                ('edu_credit', models.FloatField(default=0, null=True)),
                ('lang_nbr', models.IntegerField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='EmailData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('email_between_1904_mean_send', models.FloatField(default=0, null=True)),
                ('email_month_var_receive', models.FloatField(default=0, null=True)),
                ('email_day_mean_receive', models.FloatField(default=0, null=True)),
                ('email_before_time79_daycnt', models.FloatField(default=0, null=True)),
                ('email_between_1904_daycnt_send', models.FloatField(default=0, null=True)),
                ('email_day_mean_send', models.FloatField(default=0, null=True)),
                ('sna_outdegree', models.FloatField(default=0, null=True)),
                ('sna_closeness', models.FloatField(default=0, null=True)),
                ('buha_closeness', models.FloatField(default=0, null=True)),
                ('dongryo_closeness', models.FloatField(default=0, null=True)),
                ('sangsa_eigenvector', models.FloatField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailDateBeginEnd',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('eval_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Emaileigvec',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('eigvec', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('eval_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('bu', models.CharField(max_length=50, null=True)),
                ('place', models.CharField(max_length=30, null=True)),
                ('empname', models.CharField(max_length=30, null=True)),
                ('coreyn', models.BooleanField(default=False)),
                ('age', models.FloatField(null=True)),
                ('work_duration', models.FloatField(default=0)),
                ('sex', models.BooleanField()),
                ('pmlevel', models.IntegerField(null=True)),
                ('level', models.IntegerField(null=True)),
                ('email', models.CharField(default='', max_length=50)),
                ('istarget', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeBiography',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('bu', models.CharField(max_length=50, null=True)),
                ('place', models.CharField(max_length=30, null=True)),
                ('empname', models.CharField(max_length=30, null=True)),
                ('coreyn', models.BooleanField(default=False)),
                ('age', models.FloatField(null=True)),
                ('work_duration', models.FloatField(default=0)),
                ('sex', models.BooleanField()),
                ('pmlevel', models.IntegerField(null=True)),
                ('level', models.IntegerField(null=True)),
                ('email', models.CharField(default='', max_length=50)),
                ('istarget', models.BooleanField(default=True)),
                ('start_date', models.DateTimeField()),
                ('eval_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('grade_sv_y_2', models.FloatField(null=True)),
                ('grade_sv_y_1', models.FloatField(null=True)),
                ('grade_sv_r2_avg', models.FloatField(null=True)),
                ('grade_co_y', models.FloatField(null=True)),
                ('grade_4', models.FloatField(null=True)),
                ('grade_3', models.FloatField(null=True)),
                ('grade_2', models.FloatField(null=True)),
                ('grade_1', models.FloatField(null=True)),
                ('grade_r2_avg', models.FloatField(null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='EP_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateTimeField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='EPData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('ep_access_day_mean', models.FloatField(default=0, null=True)),
                ('ep_access_day_var', models.FloatField(default=0, null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Flow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('flow', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='IMS_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imstype', models.CharField(max_length=20)),
                ('eval_date', models.DateTimeField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='IMSData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('ims_tot_enroll', models.FloatField(default=0, null=True)),
                ('ims_tot_opinion_enroll', models.FloatField(default=0, null=True)),
                ('ims_tot_idea_enroll', models.FloatField(default=0, null=True)),
                ('ims_tot_board_enroll', models.FloatField(default=0, null=True)),
                ('ims_tot_board_opinion_enroll', models.FloatField(default=0, null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='M_EP_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateTimeField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='M_EPData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('mep_early_tot', models.FloatField(default=0, null=True)),
                ('mep_late_tot', models.FloatField(default=0, null=True)),
                ('mep_early_day', models.FloatField(default=0, null=True)),
                ('mep_late_day', models.FloatField(default=0, null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Meeting_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateTimeField()),
                ('eval_date2', models.DateTimeField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='MeetingData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('meeting_join_count', models.FloatField(default=0, null=True)),
                ('mean_meeting_time', models.FloatField(default=0, null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='PC_control_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('pccontrol_mean_timeh', models.FloatField(default=0, null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='PC_control_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_date', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('eval_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('requesterID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='PC_out_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('pcout_tot_request', models.FloatField(default=0, null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='PC_out_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('requesterID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='PCM_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateTimeField()),
                ('pcm_tot_enroll', models.FloatField(default=0, null=True)),
                ('pcm_tot_remove', models.FloatField(default=0, null=True)),
                ('pcm_tot_check', models.FloatField(default=0, null=True)),
                ('pcm_tot_checked', models.FloatField(default=0, null=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='PCMData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('pcm_tot_enroll', models.FloatField(default=0, null=True)),
                ('pcm_tot_remove', models.FloatField(default=0, null=True)),
                ('pcm_tot_check', models.FloatField(default=0, null=True)),
                ('pcm_tot_checked', models.FloatField(default=0, null=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Portable_out_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('porta_tot_request', models.FloatField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Portable_out_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('requesterID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Reward_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_date', models.DateTimeField()),
                ('rewardID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('score1', models.FloatField(default=0)),
                ('score2', models.FloatField(default=0)),
                ('score3', models.FloatField(default=0)),
                ('score4', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='SNAGraph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date1', models.DateTimeField()),
                ('eval_date2', models.DateTimeField()),
                ('x', models.FloatField(default=0, null=True)),
                ('y', models.FloatField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('cct1', models.FloatField(null=True)),
                ('cct2', models.FloatField(null=True)),
                ('cct3', models.FloatField(null=True)),
                ('cct4', models.FloatField(null=True)),
                ('cct5', models.FloatField(null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Thanks_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('thank_letter_tot_receive', models.FloatField(default=0, null=True)),
                ('thank_token_tot_receive', models.FloatField(default=0, null=True)),
                ('thank_msg_tot_receive', models.FloatField(default=0, null=True)),
                ('thank_note_tot_receive', models.FloatField(default=0, null=True)),
                ('thank_letter_tot_send', models.FloatField(default=0, null=True)),
                ('thank_token_tot_send', models.FloatField(default=0, null=True)),
                ('thank_msg_tot_send', models.FloatField(default=0, null=True)),
                ('thank_note_tot_send', models.FloatField(default=0, null=True)),
                ('thank_like_tot', models.FloatField(default=0, null=True)),
                ('thank_reply_tot', models.FloatField(default=0, null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Thanks_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thxType', models.CharField(max_length=20)),
                ('writerType', models.CharField(max_length=20)),
                ('followType', models.CharField(max_length=20)),
                ('eval_date', models.DateField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('trip_domestic', models.FloatField(default=0, null=True)),
                ('trip_town', models.FloatField(default=0, null=True)),
                ('trip_abroad', models.FloatField(default=0, null=True)),
                ('annual_vacation_gen_dt', models.DateField(null=True)),
                ('annual_vacation_gen_amt', models.FloatField(default=0, null=True)),
                ('annual_vacation_gen_usage', models.FloatField(default=0, null=True)),
                ('btrip_nbr', models.FloatField(default=0, null=True)),
                ('off_use_pct_permon', models.FloatField(default=0, null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='VDI_indi_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('vdi_indi_mean_timem', models.FloatField(default=0, null=True)),
                ('vdi_indi_tot_access', models.FloatField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='VDI_indi_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('useMinute', models.FloatField(default=0)),
                ('eval_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user_indi_ID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='VDI_share_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('vdi_share_mean_time', models.FloatField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='VDI_share_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('useMinute', models.FloatField(default=0)),
                ('eval_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user_share_ID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee')),
            ],
        ),
        migrations.AddField(
            model_name='emaillog',
            name='receiveID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiveID', to='index.Employee'),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='sendID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sendID', to='index.Employee'),
        ),
        migrations.AddField(
            model_name='emaileigvec',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee'),
        ),
        migrations.AddField(
            model_name='emaildata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee'),
        ),
        migrations.AddField(
            model_name='education',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee'),
        ),
        migrations.AddField(
            model_name='ecmdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee'),
        ),
        migrations.AddField(
            model_name='ecm_log',
            name='userECMID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee'),
        ),
        migrations.AddField(
            model_name='cafeteriadata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee'),
        ),
        migrations.AddField(
            model_name='cafeteria_log',
            name='buyerID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee'),
        ),
        migrations.AddField(
            model_name='blogdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee'),
        ),
        migrations.AddField(
            model_name='blog_log',
            name='blogID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee'),
        ),
        migrations.AddField(
            model_name='approvaldata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Employee'),
        ),
        migrations.AddField(
            model_name='approval_log',
            name='approverID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approverID', to='index.Employee'),
        ),
        migrations.AddField(
            model_name='approval_log',
            name='requesterID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requesterID', to='index.Employee'),
        ),
    ]
