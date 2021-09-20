import json

from django.core.exceptions import FieldError
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views import View

from transapp.models.agent import Agent


class AgentView(View):
    model = Agent

    def get(self, request, agent_id=''):
        email_filter = request.GET.get('email', '')
        sort_by_field = request.GET.get('sort_by', 'last_name')
        if agent_id == '':
            try:
                all_agents = self.model.objects.order_by(sort_by_field)
            except FieldError:
                return HttpResponseBadRequest(json.dumps(
                    {'error': 'incorrect value for sort_by parameter'}
                ), content_type='application/json')

            if email_filter:
                all_agents = all_agents.filter(email__contains=email_filter)
            return JsonResponse(list(all_agents.values()), safe=False)
        else:
            agent = list(self.model.objects.filter(id=agent_id).values())
            return JsonResponse(agent, safe=False) if len(agent) > 0 else HttpResponseNotFound()

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            agent = self.model.objects.create(
                first_name=data['first_name'], last_name=data['last_name'], email=data['email']
            )
            return JsonResponse({'id': agent.id}, status=201)
        except KeyError as e:
            content = json.dumps({'error': e.__cause__}) if e.__cause__ else ''
            return HttpResponseBadRequest(content, content_type='application/json')
        except IntegrityError:
            return HttpResponseBadRequest(json.dumps({
                'error': 'email address specified already exists'
            }), content_type='application/json')

    def put(self, request, agent_id):
        data = json.loads(request.body.decode('utf-8'))
        try:
            self.model.objects.create(id=agent_id, first_name=data['first_name'], last_name=data['last_name'],
                                      email=data['email'])
            return HttpResponse()
        except KeyError as e:
            content = json.dumps({'error': e.__cause__}) if e.__cause__ else ''
            return HttpResponseBadRequest(content, content_type='application/json')
        except IntegrityError:
            return HttpResponseBadRequest(json.dumps({
                'error': 'email address specified already exists'
            }), content_type='application/json')

    def patch(self, request, agent_id):
        data = json.loads(request.body.decode('utf-8'))
        try:
            agent = get_object_or_404(self.model, id=agent_id)
            fields = ['first_name', 'last_name', 'email']
            for field in fields:
                if field in data.keys():
                    setattr(agent, field, data[field])

            agent.save()
            return HttpResponse()
        except IntegrityError:
            return HttpResponseBadRequest(json.dumps({
                'error': 'email address specified already exists'
            }), content_type='application/json')

    def delete(self, request, agent_id):
        get_object_or_404(self.model, id=agent_id).delete()
        return HttpResponse()
