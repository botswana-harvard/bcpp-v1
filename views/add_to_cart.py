# Import django modules
from django.shortcuts import render_to_response
from django.template import RequestContext
#from bhp_mapping.choices import ICONS
#from bhp_mapping.helpers import session_to_string, prepare_map_points
from bhp_map.classes import site_mapper
from bhp_map.exceptions import MapperError


def add_to_cart(request, **kwargs):
    """Adds a list of identifiers to a shopping cart and returns back to map or checkout cart.

    The list of identifiers of points that are within a polygon.
    """
    template = 'map.html'
    mapper_name = kwargs.get('mapper_name', '')
    if not site_mapper.get_registry(mapper_name):
        raise MapperError('Mapper class \'{0}\' does is not registered.'.format(mapper_name))
    else:
        m = site_mapper.get_registry(mapper_name)()
        additional_item_identifiers = request.GET.get('identifiers', [])
        message = ""
        is_error = False
        item_identifiers = []
        cart_size = 0
        cart = None
        temp_list = []
        if additional_item_identifiers:
            additional_item_identifiers = additional_item_identifiers.split(",")
            for ids in additional_item_identifiers:
                temp_list.append(ids.split(" ")[0])
            additional_item_identifiers = temp_list
        if additional_item_identifiers:
            if 'identifiers' in request.session:
                # add to cart, Merge identifiers in the session with the additional ones, removing duplicates
                request.session['identifiers'] = list(set(request.session['identifiers'] + additional_item_identifiers))
            else:
                request.session['identifiers'] = additional_item_identifiers
            item_identifiers = request.session['identifiers']
            cart_size = len(request.session['identifiers'])
            cart = m.session_to_string(request.session['identifiers']),
        else:
            message = "No items were selected"
            is_error = True
        item_instances = m.get_item_model_cls().objects.filter(**{'{0}__in'.format(m.get_identifier_field_attr()): item_identifiers})
        icon = request.session['icon']
        payload = m.prepare_map_points(item_instances,
            icon,
            request.session['identifiers'],
            'egg-circle'
            )
        return render_to_response(
                template, {
                    'identifier_field_attr': m.get_identifier_field_attr(),
                    'mapper_name': mapper_name,
                    'payload': payload,
                    'identifiers': item_identifiers,
                    'cart': cart,
                    'cart_size': cart_size,
                    'message': message,
                    'option': 'save',
                    'icons': m.get_icons(),
                    'is_error': is_error,
                    'show_map': 0,
                    'item_label': m.get_item_label(),
                },
                context_instance=RequestContext(request)
            )
