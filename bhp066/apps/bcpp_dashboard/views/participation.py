from django.contrib.auth.decorators import login_required

from apps.bcpp_dashboard.views import household_dashboard
from apps.bcpp_household_member.forms import ParticipationForm
from apps.bcpp_household_member.models import HouseholdMember


@login_required
def participation(request, **kwargs):
    """Updates the member status and redirects to the household dashboard."""
    if request.method == 'POST':
        form = ParticipationForm(request.POST)
        if form.is_valid():
            household_member = HouseholdMember.objects.get(id=form.cleaned_data.get('household_member'))
            if form.cleaned_data.get('status'):
                household_member.member_status = form.cleaned_data.get('status')
                # use update_fields=['member_status'] and trap in household
                # member save. Probably should not change this unless you
                # know what you're doing.
                household_member.save(update_fields=['member_status'])
            dashboard_type = form.cleaned_data.get('dashboard_type')
            dashboard_model = form.cleaned_data.get('dashboard_model')
            dashboard_id = form.cleaned_data.get('dashboard_id')
    else:
        # TODO: what happens if this gets passed? it fails!!
        dashboard_type = None
        dashboard_id = None
        dashboard_model = None

    return household_dashboard(request,
                               dashboard_type=dashboard_type,
                               dashboard_model=dashboard_model,
                               dashboard_id=dashboard_id,
                               )
