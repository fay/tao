from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:



handler404 = 'nankin.views.page_not_found'

urlpatterns = patterns('taolink.views',
    # Example:
    # (r'^mindgames/', include('mindgames.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    
    # Core App
    (r'^$', 'index'),
    (r'^add/url/1/$','add_url_1'),
    (r'^add/url/$','add_url'),
    (r'^about/', 'about'),
    (r'^home/(?P<service_type>[a-zA-Z0-9_-]*)/$', 'home'),
    (r'^accounts/login/', 'login'),
    (r'^accounts/logout/', 'logout'),
    (r'^accounts/register/', 'register'),
#(r'^wantown/upload/', 'upload'),
)
