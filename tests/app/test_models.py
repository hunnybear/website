import unittest
from unittest import mock

import app.config
import app.models


class TestUser(unittest.TestCase):

    # use these for testing user creation
    social_id = 'abc'
    avatar_path = '/foo/bar/spam.png'
    name = 'Arthur'
    nickname = 'Arthur, King of the Britons'
    email = 'arthur@camelot.biz'
    url_name = 'arthur_king_of_the_britons'

    def _make_user(self):
        """
        Make a user instance for testing
        """

        user = app.models.User(
            social_id=self.social_id,
            avatar_path=self.avatar_path,
            name=self.name,
            nickname=self.nickname,
            email=self.email,
            url_name=self.url_name
        )

        return user

    def test_user_init(self):
        """
        Make sure we can init a user
        """

        user = self._make_user()

        self.assertEqual(user.name, self.name)
        self.assertEqual(user.social_id, self.social_id)
        self.assertEqual(user.avatar_path, self.avatar_path)
        self.assertEqual(user.nickname, self.nickname)
        self.assertEqual(user.email, self.email)


    def test_get_dispaly_name_with_nickname(self):

        user = self._make_user()

        self.assertEqual(user.get_display_name(), self.nickname)

    def test_get_display_name_without_nickname(self):

        # same as code from _make_user without the nickname line
        user = app.models.User(
            social_id=self.social_id,
            avatar_path=self.avatar_path,
            name=self.name,
            email=self.email
        )

        self.assertEqual(user.get_display_name(), self.name)

    def test_get_url_name_with_url_name(self):

        user = self._make_user()

        self.assertEqual(user.get_url_name(), self.url_name)
        self.assertEqual(user.get_url_name(), user.url_name)


    def test_get_url_name_without_url_name(self):

        # same as code from _make_user without the url_name line
        user = app.models.User(
            social_id=self.social_id,
            avatar_path=self.avatar_path,
            name=self.name,
            email=self.email
        )

        self.assertEqual(user.get_url_name(), str(user.id))

    def test_url_name_validator(self):

        user = self._make_user()

        invalid_names = [
            ('name_with\ttab', 'URL name cannot contain tabs'),
            ('name with_space', 'URL name can\'t contain spaces'),
            ('name_with\nnewline', 'URL name cannot contain newline char'),

            ('12345', 'URL name cannot resolve to a digit')
        ]

        for invalid_name, msg in invalid_names:

            with self.assertRaises(ValueError, msg=msg):
                user.validate_url_name(None, invalid_name)

        valid_names = [
            'user_1234',
            'userslug',
            'MixedCase',
            'ValidName123'
        ]

        # Check valid names
        for valid_name in valid_names:
            msg = '{0} should be a valid name'.format(valid_name)
            validated_name = user.validate_url_name(None, valid_name)
            self.assertEqual(validated_name, valid_name, msg=msg)


