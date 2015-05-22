from collections import defaultdict
from compressor.templatetags.compress import CompressorNode

from django.template import Library, Node, Template, TemplateSyntaxError


register = Library()


CONTEXT_VARIABLE_NAME = 'static_grouper_dict'


class AddStaticNode(Node):
    def __init__(self, parser, token):
        contents = token.split_contents()
        if len(contents) != 2:
            raise TemplateSyntaxError

        self.static_type = contents[1]
        self.nodelist = parser.parse(('endaddstatic',))
        parser.delete_first_token()

    def render(self, context):
        output = self.nodelist.render(context).strip()
        static_grouper_dict = context.get(CONTEXT_VARIABLE_NAME)
        if static_grouper_dict is None:
            root_context = context.dicts[0]
            root_context[CONTEXT_VARIABLE_NAME] = \
                static_grouper_dict = defaultdict(list)
        if output not in static_grouper_dict[self.static_type]:
            static_grouper_dict[self.static_type].append(output)
        return ''

register.tag('addstatic', AddStaticNode)


class StaticListNode(Node):
    def __init__(self, parser, token):
        contents = token.split_contents()
        if len(contents) not in (2, 3):
            raise TemplateSyntaxError

        self.static_type = contents[1]
        if len(contents) == 3:
            assert contents[2] == 'compress'
            self.compress = True
        else:
            self.compress = False

        self.following_nodelist = parser.parse()

    def render(self, context):
        static_grouper_dict = context.get(CONTEXT_VARIABLE_NAME, defaultdict(list))
        following = self.following_nodelist.render(context)
        inner = ''.join(static_grouper_dict[self.static_type])
        if self.compress:
            inner = CompressorNode(
                nodelist=Template(inner).nodelist, kind=self.static_type,
                mode='file').render(context=context)
        return inner + following

register.tag('static_list', StaticListNode)
