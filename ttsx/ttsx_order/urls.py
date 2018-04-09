from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$',views.do_order),

]