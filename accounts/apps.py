from wagtail.users.apps import WagtailUsersAppConfig


class CustomWagtailUsersConfig(WagtailUsersAppConfig):
    user_viewset = 'accounts.viewsets.CustomUserViewSet'
