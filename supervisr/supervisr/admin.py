from django.contrib import admin
from supervisr.models import *
# Register your models here.
admin.site.register(ServerProduct)
admin.site.register(ServerCPU)
admin.site.register(ServerDrive)
admin.site.register(ServerNIC)
admin.site.register(IPAddress)
