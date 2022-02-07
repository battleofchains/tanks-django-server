from allauth.account import forms as user_forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.forms import BooleanField
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(admin_forms.UserCreationForm):
    class Meta(admin_forms.UserCreationForm.Meta):
        model = User

        error_messages = {
            "username": {"unique": _("This username has already been taken.")}
        }


class UserRegisterForm(user_forms.SignupForm):
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields["password2"] = user_forms.PasswordField(label=_("Confirm Password"))
        self.fields["notifications_disabled"] = BooleanField(label=_("I do not want to receive promotional emails"))

    def save(self, request):
        user = super(UserRegisterForm, self).save(request)
        user.notifications_disabled = self.cleaned_data.get('notifications_disabled', False)
        user.save()
        return user
