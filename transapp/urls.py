from django.urls import re_path, include, path
from .views.agent import AgentView

urlpatterns = [
    path('agent/', include([
        path('', AgentView.as_view(), name='agents'),
        path('<int:agent_id>/', AgentView.as_view(), name='agent')
    ]))
]
