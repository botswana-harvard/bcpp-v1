from datetime import datetime
from bhp_site_edc import edc as admin


class BaseStackedInline (admin.StackedInline):

    """Forces username to be saved on add and change"""

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user_created = request.user.username
        if change:
            obj.user_modified = request.user.username
            obj.modified = datetime.today()

        super(BaseStackedInline, self).save_model(request, obj, form, change)
