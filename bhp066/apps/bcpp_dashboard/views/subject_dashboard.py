from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from apps.bcpp_dashboard.classes import SubjectDashboard
from apps.bcpp_subject.models import SubjectConsent


@login_required
def subject_dashboard(request, **kwargs):
    dashboard = SubjectDashboard(
        dashboard_type=kwargs.get('dashboard_type'),
        dashboard_id=kwargs.get('dashboard_id'),
        dashboard_model=kwargs.get('dashboard_model'),
        registered_subject=kwargs.get('registered_subject'),
        show=kwargs.get('show'),
        dashboard_type_list=['subject'],
        dashboard_models={'subject_consent': SubjectConsent},
        app_label='bcpp_subject',
        )
    return render_to_response(
        'subject_dashboard.html',
        dashboard.context,
        context_instance=RequestContext(request))
