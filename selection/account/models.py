from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class MedalTypes:
    gold = 'gold'
    silver = 'silver'
    without_medal = 'without_medal'

    NAMES = {
        gold: 'Золотая',
        silver: 'Серебряная',
        without_medal: 'Нет медали'
    }

    CHOICES = (
        (gold, NAMES[gold]),
        (silver, NAMES[silver]),
        (without_medal, NAMES[without_medal])
    )


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwars):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email, password=password
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField(verbose_name='Электронная почта', blank=False, unique=True)
    full_name = models.CharField(verbose_name='Полное имя', max_length=200)
    passport = models.CharField(verbose_name='Паспортные данные', max_length=200)
    school = models.CharField(verbose_name='Школа', max_length=200)
    year_graduation = models.IntegerField(verbose_name='Год окончания школы', default=timezone.now().year)
    medal = models.CharField(verbose_name='Наличие медали', choices=MedalTypes.CHOICES, max_length=200)

    objects = UserManager()

    class Meta:
        verbose_name = 'Абитуриент'
        verbose_name_plural = 'Абитуриенты'

    def __str__(self):
        return self.full_name

    def get_medal_name(self):
        return MedalTypes.NAMES[self.medal]

    def to_json(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'passport': self.passport,
            'school': self.school,
            'year_graduation': self.year_graduation,
            'medal': self.get_medal_name()
        }


User._meta.get_field('email')._unique = True
User._meta.get_field('email')._blank = False
User._meta.get_field('username')._unique = False


class EntrantSubject(models.Model):
    entrant = models.ForeignKey(User, verbose_name='Абитуриент', on_delete=models.CASCADE)
    subject = models.ForeignKey('university.Subject', verbose_name='Предмет', on_delete=models.CASCADE)
    score = models.PositiveIntegerField(verbose_name='Количество баллов')

    class Meta:
        verbose_name = 'Связь Абитуриент-Предмет'
        verbose_name_plural = 'Связи Абитуриент-Предмет'

    def __str__(self):
        return '{0}:{1}'.format(self.entrant.full_name, self.subject.title)

    def to_json(self):
        return {
            'id': self.id,
            'score': self.score,
            'subject': {
                'id': self.subject.id,
                'title': self.subject.title
            }
        }

