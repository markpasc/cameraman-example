import re

from google.appengine.ext.webapp import template


register = template.create_template_register()


@register.filter
def superspaceless(text):
    return re.sub(r'>\s+<', '><', text)
