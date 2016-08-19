import flask_wtf
import wtforms
from wtforms import validators

from app import config


class LoginForm(flask_wtf.Form):
    openid = wtforms.StringField(
        'openid',
        validators=[validators.DataRequired()]
    )
    remember_me = wtforms.BooleanField('remember_me', default=False)


class EditForm(flask_wtf.Form):
    """Form used for editing a user."""
    nickname = wtforms.StringField(
        'nickname',
        validators=[validators.DataRequired()]
    )

    about_me = wtforms.TextAreaField(
        'about_me',
        validators=[
            validators.Length(
                min=0,
                max=config.ABOUT_ME_LENGTH
            )
        ]
    )
    url_subpath = wtforms.StringField(
        'url_name',
        validators=[validators.Length(min=0, max=config.URL_NAME_LENGTH)]
    )


class PostForm(flask_wtf.Form):
    """
    Form used for composing or editing a post or project.

    *Fields:*

        :``title``: `string` the title of the post
        :``post``:  `string` the body of the post
        :``slug``:  `string` the slug for the post

    """

    title = wtforms.StringField(
        'title',
        validators=[validators.Length(
            min=1,
            max=config.MAX_POST_TITLE_LENGTH
        )]
    )
    post = wtforms.TextAreaField('post', validators=[validators.DataRequired()])

    slug = wtforms.StringField(
        'slug',
        validators=[validators.Length(min=0, max=config.MAX_SLUG_LENGTH)]
    )
