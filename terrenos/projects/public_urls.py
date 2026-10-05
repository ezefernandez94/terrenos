from django.urls import path
from . import public_views

app_name = 'public_projects'

urlpatterns = [
    path("<slug:slug>/", public_views.detail, name='detail'),
    path("<slug:slug>/mapa.json", public_views.map_data, name='map_data'),
    path("<slug:slug>/plano.svg", public_views.plan_svg, name='plan_svg'),
]
