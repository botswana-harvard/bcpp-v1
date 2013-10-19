from edc.dashboard.search.classes import BaseSearchByWord

from ..models import Household
from .base_search_by_mixin import BaseSearchByMixin


class HouseholdSearchByWord(BaseSearchByMixin, BaseSearchByWord):

    name = 'word'
    search_model = Household
#     search_model_attrname = 'household_identifier'
    order_by = 'household_identifier'
    template = 'search_household_result_include.html'
