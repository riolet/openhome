import oauthlib.oauth2.rfc6749.errors
from openhome import settings
from property.oauth_consumer import Authorization
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpRequest
from django.urls import reverse
from django.utils import timezone

from .models import User


def login(request):
    """
    :type request: HttpRequest
    """
    l_model = LoginView(request)

    if request.method == 'POST':
        return HttpResponseNotAllowed(['GET'])
    else:
        return l_model.get_method()


def logout(request):
    l_model = LoginView(request)
    l_model.log_out()
    return HttpResponseRedirect(reverse("property:home"))


class LoginView:
    def __init__(self, request):
        """
        :type request: HttpRequest
        """
        self.request = request
        self.session = request.session
        self.redirect_uri = settings.OAUTH['login_uri']
        self.login_redirect = reverse("property:account")
        self.scope = settings.OAUTH['scope']
        self.oauth = Authorization(
            session=self.session,
            authorization_url=settings.OAUTH['authorization_url'],
            token_url=settings.OAUTH['token_url'],
            client_id=settings.OAUTH['client_id'],
            client_secret=settings.OAUTH['client_secret'],
            default_redirect_uri=settings.OAUTH['redirect_uri'],
            default_scope_requested=settings.OAUTH['scope'])

    def get_token(self):
        authorization_response = self.request.build_absolute_uri()
        try:
            # redirect_uri must match between get_auth_code and get_token.
            # scope must match between get_auth_code and get_token
            self.oauth.fetch_token(authorization_response, redirect_uri=self.redirect_uri, scope=self.scope)
        except oauthlib.oauth2.rfc6749.errors.AccessDeniedError:
            print("Access was denied. Reason unknown.")
            return False
        except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:
            print("Access was denied. Error: Invalid Grant.")
            return False
        return True

    def get_auth_code(self):
        # redirect_uri must match between get_auth_code and get_token.
        # scope must match between get_auth_code and get_token
        authorization_url = self.oauth.get_auth_url(redirect_uri=self.redirect_uri, scope=self.scope)
        return HttpResponseRedirect(authorization_url)

    def request_login_info(self):
        """
        returned data will resemble this:
        {'user': {
            'last_access': 1506375126,
            'id': 2,
            'email': 'joe.pelz@riolet.com',
            'name': 'Joe',
            'groups': 'read write'
         },
         'subscription': {
            'subscription_type': 'Basic',
            'status': 'active',
            'subscription_id': 5,
            'user_id': 2,
            'app_id': 'abc123'
         },
         'status': 'success'
        }
        """

        data = self.oauth.request(settings.OAUTH["resource"])
        return data

    def log_in(self):
        login_info = self.request_login_info()
        self.session['logged_in'] = True
        account = login_info['user']['email']
        self.session['login_email'] = account

        try:
            user = User.objects.get(pk=account.lower())
            user.last_login = timezone.now()
        except User.DoesNotExist:
            user = User(
                login_email=account.lower(),
                email=account,
                last_login=timezone.now()
            )
        user.save()

    def log_out(self):
        self.session.flush()

    def get_method(self):
        data = self.request.GET
        if 'login_redirect' in data:
            self.login_redirect = data['login_redirect']
            # save for the return trip
            self.session['login_redirect'] = self.login_redirect

        if 'state' in data and 'code' in data:
            if self.get_token():
                self.log_in()
                return HttpResponseRedirect(self.login_redirect)
            else:
                self.log_out()
                return HttpResponseRedirect(self.login_redirect)
        elif 'error' in data:
            print("Error response.\n\t{0}".format(data['error']))
            if 'error_description' in data:
                print("\t{0}".format(data['error_description']))
            # TODO: have destination page indicate to user that an error has occurred.
            return HttpResponseRedirect(reverse("property:home"))
        else:
            return self.get_auth_code()

        # this code should be unreachable.
        return HttpResponseRedirect(reverse("property:home"))
