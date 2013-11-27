from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'zhpBackend.views.home', name='home'),
    # url(r'^zhpBackend/', include('zhpBackend.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
    # API URL
    url(r'^webapi/', include('webapi.urls'), name='webapi'),
    url(r'^docs$', include('rest_framework_docs.urls'), name='docs'),
)
