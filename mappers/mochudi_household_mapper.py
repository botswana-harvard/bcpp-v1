from bhp_map.classes import site_mappers
from base_household_mapper import BaseHouseholdMapper
from choices import MOCHUDI_SECTIONS, MOCHUDI_SUB_SECTIONS, MOCHUDI_LANDMARKS


class MochudiHouseholdMapper(BaseHouseholdMapper):

    map_area = 'mochudi'

    regions = MOCHUDI_SECTIONS
    sections = MOCHUDI_SUB_SECTIONS

    landmarks = MOCHUDI_LANDMARKS

    gps_center_lat = -24.390254
    gps_center_lon = 26.158733
    radius = 9.5
    location_boundary = (
        [-24.390254188712102, 26.131668090820312], [-24.392442947551878, 26.111068725585938], [-24.390879552249302, 26.097335815429688],
        [-24.37180457231936, 26.086349487304688], [-24.36304788022171, 26.07330322265625], [-24.36744604364978, 26.06399081186771],
        [-24.375178129210646, 26.06408408763218], [-24.376964481997824, 26.071758270263672], [-24.4048793376205, 26.079332088601973],
        [-24.410733235173616, 26.094202995300293], [-24.410733235173616, 26.116132736206055], [-24.41722017934173, 26.1295223236084],
        [-24.42761985978531, 26.13763808985493], [-24.429646044835177, 26.155014038085938], [-24.422685193983785, 26.162831492273654],
        [-24.40416779566267, 26.18539810180664], [-24.402682708433254, 26.192951202392578], [-24.391739422059494, 26.194581985473633],
        [-24.381264245888335, 26.184968948364258], [-24.363641549074845, 26.20018543518802], [-24.35898206714331, 26.197586059570312],
        [-24.354056003216844, 26.182308197021484], [-24.34714566073864, 26.161934705225462], [-24.349755314471462, 26.13776206970215],
        [-24.36573872359394, 26.122189151045745], [-24.390254188712102, 26.131668090820312]
    )

site_mappers.register(MochudiHouseholdMapper)
