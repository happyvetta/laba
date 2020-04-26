from django.db import models
from account.models import User, EntrantSubject


class PaymentTypes:
    budget = 'budget'
    commerce = 'commerce'
    target = 'target'

    NAMES = {
        budget: 'На бюджетной основе',
        commerce: 'На коммерческой основе',
        target: 'По целевому направлению'
    }

    CHOICES = (
        (budget, NAMES[budget]),
        (commerce, NAMES[commerce]),
        (target, NAMES[target])
    )


class LearningTypes:
    internal = 'internal'
    part_time = 'part_time'
    distance = 'distance '

    NAMES = {
        internal: 'Очная',
        part_time: 'Очно-заочная (вечерняя)',
        distance: 'Заочная'
    }

    CHOICES = (
        (internal, NAMES[internal]),
        (part_time, NAMES[part_time]),
        (distance, NAMES[distance])
    )


class StatementStatuses:
    verification_wait = 'verification_wait'
    verification_success = 'verification_success'
    verification_denied = 'verification_denied'

    NAMES = {
        verification_wait: 'Ожидает подтверждения',
        verification_success: 'Заявление принято',
        verification_denied: 'Заявление отклонено'
    }

    CHOICES = (
        (verification_wait, NAMES[verification_wait]),
        (verification_success, NAMES[verification_success]),
        (verification_denied, NAMES[verification_denied])
    )


class Faculty(models.Model):
    title = models.CharField(verbose_name='Название', max_length=200)

    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'

    def __str__(self):
        return self.title

    def get_specialities(self):
        return Special.objects.filter(faculty=self)

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title
        }


class Subject(models.Model):
    title = models.CharField(verbose_name='Название', max_length=200)

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return self.title

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title
        }


class Special(models.Model):
    title = models.CharField(verbose_name='Название', max_length=200)
    faculty = models.ForeignKey(Faculty, verbose_name='Факультет', on_delete=models.CASCADE)
    number_budget_places = models.PositiveIntegerField(verbose_name='Количество бюджетных мест')
    number_paid_places = models.PositiveIntegerField(verbose_name='Количество платных мест')
    number_target_places = models.PositiveIntegerField(verbose_name='Количество целевых мест')
    cost = models.FloatField(verbose_name='Плата за обучение')
    is_stipend = models.BooleanField(verbose_name='Наличие стипендии')
    subjects = models.ManyToManyField(Subject, verbose_name='Предметы', blank=True)

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальсноти'

    def __str__(self):
        return self.title

    def get_internal_statements(self):
        return Statement.objects.filter(special=self, learning_type=LearningTypes.internal,
                                        status=StatementStatuses.verification_success)

    def get_part_time_statements(self):
        return Statement.objects.filter(special=self, learning_type=LearningTypes.part_time,
                                        status=StatementStatuses.verification_success)

    def get_distance_statements(self):
        return Statement.objects.filter(special=self, learning_type=LearningTypes.distance,
                                        status=StatementStatuses.verification_success)

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'faculty': self.faculty.id,
            'cost': self.cost,
            'number_budget_places': self.number_budget_places,
            'number_paid_places': self.number_paid_places,
            'number_target_places': self.number_target_places
        }

    def to_json_secretary(self):
        return {
            'id': self.id,
            'title': self.title,
            'faculty': {
                'id': self.faculty.id,
                'title': self.faculty.title
            },
            'cost': self.cost,
            'number_budget_places': self.number_budget_places,
            'number_paid_places': self.number_paid_places,
            'number_target_places': self.number_target_places,
            'is_stipend': self.is_stipend
        }


class Statement(models.Model):
    entrant = models.ForeignKey(User, verbose_name='Абитуриент', on_delete=models.CASCADE)
    payment_type = models.CharField(verbose_name='Тип оплаты', choices=PaymentTypes.CHOICES, max_length=200)
    learning_type = models.CharField(verbose_name='Форма обучения', choices=LearningTypes.CHOICES, max_length=200)
    special = models.ForeignKey(Special, verbose_name='Специальность', on_delete=models.CASCADE)
    status = models.CharField(verbose_name='Статус', choices=StatementStatuses.CHOICES,
                              default=StatementStatuses.verification_wait, max_length=200)

    class Meta:
        verbose_name = 'Заявление'
        verbose_name_plural = 'Заявления'

    def __str__(self):
        return '{0}: {1}'.format(self.entrant.full_name, self.special.title)

    def get_payment_type(self):
        return PaymentTypes.NAMES[self.payment_type]

    def get_learning_type(self):
        return LearningTypes.NAMES[self.learning_type]

    def get_status(self):
        return StatementStatuses.NAMES[self.status]

    def get_score(self):
        entrant_subjects = EntrantSubject.objects.filter(entrant=self.entrant, subject__in=self.special.subjects.all())
        return sum([entrant_subject.score for entrant_subject in entrant_subjects])

    def to_json(self):
        return {
            'id': self.id,
            'payment_type': self.get_payment_type(),
            'learning_type': self.get_learning_type(),
            'special': {
                'id': self.special.id,
                'title': self.special.title,
                'faculty': self.special.faculty.id
            },
            'status': self.get_status()
        }

    def to_json_secretary(self):
        return {
            'id': self.id,
            'payment_type': self.get_payment_type(),
            'payment_type_value': self.payment_type,
            'learning_type': self.get_learning_type(),
            'special': {
                'id': self.special.id,
                'title': self.special.title,
                'faculty': self.special.faculty.title,
                'faculty_id': self.special.faculty.id,
            },
            'subjects': [
                {'title': entrant_subject.subject.title,
                 'score': entrant_subject.score} for entrant_subject in EntrantSubject.objects.filter(
                    entrant=self.entrant,
                    subject__in=self.special.subjects.all())],
            'status': self.get_status(),
            'entrant': self.entrant.to_json()
        }
