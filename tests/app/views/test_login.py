import unittest
from unittest import mock

import app.views.login
import app.flash_messages

class CallbackTests(unittest.TestCase):

    def setUp(self):
        # out of sheer laziness
        self.user_name = 'name'
        self.user_social_id = 'social_id'
        self.user_email = 'email'
        self.user_avatar = 'avatar'

        # Mock the db session
        self.patcher_db_session = mock.patch('app.db.session')
        self.mock_db_session = self.patcher_db_session.start()

        # Mock the get_provider() calll
        self.patcher_get_provider = mock.patch('app.auth.OAuthSignIn.get_provider')
        self.mock_get_provider = self.patcher_get_provider.start()
        mock_oauth = mock.Mock(name='oauth')
        # Exposing this to the class b/c this is how you set the google auth
        # returns
        self.mock_oauth_callback = mock.Mock(
            name="oauth.callback",
            return_value=(
                self.user_social_id,
                self.user_name,
                self.user_email,
                self.user_avatar
            )
        )

        mock_oauth.callback = self.mock_oauth_callback
        self.mock_get_provider.return_value = mock_oauth

        # Setup mock for flask current user
        self.patcher_current_user = mock.patch('flask_login.current_user')
        self.mock_current_user = self.patcher_current_user.start()
        # We want this to be False in all cases except when we're testing the
        # case when a user is already logged in, so we'll set this to False and
        # just handle swiching it in that one case.
        self.mock_current_user.is_anonymous = True

        # Setup mocks for the flask url for and redirect functions
        # Return values
        self.return_url = mock.Mock()
        self.redirect_result = mock.Mock(name="flask.redirect() return val")

        self.patcher_url_for = mock.patch('flask.url_for')
        self.mock_url_for = self.patcher_url_for.start()
        self.mock_url_for.return_value = self.return_url

        self.patcher_redirect = mock.patch('flask.redirect')
        self.mock_redirect = self.patcher_redirect.start()
        self.mock_redirect.return_value = self.redirect_result

        # Setup mocks for the user class, user instance and user query

        self.mock_user_instance = mock.Mock(name='User instance')
        self.mock_user_instance.name = self.user_name
        self.mock_user_instance.avatar_path = self.user_avatar
        self.mock_user_instance.email = self.user_email
        self.mock_user_instance.social_id = self.user_social_id

        self.patcher_user_class = mock.patch('app.models.User')
        self.mock_user_class = self.patcher_user_class.start()
        self.mock_user_class.return_value = self.mock_user_instance

        mock_filtered = mock.Mock(name='filtered query')

        self.mock_first = mock.Mock(name='first() mock', return_value=self.mock_user_instance)
        mock_filtered.first = self.mock_first

        mock_filter_by = mock.Mock(
            name='filter_by() mock', return_value=mock_filtered
        )

        mock_user_query = mock.Mock(name="query mock")
        mock_user_query.filter_by = mock_filter_by
        self.mock_user_class.query = mock_user_query

        # Setup mock for flask_login.login_user
        self.patcher_login_user = mock.patch('flask_login.login_user')
        self.mock_login_user = self.patcher_login_user.start()

    def tearDown(self):
        self.patcher_url_for.stop()
        self.patcher_redirect.stop()
        self.patcher_current_user.stop()
        self.patcher_login_user.stop()
        self.patcher_user_class.stop()
        self.patcher_get_provider.stop()
        self.patcher_db_session.stop()

    def test_callback_no_auth(self):
        pass

    def test_callback_already_logged_in(self):

        self.mock_current_user.is_anonymous = False

        index_view = app.views.login.callback('google')

        # This is our most important result, really.
        self.assertIs(self.redirect_result, index_view)

        # make sure it doesn't attempt to even get the provider
        self.mock_get_provider.assert_not_called()

        # make sure the flask functions are called once for the redirect
        self.mock_url_for.assert_called_once_with('index')
        self.mock_redirect.assert_called_once_with(self.return_url)

    @mock.patch('flask.flash')
    def test_callback_no_email(self, flash_mock):

        self.mock_oauth_callback.return_value = (None, None, None, None)

        return_value = app.views.login.callback('google')

        self.assertEqual(return_value, self.redirect_result)

        # make sure we called oauth.callback
        self.mock_oauth_callback.assert_called_once_with()
        flash_mock.assert_called_once_with(app.flash_messages.AUTH_FAILED)

    def test_callback_new_user(self):

        # set the User query (by way of first()) to return None, signifying
        # that there are no users returned by the query.
        self.mock_first.return_value = None

        app.login.callback('google')

        # Make sure that a user was created
        self.mock_user_class.assert_called_once_with(
            social_id=self.user_social_id, name=self.user_name, email=self.user_email
        )

        # Make sure that the user instance was added to the session
        self.mock_db_session.add.assert_called_once_with(self.mock_user_instance)

        # Make sure the session was commited
        self.mock_db_session.commit.assert_called_once_with()

        # Make sure the user is logged in
        self.mock_login_user.assert_called_with(self.mock_user_instance, True)

    def test_callback_new_name(self):
        old_name = self.user_name + "_old"
        self.mock_user_instance.name = old_name
        app.views.login.callback('google')

        self.assertEqual(self.mock_user_instance.name, self.user_name)
        self.mock_db_session.commit.assert_called_once_with()
        self.mock_login_user.assert_called_once_with(self.mock_user_instance, True)

    def test_callback_new_avatar(self):
        old_avatar = self.user_avatar + "_old"
        self.mock_user_instance.avatar_path = old_avatar
        app.views.login.callback('google')

        self.assertEqual(self.mock_user_instance.avatar_path, self.user_avatar)
        self.mock_db_session.commit.assert_called_once_with()
        self.mock_login_user.assert_called_once_with(self.mock_user_instance, True)

    def test_callback_existing_user(self):
        # Test the case where the user exists and no data has changed

        app.views.login.callback('google')

        self.mock_db_session.commit.assert_not_called()
        self.mock_login_user.assert_called_once_with(self.mock_user_instance, True)

