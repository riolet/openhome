from django.conf.urls import url

from . import views

app_name = 'property'

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^results/$', views.search_results, name='search results'),
    url(r'^search/$', views.search, name='search'),
    url(r'^listing/new/$', views.new, name='new'),
    url(r'^listing/(?P<property_id>\w{11,20})/$', views.details, name='details'),
    url(r'^listing/(?P<property_id>\w{11,20})/edit/$', views.edit, name='edit'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^user/(?P<user_id>\d+)/$', views.user, name='account'),
]