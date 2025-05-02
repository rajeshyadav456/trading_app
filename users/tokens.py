from rest_framework_simplejwt.tokens import AccessToken

class CustomAccessToken(AccessToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token['user_type'] = user.user_type
        token['email'] = user.email
        token['is_superuser'] = user.is_superuser
        token['mobile'] = user.mobile
        return token


        