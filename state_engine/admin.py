from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Workflow, State, Transition, Entity, ActionLog, ContactMessage

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Workflow)
admin.site.register(State)
admin.site.register(Transition)
admin.site.register(Entity)
admin.site.register(ActionLog)
admin.site.register(ContactMessage)