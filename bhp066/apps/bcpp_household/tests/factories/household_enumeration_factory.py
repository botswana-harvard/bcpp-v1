import factory
from datetime import datetime
from edc.base.model.tests.factories import BaseUuidModelFactory
from ...models import HouseholdEnumerationRefusal
from .plot_factory import PlotFactory


class HouseholdEnumerationRefusalFactory(BaseUuidModelFactory):
    FACTORY_FOR = HouseholdEnumerationRefusal

    household = factory.SubFactory(PlotFactory)
    report_datetime = datetime.now()
    reason = 'Does not have time'