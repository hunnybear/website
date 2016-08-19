import datetime
import random
import sys

import app
import app.models

sys.path.append(os.path.split(os.path.split(os.getcwd())[0])[0])

BRANCH_BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# For testing
import app.testing.testing_posts

POSTS_TO_ADD = 10


def get_random_dates(count):
    current = datetime.datetime.utcnow()

    for _i in range(count):
        yield current
        day_delta = random.randrange(30)
        hour_delta = random.randrange(24)
        minute_delta = random.randrange(60)
        second_delta = random.randrange(60)
        current = current - datetime.timedelta(
            days=day_delta,
            hours=hour_delta,
            minutes=minute_delta,
            seconds=second_delta,
        )


def make_post(user, title, text, timestamp):

    post = app.models.Post(
        title=title,
        author=user,
        body=text,
        timestamp=timestamp
    )

    return post


def run(post_count=POSTS_TO_ADD):
    users = app.models.User.query.all()

    posts = []

    for timestamp in get_random_dates(post_count):
        user = random.choice(users)
        title, text = random.choice(app.testing.testing_posts.POSTS)

        posts.append(make_post(user, title, text, timestamp))

    app.db.session.add_all(posts)
    app.db.session.commit()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        post_count = int(sys.argv[1])
    else:
        post_count = POSTS_TO_ADD
    run(post_count=post_count)
