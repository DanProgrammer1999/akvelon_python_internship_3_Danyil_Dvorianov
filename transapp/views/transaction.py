import json

from django.core import serializers
from django.db import IntegrityError
from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.views import View

from transapp.models.agent import Agent
from transapp.models.transaction import Transaction


class TransactionView(View):
    model = Transaction

    def get(self, request, transaction_id='', agent_id=''):
        sort_by = request.GET.get('sort_by', 'date')
        group_by = request.GET.get('group_by', '')
        agent_id = request.GET.get('agent_id', agent_id)

        if transaction_id == '':
            try:
                items = self.apply_parameters(request, self.model.objects)
                if agent_id:
                    items = items.filter(agent_id=agent_id)

                if group_by:
                    if not agent_id:
                        return HttpResponseBadRequest('agent_id is not specified for aggregate request')
                    return self.group_transactions(items, group_by)
                else:
                    items = items.order_by(sort_by)
                    return HttpResponse(serializers.serialize("json", items), content_type="application/json")
            except (ValueError, AttributeError) as e:
                return HttpResponseBadRequest(e.__cause__)
        else:
            item = get_object_or_404(self.model, id=transaction_id)
            return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")

    @staticmethod
    def group_transactions(items, group_by):
        if group_by == 'day':
            items = items.annotate(day=TruncDate('date'))
        elif group_by == 'month':
            items = items.annotate(month=TruncMonth('date'))
        else:
            return HttpResponseBadRequest(f'Unknown group_by value: {group_by}. Choose either \'day\' or \'month\'')

        items = items.values(group_by).annotate(total=Sum('amount')).values(group_by, 'total').order_by(group_by)

        return JsonResponse(list(items), safe=False)

    @staticmethod
    def apply_parameters(request, items):
        transaction_type = request.GET.get('type', 'all')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        if transaction_type == 'income':
            items = items.filter(amount__gt=0)
        elif transaction_type == 'outcome':
            items = items.filter(amount__lt=0)
        if start_date:
            items = items.filter(date__gte=parse_datetime(start_date))
        if end_date:
            items = items.filter(date__gte=parse_datetime(end_date))

        return items

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            agent = get_object_or_404(Agent, id=data['agent_id'])
            item = self.model.objects.create(agent_id=agent, amount=data['amount'], date=data['date'])
            return JsonResponse({'id': item.id}, status=201)
        except (KeyError, IntegrityError):
            return HttpResponseBadRequest()

    def put(self, request, transaction_id):
        data = json.loads(request.body.decode('utf-8'))
        try:
            self.model.objects.create(id=transaction_id, agent_id=data['agent_id'],
                                      amount=data['amount'], date=data['date'])
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
        get_object_or_404(self.model, id=transaction_id).delete()
        return HttpResponse()
