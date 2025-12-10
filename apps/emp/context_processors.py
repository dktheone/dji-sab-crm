# apps/leads/context_processors.py
# from django.http import HttpRequest

# def active_menu(request: HttpRequest) -> dict:
#     """
#     Context processor to determine active sidebar menu section.
#     Returns {'active_menu': 'leads' | 'emp' | None} based on view_name.
#     """
#     view_name = request.resolver_match.view_name if request.resolver_match else ''
#     if view_name.startswith('leads:'):
#         return {'active_menu': 'leads'}
#     elif view_name.startswith('emp:'):
#         return {'active_menu': 'emp'}
#     return {'active_menu': None}



# apps/emp/context_processors.py
from typing import List
from django.http import HttpRequest

def active_menus(request: HttpRequest) -> dict:
    """
    Context processor for multi-level sidebar expansion.
    Returns {'active_menus': ['emp', 'salary']} based on view_name hierarchy.
    Supports fixed levels: 'emp' (HRMS), 'salary' (sub), 'leads'.
    Extend mapping as needed for deeper nesting.
    """
    view_name = getattr(request.resolver_match, 'view_name', '') if request.resolver_match else ''
    
    # Mapping: view_name prefix → active menu path (list for levels)
    menu_hierarchy = {
        'emp:employee_dash': ['emp'],
        'emp:employee_list': ['emp'],
        'emp:create_employee_user': ['emp'],
        'emp:salary_master_list': ['emp', 'salary'],
        'emp:adjustments_list': ['emp', 'salary'],
        'emp:adjustments_page': ['emp', 'salary'],
        'emp:salary_preparation': ['emp', 'salary'],
        # LEADS
        # 'leads:lead_list': ['leads'],
        # 'leads:lead_form_add': ['leads'],
        # 'leads:lead_form_edit': ['leads'],
        # 'leads:lead_follow_ups': ['leads'],
        # 'leads:convert_to_site': ['leads'],
        # 'leads:employee_activity': ['leads'],
        # 'leads:conversion_logs': ['leads'],
        # Add more as your menu grows
    }
    
    # Find matching path
    active_menus: List[str] = []
    for key, path in menu_hierarchy.items():
        if view_name.startswith(key.split(':')[0] + ':') or view_name == key:
            active_menus = path
            break
    
    # Fallback to path-based if view_name missing
    if not active_menus and request.path.startswith('/emp/'):
        active_menus = ['emp'] if not any(s in request.path for s in ['salary', 'adjustments']) else ['emp', 'salary']
    elif request.path.startswith('/leads/'):
        active_menus = ['leads']
    
    return {'active_menus': active_menus}


def menu_context(request):
    return {'view_name': request.resolver_match.view_name if request.resolver_match else ''}