from django.contrib.auth import logout, login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from account.models import User, EntrantSubject
from account.serializers.account import UserSerializer
from university.models import Statement, Faculty, Special, Subject
from university.serializers.entrant_subject import EntrantSubjectSerializer
from university.serializers.statement import StatementSerializer
from utils.utils import CsrfExemptSessionAuthentication
from utils.email import EmailManager


class Login(APIView):
    template_name = 'login.html'
    authentication_classes = (BasicAuthentication,)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request):
        lg = request.data.get('login', '')
        password = request.data.get('password', '')
        try:
            user = User.objects.get(email__iexact=lg)
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


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/login/')


class RegistrationView(View):
    template_name = 'registration.html'

    def get(self, request, *args, **kwargs):
        subjects = Subject.objects.all()
        return render(request, self.template_name, {'subjects': [subject.to_json() for subject in subjects]})


@method_decorator(csrf_exempt, name='dispatch')
class RegistrationCreateAccount(APIView):
    authentication_classes = (BasicAuthentication,)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            account = serializer.save()
            password = request.data['password']
            account.set_password(password)
            account.is_active = True
            account.save()

            entrant_subjects = request.data['entrantSubjects']
            for subject in entrant_subjects:
                EntrantSubject.objects.create(entrant=account, score=subject['score'],
                                              subject=Subject.objects.filter(id=int(subject['subject'])).first())

            return Response({'success': True, 'data': serializer.data}, status=201)
        return Response({'success': False, 'errors': serializer.errors}, status=200)


class Home(View):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse('lc-secretary-statements'))
        return redirect(reverse('lc-data'))


class LCData(View):
    template_name = 'lc-data.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse('lc-secretary'))
        subjects = Subject.objects.all()
        entrant_subjects = EntrantSubject.objects.filter(entrant=request.user)
        return render(request, self.template_name, {
            'user': self.request.user,
            'subjects': [subject.to_json() for subject in subjects],
            'entrant_subjects': [entrant_subject.to_json() for entrant_subject in entrant_subjects]
        })


class LCStatements(View):
    template_name = 'lc-statements.html'

    def get(self, request, *args, **kwargs):
        statements = Statement.objects.filter(entrant=self.request.user)
        faculties = Faculty.objects.all()
        specialties = Special.objects.all()
        return render(request, self.template_name, {
            'user': self.request.user,
            'statements': [statement.to_json() for statement in statements],
            'faculties': [faculty.to_json() for faculty in faculties],
            'specialties': [special.to_json() for special in specialties]
        })


class SaveStatementsView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    parser_classes = (JSONParser,)
    serializer_class = StatementSerializer

    def post(self, request, *args, **kwargs):
        statements = request.data['statements']
        statement_ids = []
        for statement in statements:
            if statement['id']:
                statement_serializer = self.serializer_class(data=statement,
                                                             instance=Statement.objects.get(id=int(statement['id'])))
                if statement_serializer.is_valid():
                    statement = statement_serializer.save()
                    statement_ids.append(statement.id)
            else:
                statement_serializer = self.serializer_class(data=statement)
                if statement_serializer.is_valid():
                    statement = statement_serializer.save()
                    statement_ids.append(statement.id)
            print(statement_serializer.errors)
        Statement.objects.exclude(id__in=statement_ids).delete()

        return JsonResponse({'success': True})


class SaveSubjectsInfoView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    parser_classes = (JSONParser,)
    serializer_class = EntrantSubjectSerializer

    def post(self, request, *args, **kwargs):
        entrant_subjects = request.data['entrant_subjects']
        entrant_subject_ids = []
        for entrant_subject in entrant_subjects:
            if entrant_subject['id']:
                entrant_subject_serializer = self.serializer_class(
                    data=entrant_subject,
                    instance=EntrantSubject.objects.get(id=int(entrant_subject['id'])))
                if entrant_subject_serializer.is_valid():
                    entrant_subjects = entrant_subject_serializer.save()
                    entrant_subject_ids.append(entrant_subjects.id)
            else:
                entrant_subject_serializer = self.serializer_class(data=entrant_subject)
                if entrant_subject_serializer.is_valid():
                    entrant_subjects = entrant_subject_serializer.save()
                    entrant_subject_ids.append(entrant_subjects.id)

        EntrantSubject.objects.exclude(id__in=entrant_subject_ids).delete()
        return JsonResponse({'success': True})

