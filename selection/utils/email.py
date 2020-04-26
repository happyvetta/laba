from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings


class EmailManager:
    @classmethod
    def send_email(cls, theme, template, context, email):
        try:
            t = get_template(template)
            html_content = t.render(context)
            msg = EmailMultiAlternatives(theme, html_content, settings.EMAIL_HOST_USER, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            print(e)
            pass

    @classmethod
    def create_account_notification(cls, user, password):
        t = 'mail/create_account_notification.html'
        context = {'user': user, 'password': password}
        theme = 'Регистрация в личном кабинете'
        cls.send_email(theme, t, context, user.email)
