"""
Class for displaying time nicely using moment.js
"""

import jinja2


class moment(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, fmt):
        markup_str = '<script>\ndocument.write(moment("{0}").{1});\n</script>'
        markup_str = markup_str.format(self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), fmt)

        return jinja2.Markup(markup_str)

    def format(self, fmt):
        """Create a format string that can be inserted into Jinja"""
        format_str = 'format("{0}")'.format(fmt)
        return self.render(format_str)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")
