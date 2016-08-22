"""
Unit tests for the blog view module.
"""

import unittest
from unittest import mock

with mock.patch('app.models.Post_Type.query.all') as mock_post_type_query:
    # We don't need to register any views right now
    mock_post_type_query.return_value = [ ]
    import app.views.blog


class TestMakeFunctions(unittest.TestCase):
    """
    Tests for the functions that make the functions that are actually used for
    the views
    """

    def setUp(self):

        globals_patcher = mock.patch('flask.g')
        globals_patcher.start()

        self.mock_post_type = mock.Mock(name="Post_Type")

        # Mock the get posts paginated method
        self.mock_get_posts_paginated = mock.Mock(name="get_posts_paginated()")
        self.mock_posts = mock.Mock(name="returned posts")
        self.mock_get_posts_paginated.return_value = self.mock_posts

        self.mock_post_type.get_posts_paginated = self.mock_get_posts_paginated

        # Mock the get by slug method
        self.mock_post = mock.Mock(name='Post')
        self.mock_get_by_slug = mock.Mock(name='get_by_slug()', return_value=self.mock_post)
        self.mock_post_type.get_by_slug = self.mock_get_by_slug

        patcher_render_template = mock.patch('app.views.util.render_template')
        self.mock_render_template = patcher_render_template.start()
        self.rendered_template = mock.Mock('rendered template')
        self.mock_render_template.return_value = self.rendered_template

    def tearDown(self):
        mock.patch.stopall()

    def test_make_posts_function(self):

        posts_function = app.views.blog._make_posts_function(self.mock_post_type)

        posts_function()

        self.mock_get_posts_paginated.assert_called_once_with(page=1)

        call_args, call_kwargs = self.mock_render_template.call_args

        #assert the posts_function calls render_template with blog.html as the
        # source
        self.assertEqual(call_args[0], 'blog.html')

        # assert that the posts function calls render_template with the output
        # from paginated post query as the posts kwarg
        self.assertIn('posts', call_kwargs)
        self.assertEqual(self.mock_posts, call_kwargs['posts'])

    def test_make_posts_function_paginated_query(self):

        posts_function = app.views.blog._make_posts_function(self.mock_post_type)

        posts_function()

        self.mock_get_posts_paginated.assert_called_with(page=1)

        posts_function(3)

        self.mock_get_posts_paginated.assert_called_with(page=3)


    @mock.patch('flask.g.user')
    def test_make_slug_function(self, mock_user):

        # TODO published only tests
        mock_user.is_authenticated = False

        slug_function = app.views.blog._make_slug_function(self.mock_post_type)

        slug = 'spam'
        slug_function(slug)

        self.mock_post_type.get_by_slug.assert_called_once_with(slug, published_only=True)

    @mock.patch('flask.g.user')
    def test_slug_function_post(self, mock_user):

        slug_function = app.views.blog._make_slug_function(self.mock_post_type)

        # Test with return from post_type.get_by_slug default in setup (returns
        # a post).
        res = slug_function('spam')

        self.assertIs(res, self.rendered_template)

    @mock.patch('flask.g.user')
    def test_slug_function_no_post(self, mock_user):

        slug_function = app.views.blog._make_slug_function(self.mock_post_type)

        # Set the get_by_slug method to return None, so we should return a 404
        self.mock_get_by_slug.return_value = None
        res = slug_function('slug')

        self.assertEqual(res, (self.rendered_template, 404))



@mock.patch('app.application.add_url_rule')
class TestCreateRules(unittest.TestCase):

    def setUp(self):
        self.mock_post_type = mock.Mock(name='Post_Type')
        self.mock_post_type.url_name = 'blog'

        patcher_make_posts_function = mock.patch('app.views.blog._make_posts_function')
        mock_make_posts_function = patcher_make_posts_function.start()

        self.mock_posts_function = mock.Mock(name='posts_function()')
        mock_make_posts_function.return_value = self.mock_posts_function

    def tearDown(self):
        mock.patch.stopall()

    def test_main_rule(self, mock_add_url_rule):
        # TODO
        pass










