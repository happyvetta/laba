import json
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.urls import reverse
from django.views import View
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from account.models import User
from university.models import Faculty, Statement, Special
from university.serializers.faculty import FacultySerializer
from university.serializers.special import SpecialSerializer
from university.serializers.statement import ChangeStatementStatusSerializer
from utils.utils import CsrfExemptSessionAuthentication


class LoginSecretary(APIView):
    template_name = 'login-secretary.html'
    authentication_classes = (BasicAuthentication,)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request):
        lg = request.data.get('login', '')
        password = request.data.get('password', '')
        try:
            user = User.objects.get(email__iexact=lg, is_superuser=True)
            if user.check_password(password):
                login(request, user)
                return JsonResponse({'success': True})
        except User.DoesNotExist:
            pass

        return JsonResponse({
            'non_field_error': 'Невозможно войти с предоставленными учетными данными',
            'errors': {
                'login': ['Поле заполнено не верно'],
                'password': ['Поле заполнено не верно']
            }
        }, status=400)


class LCSecretaryFaculties(View):
    template_name = 'lc-secretary-faculties.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            faculties = Faculty.objects.all()
            return render(request, self.template_name, {
                'faculties': [faculty.to_json() for faculty in faculties]
            })
        raise HttpResponseForbidden


class LCSecretarySpecialities(View):
    template_name = 'lc-secretary-specialities.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            faculties = Faculty.objects.all()
            specialities = Special.objects.all()
            return render(request, self.template_name, {
                'faculties': [faculty.to_json() for faculty in faculties],
                'specialities': json.dumps(SpecialSerializer(instance=specialities, many=True).data)
            })
        raise HttpResponseForbidden


class LCSecretaryStatements(View):
    template_name = 'lc-secretary-statements.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            statements = Statement.objects.all()
            faculties = Faculty.objects.all()
            specialities = Special.objects.all()
            return render(request, self.template_name, {
                'statements': [statement.to_json_secretary() for statement in statements],
                'faculties': [faculty.to_json() for faculty in faculties],
                'specialities': [special.to_json() for special in specialities]
            })
        raise HttpResponseForbidden


class SaveFacultiesSecretaryView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    parser_classes = (JSONParser,)
    serializer_class = FacultySerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            faculties = request.data['faculties']
            faculty_ids = []
            for faculty in faculties:
                if faculty['id']:
                    faculty_serializer = self.serializer_class(
                        data=faculty,
                        instance=Faculty.objects.get(id=int(faculty['id'])))
                    if faculty_serializer.is_valid():
                        faculty = faculty_serializer.save()
                        faculty_ids.append(faculty.id)
                else:
                    faculty_serializer = self.serializer_class(data=faculty)
                    if faculty_serializer.is_valid():
                        faculty = faculty_serializer.save()
                        faculty_ids.append(faculty.id)

            Faculty.objects.exclude(id__in=faculty_ids).delete()
            return JsonResponse({'success': True})
        raise HttpResponseForbidden


class SaveSpecialitiesSecretaryView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    parser_classes = (JSONParser,)
    serializer_class = SpecialSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            specialities = request.data['specialities']
            special_ids = []
            for special in specialities:
                if special['id']:
                    special_serializer = self.serializer_class(
                        data=special,
                        instance=Special.objects.get(id=int(special['id'])))
                    if special_serializer.is_valid():
                        special = special_serializer.save()
                        special_ids.append(special.id)
                else:
                    special_serializer = self.serializer_class(data=special)
                    if special_serializer.is_valid():
                        special = special_serializer.save()
                        special_ids.append(special.id)
            Special.objects.exclude(id__in=special_ids).delete()
            return JsonResponse({'success': True})
        raise HttpResponseForbidden


class SaveStatementsSecretaryView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    parser_classes = (JSONParser,)
    serializer_class = ChangeStatementStatusSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            statements = request.data['statements']
            for statement in statements:
                if statement['id']:
                    statement_serializer = self.serializer_class(
                        data=statement,
                        instance=Statement.objects.get(id=int(statement['id'])))
                    if statement_serializer.is_valid():
                        statement_serializer.save()
            return JsonResponse({'success': True})
        raise HttpResponseForbidden


class MakeReportView(View):
    template_name = 'report/entrant_list.html'

    def get(self, request):
        faculties = Faculty.objects.all()
        return render(request, self.template_name, {'faculties': faculties})
