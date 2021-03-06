import flask
import logging
import json
import rauth
import urllib.request

import app.log

from app import config

logger = logging.getLogger('')

GOOGLE_INFO_URL = 'https://accounts.google.com/.well-known/openid-configuration'


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = app.application.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return flask.url_for(
            'callback',
            provider=self.provider_name,
            _external=True,
            _scheme='https'
        )

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}

            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider

        try:
            return self.providers[provider_name]
        except KeyError as exc:
            providers_str = ', '.join(self.providers.keys())
            error_msg = 'provider not found, available providers: {0}'.format(providers_str)
            app.application.logger.error(error_msg)
            raise exc


class GoogleSignIn(OAuthSignIn):
    """
    OAuth sign in class for google sign ins. Only thing i'm going to be using.
    Learned how to do this from a tutorial, I'm not going to touch it until I
    feel more confident in the oAuth Stuff.
    """

    def __init__(self):
        super(GoogleSignIn, self).__init__('google')

        google_params = self._get_google_params()

        self.service = rauth.OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=google_params.get('authorization_endpoint'),
            base_url=google_params.get('userinfo_endpoint'),
            access_token_url=google_params.get('token_endpoint')
        )

    def _get_google_params(self):
         # We can't use json.load directly on the file-like object because
        # python 3 and bytes
        googleinfo = urllib.request.urlopen(GOOGLE_INFO_URL)
        googlieinfo_data = googleinfo.read()
        # TODO use googleinfo data to get the encoding
        google_params = json.loads(googlieinfo_data.decode('utf-8'))

        return google_params

    def authorize(self):
        return flask.redirect(
            self.service.get_authorize_url(
                scope='email',
                response_type='code',
                redirect_uri=self.get_callback_url()
            )
        )

    def callback(self):
        """
        Cribbed my whole auth system from a tutorial, I'll come back and make
        all of this more sensible when I have a better grasp of the oAuth.
        """
        if 'code' not in flask.request.args:
            return None, None, None, None

        oauth_session = self.service.get_auth_session(
            data={
                'code': flask.request.args['code'],
                'grant_type': 'authorization_code',
                'redirect_uri': self.get_callback_url(),
            },
            decoder=lambda x: json.loads(x.decode('utf-8'))
        )
        me = oauth_session.get('').json()

        # this is my attempt at not letting other people post on my
        # site. Using google auth with flask the easy way. Could also
        # do my own auth, but why?
        if me['email'] not in config.ALLOWED_USERS:
            flask.flash('{0} is not a whitelisted email'.format(me['email']))
            return None, None, None, None

        # TODO might want to struct this up
        return(me['sub'], me['name'], me['email'], me.get('picture'))
