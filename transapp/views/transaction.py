import json

from django.core import serializers
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from transapp.models.transaction import Transaction


# TODO remove decorator
@method_decorator(csrf_exempt, name='dispatch')
class AgentView(View):
    model = Transaction

    def get(self, request, transaction_id=''):
        if transaction_id == '':
            try:
                all_items = self.model.objects.all()
            except AttributeError:
                return HttpResponseBadRequest()

            return HttpResponse(serializers.serialize("json", all_items), content_type="application/json")
        else:
            try:
                agent = serializers.serialize("json", [self.model.objects.get(pk=transaction_id)])
                return HttpResponse(agent, content_type="application/json")
            except self.model.DoesNotExist:
                return Http404()

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            item = self.model(agent_id=data['agent_id'], amount=data['amount'], date=data['date'])
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
            agent = self.model.objects.get(id=transaction_id)
            fields = ['agent_id', 'amount', 'date']
            for field in fields:
                if field in data.keys():
                    setattr(agent, field, data[field])

            agent.save()
            return HttpResponse()
        except (KeyError, IntegrityError, self.model.DoesNotExist):
            return HttpResponseBadRequest()

    def delete(self, request, transaction_id):
        try:
            res = self.model.objects.filter(id=transaction_id).delete()
            print(res)
            return HttpResponse()
        except (KeyError, IntegrityError, self.model.DoesNotExist):
            return HttpResponseBadRequest()
