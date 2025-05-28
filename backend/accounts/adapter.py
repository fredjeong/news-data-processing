from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_field


class CustomUserAccountAdapter(DefaultAccountAdapter):

    def clean_username(self, username, shallow=False):
        # username을 사용하지 않으므로 무시
        return None

    def generate_unique_username(self, txts, regex=None):
        # username을 사용하지 않으므로 무시
        return None

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """

        user = super().save_user(request, user, form, commit=False)
        user_field(user, 'email', request.data.get('email'))
        user_field(user, 'first_name', request.data.get('first_name'))
        user_field(user, 'last_name', request.data.get('last_name'))
        user_field(user, 'date_of_birth', request.data.get('date_of_birth'))

        user.save()
        
        return user
    