from django.urls import path
from photos.views import index

app_name = 'photos'

urlpatterns = [
    path('index/', index.IndexView.as_view(), name='index'),
    path('<int:num_album>/selecao/', index.selecao, name='selecao'),
    path('<int:slideshow_codigo>/configuracao/', index.configuracao, name='configuracao'),
    path('<int:slideshow_codigo>/slideshow/', index.slideshow, name='slideshow')
]

