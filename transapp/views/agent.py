import json

from django.core import serializers
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from transapp.models.agent import Agent


@method_decorator(csrf_exempt, name='dispatch')
class AgentView(View):
    model = Agent

    def get(self, request, agent_id=''):
        email_filter = request.GET.get('email', '')
        sort_by_field = request.GET.get('sort_by', 'last_name')
        if agent_id == '':
            try:
                all_agents = sorted(self.model.objects.filter(email__contains=email_filter),
                                    key=lambda a: getattr(a, sort_by_field))
            except AttributeError:
                return HttpResponseBadRequest()

            return HttpResponse(serializers.serialize("json", all_agents), content_type="application/json")
        else:
            try:
                agent = serializers.serialize("json", [self.model.objects.get(pk=agent_id)])
                return HttpResponse(agent, content_type="application/json")
            except self.model.DoesNotExist:
                return Http404()

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            agent = self.model(first_name=data['first_name'], last_name=data['last_name'], email=data['email'])
            agent.save()
            response = JsonResponse({'id': agent.id})
            response.status_code = 201
            return response
        except (KeyError, IntegrityError):
            return HttpResponseBadRequest()

    def patch(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            agent = self.model.objects.get(data['id'])
            fields = ['first_name', 'last_name', 'email']
            for field in fields:
                if field in data.keys():
                    setattr(agent, field, data['field'])

            agent.save()
            response = JsonResponse()
            response.status_code = 200
            return response
        except (KeyError, IntegrityError, self.model.DoesNotExist):
            return HttpResponseBadRequest()

    def put(self, request):
        self.patch(request)

    def delete(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            self.model.objects.get(data['id']).delete()
        except (KeyError, IntegrityError, self.model.DoesNotExist):
            return HttpResponseBadRequest()
