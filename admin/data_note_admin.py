from django.contrib import admin
from bhp_data_manager.models import DataNote
from base_comment_admin import BaseCommentAdmin


class DataNoteAdmin(BaseCommentAdmin):
        pass
admin.site.register(DataNote, DataNoteAdmin)
