from django.conf.urls import url
 
from . import view


 
urlpatterns = [
	url(r'^problem_type/$', view.problem_type,name='problem_type'),
    url(r'^$', view.index),
    url(r'^index/$', view.index),
    url(r'^submit_data/(?P<problem_type>\d+)/$', view.submit_data,name='submit_data'),
    url(r'^save_train_data/$', view.save_train_data,name='save_train_data'),
    url(r'^save_id_target/$', view.save_id_target,name='save_id_target'),
    url(r'^submit_label/$', view.submit_label,name='submit_label'),
    url(r'^submit_type/$', view.submit_type,name='submit_type'),
    url(r'^save_feature_type/$', view.save_feature_type,name='save_feature_type'),

    # ajax
    url(r'^feature/list/(?P<file>\w+)/$', view.feature_list, name='feature_list'),
]

