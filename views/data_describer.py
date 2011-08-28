from datetime import datetime, date, time
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from bhp_common.utils import os_variables
from bhp_model_selector.classes import ModelSelector
from bhp_model_selector.forms import ModelSelectorForm
from bhp_describer.classes import DataDescriber

@login_required
def data_describer(request, **kwargs):

    section_name = kwargs.get('section_name')
    report_title  = 'Data Describer'
    template = 'data_description.html' 

    if request.method == 'POST':

        form = ModelSelectorForm(request.POST)
    


        if form.is_valid():

            app_label = form.cleaned_data['app_label']
            model_name = form.cleaned_data['model_name']   
            model_selector = ModelSelector(app_label, model_name)             
    
            dd = DataDescriber(form.cleaned_data['app_label'], form.cleaned_data['model_name'])
    
            if dd.model:
                template = 'data_description.html'            
                summary = dd.summarize()
                group = dd.group()
                group_m2m = dd.group_m2m()   
                context = {
                'form': form,
                'app_label': app_label,                                
                'model_name': model_name,
                'app_labels': model_selector.app_labels,                
                'model_names': model_selector.model_names,
                'summary_fields': summary['fields'],
                'group_fields': group['fields'],
                'group_m2m_fields': group_m2m['fields'],                
                'fields': dd.model._meta.fields,
                'section_name': section_name,
                'report_title': report_title,                  
                'cumulative_frequency': 0,
                }
            elif dd.error_type == 'app_label':
                template = 'data_description.html'            
                context = {
                'form': form,
                'error_message': dd.error_message,
                'app_label': app_label,                                
                'model_name': model_name,
                'app_labels': model_selector.app_labels,                
                'model_names': model_selector.model_names,
                'section_name': section_name, 
                #'report_title': report_title,                                  
                }
            elif dd.error_type == 'model_name':
                template = 'data_description.html'            
                context = {
                'form': form,
                'error_message': dd.error_message,
                'app_labels': model_selector.app_labels,                
                'model_names': model_selector.model_names,
                'app_label': app_label,                                
                'model_name': model_name,
                'section_name': section_name, 
                #'report_title': report_title,                                  
                }
            else:
                raise ValueError('Unknown error_type. Got %s' % dd.error_type)
                
            return render_to_response(template, context, context_instance=RequestContext(request))

    else:
    
        form = ModelSelectorForm(request.GET)
        app_label = request.GET.get('app_label', None)
        model_name = request.GET.get('model_name', None)
        model_selector = ModelSelector(app_label, model_name)                     

    return render_to_response(template, { 
        'form': form,
        'table': '',
        'app_label': app_label,                                
        'model_name': model_name,
        'app_labels': model_selector.app_labels,                
        'model_names': model_selector.model_names,
        'summary_fields':{},
        'group_fields': {},                                
        'group_m2m_fields': {},                        
        'section_name': section_name, 
        'report_title': report_title,                          
        'report': ''  ,
        'report_name': kwargs.get('report_name'),         
        }, context_instance=RequestContext(request))

