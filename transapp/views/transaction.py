import json

from django.core import serializers
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.utils.dateparse import parse_datetime

from django.views.decorators.csrf import csrf_exempt

from transapp.models.agent import Agent
from transapp.models.transaction import Transaction


# TODO remove decorator
@method_decorator(csrf_exempt, name='dispatch')
class TransactionView(View):
    model = Transaction

    def get(self, request, transaction_id=''):
        transaction_type = request.GET.get('type', 'all')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        sort_by = request.GET.get('sort_by', 'date')
        if transaction_id == '':
            try:
                items = self.model.objects.order_by(sort_by)
                if transaction_type == 'income':
                    items = items.filter(amount__gt=0)
                elif transaction_type == 'outcome':
                    items = items.filter(amount__lt=0)
                if start_date:
                    items = items.filter(date__gte=parse_datetime(start_date))
                if end_date:
                    items = items.filter(date__gte=parse_datetime(end_date))

                return HttpResponse(serializers.serialize("json", items), content_type="application/json")
            except (ValueError, AttributeError):
                return HttpResponseBadRequest()
        else:
            item = get_object_or_404(self.model, id=transaction_id)
            return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            agent = get_object_or_404(Agent, id=data['agent_id'])
            item = self.model(agent_id=agent, amount=data['amount'], date=data['date'])
            item.save()
            response = JsonResponse({'id': item.id})
            response.status_code = 201
            return response
        except (KeyError, IntegrityError):
            return HttpResponseBadRequest()

    def put(self, request, transaction_id):
        data = json.loads(request.body.decode('utf-8'))
        try:
            self.model(id=transaction_id, agent_id=data['agent_id'],
                       amount=data['amount'], date=data['date']) \
                .save()
            return HttpResponse()
        except (KeyError, IntegrityError):
            return HttpResponseBadRequest()

    def patch(self, request, transaction_id):
        data = json.loads(request.body.decode('utf-8'))
        try:
            item = get_object_or_404(self.model, id=transaction_id)
            fields = ['amount', 'date']
            for field in fields:
                if field in data.keys():
                    setattr(item, field, data[field])

            if 'agent_id' in data:
                item.agent_id = Agent.objects.get(id=data['agent_id'])

            item.save()
            return HttpResponse()
        except (KeyError, IntegrityError, self.model.DoesNotExist):
            return HttpResponseBadRequest()

    def delete(self, request, transaction_id):
        try:
            get_object_or_404(self.model, id=transaction_id).delete()
            return HttpResponse()
        except (KeyError, IntegrityError, self.model.DoesNotExist):
            return HttpResponseBadRequest()
