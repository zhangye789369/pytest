from django.conf.urls import url
import views

urlpatterns = [
    url(r'^add/$', views.add),
    url(r'^count/$', views.count),
    url('^$', views.index),
    url('^edit/$', views.edit),
    url('^del/$', views.delete),
    url('^order/$', views.order),
]