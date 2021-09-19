from django.urls import include, path
from .views.agent import AgentView
from .views.transaction import TransactionView

urlpatterns = [
    path('agent/', include([
        path('', AgentView.as_view(), name='agents'),
        path('<int:agent_id>/', include([
            path('', AgentView.as_view(), name='agent'),
            path('transactions', TransactionView.as_view(), name='agent_transactions')
        ]))
    ])),
    path('transaction/', include([
        path('', TransactionView.as_view(), name='agents'),
        path('<int:transaction_id>/', TransactionView.as_view(), name='agent')
    ]))
]
