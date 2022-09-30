from django.contrib import admin
from . import  models

admin.site.register(models.StudentAuthProfile)
admin.site.register(models.StudentPersonalProfile)
admin.site.register(models.JobProfile)
admin.site.register(models.HackathonProfile)
admin.site.register(models.OnlineCoursesProfile)
admin.site.register(models.OtherDocuments)
