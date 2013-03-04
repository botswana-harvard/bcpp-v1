from django.contrib import admin
from bhp_base_model.classes import BaseModelAdmin
from bhp_consent.models import TestSubjectUuidModel
from bhp_consent.forms import TestSubjectUuidModelForm


class TestSubjectUuidModelAdmin(BaseModelAdmin):
    form = TestSubjectUuidModelForm
admin.site.register(TestSubjectUuidModel, TestSubjectUuidModelAdmin)
