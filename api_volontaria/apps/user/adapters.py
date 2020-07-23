from allauth.account.adapter import DefaultAccountAdapter

from django.contrib.auth import get_user_model

User = get_user_model()


class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        user.username = data['username']
        user.email = data['email']
        user.first_name = data['first_name']
        user.last_name = data['last_name']

        if 'password1' in data:
            user.set_password(data['password1'])
        else:
            user.set_unusable_password()

        self.populate_username(request, user)
        if commit:
            user.save()

        return user

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        pass
