from django.urls import path
from . import view

app_name = 'photos'

urlpatterns = [
    
    path('index/', view.IndexView.as_view(), name='index'),
    path('<int:num_album>/selecao/', view.selecao, name='selecao'),
    path('<int:slideshow_codigo>/configuracao/', view.configuracao, name='configuracao'),
    path('<int:slideshow_codigo>/slideshow/', view.slideshow, name='slideshow'),
    path('<int:slideshow_codigo>/slideshow/check_progress', view.check_progress, name='check_progress')
]

