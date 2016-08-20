import unittest.mock
import unittest

import sys

import app.auth



class TestGoogle(unittest.TestCase):
    def setUp(self):
        self.sign_in = app.auth.GoogleSignIn()

    @unittest.mock.patch('app.auth.GoogleSignIn._get_google_params')
    @unittest.mock.patch('rauth.OAuth2Service')
    def test_init(self, mock_auth_service, mock_get_params):
        mock_get_params.return_value = {
            "authorization_endpoint": r"https://accounts.google.com/o/oauth2/v2/auth",
            "userinfo_endpoint": r"https://www.googleapis.com/oauth2/v3/userinfo",
            "token_endpoint": r"https://www.googleapis.com/oauth2/v4/token"

        }
        self.assertEqual(self.sign_in.provider_name, 'google')

        # Assert that the auth service was called


    def test_callback(self):
        pass
