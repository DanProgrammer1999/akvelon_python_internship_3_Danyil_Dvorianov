from django.urls import re_path, include, path
from .views.agent import AgentView
from .views.transaction import TransactionView

urlpatterns = [
    path('agent/', include([
        path('', AgentView.as_view(), name='agents'),
        path('<int:agent_id>/', AgentView.as_view(), name='agent')
    ])),
    path('transaction/', include([
        path('', TransactionView.as_view(), name='agents'),
        path('<int:transaction_id>/', TransactionView.as_view(), name='agent')
    ]))
]
