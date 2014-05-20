from datetime import datetime
import factory
from edc.base.model.tests.factories import BaseUuidModelFactory
from ...models import AliquotProfile
from .aliquot_type_factory import AliquotTypeFactory


class ProfileFactory(BaseUuidModelFactory):
    FACTORY_FOR = AliquotProfile

    aliquot_type = factory.SubFactory(AliquotTypeFactory)
    name = factory.Sequence(lambda n: 'name{0}'.format(n))