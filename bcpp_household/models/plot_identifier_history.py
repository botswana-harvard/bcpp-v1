from edc_identifier.models import IdentifierModelMixin
from edc_base.model.models import BaseUuidModel


class PlotIdentifierHistory(IdentifierModelMixin, BaseUuidModel):
    """A system model to track allocated plot identifiers."""

    class Meta:
        app_label = "bcpp_household"
