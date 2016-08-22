"""
Unit tests for the app.views.util module
"""

import unittest
from unittest import mock

import app.views.util

class TestRenderTemplate(unittest.TestCase):
    """
    Tests for the render_template function I have to make sure certain context
    always gets passed in to all views.
    """

    def setUp(self):

        self.source = 'index.html'

        # Set up a patcher for the post type
        patcher_post_type = mock.patch('app.models.Post_Type')
        self.mock_post_type = patcher_post_type.start()

        # use this to set the returned patches
        self.ordered_patches = []
        mock_get_ordered = mock.Mock(return_value=self.ordered_patches)
        self.mock_post_type.get_ordered = mock_get_ordered

        patcher_flask_render_template = mock.patch('flask.render_template')
        self.mock_flask_render_template = patcher_flask_render_template.start()

        # Return value from the mocked flask stock render template
        self.rendered_template = mock.Mock()
        self.mock_flask_render_template.return_value = self.rendered_template

    def tearDown(self):
        # Stop all patches
        mock.patch.stopall()

    def test_no_post_types(self):
        # The simplest case.
        rendered_template_result = app.views.util.render_template(self.source)

        # Check that flask's render template was callled with the correct args
        self.mock_flask_render_template.assert_called_once_with(
            self.source,
            post_types=[]
        )

        # Check that we return the rendered template
        self.assertEqual(rendered_template_result, self.rendered_template)

    def test_one_post_type(self):

        type_url_name = 'blog'
        type_name = 'Blog'

        mock_post_type = mock.Mock()
        mock_post_type.type_url_name = type_url_name
        mock_post_type.type_name = type_name

        self.ordered_patches.append(mock_post_type)

        app.views.util.render_template(self.source)

        # Check that flask's render template was called with the correct args
        self.mock_flask_render_template.assert_called_once_with(
            self.source,
            post_types=[(type_url_name, type_name)]
        )

    def test_multiple_post_types(self):
        type_url_name_0 = 'blog'
        type_name_0 = 'Blog'

        type_url_name_1 = 'project'
        type_name_1 = 'Project'

        mock_post_type_0 = mock.Mock()
        mock_post_type_0.type_url_name = type_url_name_0
        mock_post_type_0.type_name = type_name_0

        mock_post_type_1 = mock.Mock()
        mock_post_type_1.type_url_name = type_url_name_1
        mock_post_type_1.type_name = type_name_1

        self.ordered_patches.append(mock_post_type_0)
        self.ordered_patches.append(mock_post_type_1)

        app.views.util.render_template(self.source)

        # Check that flask's render template was called with the correct args
        self.mock_flask_render_template.assert_called_once_with(
            self.source,
            post_types=[(type_url_name_0, type_name_0), (type_url_name_1, type_name_1)]
        )

    def test_other_context(self):
        other_context = {'foo': 'bar'}
        app.views.util.render_template(self.source, **other_context)

        self.mock_flask_render_template.assert_called_once_with(
            self.source,
            post_types=[],  # always called with this
            **other_context
        )
