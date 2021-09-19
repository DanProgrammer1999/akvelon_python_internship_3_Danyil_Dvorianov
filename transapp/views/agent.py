import json

from django.core import serializers
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from transapp.models.agent import Agent


# TODO remove decorator
@method_decorator(csrf_exempt, name='dispatch')
class AgentView(View):
    model = Agent

    def get(self, request, agent_id=''):
        email_filter = request.GET.get('email', '')
        sort_by_field = request.GET.get('sort_by', 'last_name')
        if agent_id == '':
            try:
                all_agents = self.model.objects.order_by(sort_by_field)
                if email_filter:
                    all_agents = all_agents.filter(email__contains=email_filter)
            except AttributeError:
                return HttpResponseBadRequest()

            return HttpResponse(serializers.serialize("json", all_agents), content_type="application/json")
        else:
            agent = get_object_or_404(self.model, id=agent_id)
            return HttpResponse(serializers.serialize("json", [agent]), content_type="application/json")

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            agent = self.model.objects.create(first_name=data['first_name'], last_name=data['last_name'],
                                              email=data['email'])
            return JsonResponse({'id': agent.id}, status=201)
        except (KeyError, IntegrityError):
            return HttpResponseBadRequest()

    def put(self, request, agent_id):
        data = json.loads(request.body.decode('utf-8'))
        try:
            self.model.objects.create(id=agent_id, first_name=data['first_name'], last_name=data['last_name'],
                                      email=data['email'])
            return HttpResponse()
        except (KeyError, IntegrityError):
            return HttpResponseBadRequest()

    def patch(self, request, agent_id):
        data = json.loads(request.body.decode('utf-8'))
        try:
            agent = self.model.objects.get(id=agent_id)
            fields = ['first_name', 'last_name', 'email']
            for field in fields:
                if field in data.keys():
                    setattr(agent, field, data[field])

            agent.save()
            return HttpResponse()
        except (KeyError, IntegrityError, self.model.DoesNotExist):
            return HttpResponseBadRequest()

    def delete(self, request, agent_id):
        get_object_or_404(self.model, id=agent_id).delete()
        return HttpResponse()
