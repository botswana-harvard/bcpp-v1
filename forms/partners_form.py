from base_htc_model_form import BaseHtcModelForm
from bcpp_subject_htc.models import HtcRecentPartner, HtcSecondPartner, HtcThirdPartner


class HtcRecentPartnerForm (BaseHtcModelForm):

    class Meta:
        model = HtcRecentPartner


class HtcSecondPartnerForm (BaseHtcModelForm):

    class Meta:
        model = HtcSecondPartner


class HtcThirdPartnerForm (BaseHtcModelForm):

    class Meta:
        model = HtcThirdPartner
