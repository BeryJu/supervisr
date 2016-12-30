from django.contrib import admin
from supervisr.models import *
# Register your models here.
admin.site.register(AccountConfirmation)
admin.site.register(Notification)
admin.site.register(UserProductRelationship)
admin.site.register(Product)
admin.site.register(ServerProduct)
admin.site.register(ServerCPU)
admin.site.register(ServerDrive)
admin.site.register(ServerNIC)
admin.site.register(IPAddress)
admin.site.register(HostedApplicationProduct)

