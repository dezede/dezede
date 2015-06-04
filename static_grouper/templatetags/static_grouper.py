from collections import defaultdict
from compressor.templatetags.compress import CompressorNode

from django.template import Library, Node, Template, TemplateSyntaxError


register = Library()


CONTEXT_VARIABLE_NAME = 'static_grouper_dict'


class AddStaticNode(Node):
    def __init__(self, parser, token):
        contents = token.split_contents()
        if len(contents) not in (2, 3):
            raise TemplateSyntaxError

        if len(contents) == 3:
            assert contents[2] == 'nocompress'
            self.compress = False
        else:
            self.compress = True

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
            static_grouper_dict[self.static_type].append(
                (self.compress, output))
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

    def groups_iterator(self, static_grouper_dict):
        compressed_group = []
        for compress, output in static_grouper_dict[self.static_type]:
            if compress:
                compressed_group.append(output)
            else:
                if compressed_group:
                    yield True, ''.join(compressed_group)
                    compressed_group = []
                yield False, output
        if compressed_group:
            yield True, ''.join(compressed_group)

    def render(self, context):
        static_grouper_dict = context.get(CONTEXT_VARIABLE_NAME, defaultdict(list))
        following = self.following_nodelist.render(context)

        inner = ''
        for compress, output in self.groups_iterator(static_grouper_dict):
            if compress and self.compress:
                inner += CompressorNode(
                    nodelist=Template(output).nodelist, kind=self.static_type,
                    mode='file').render(context=context)
            else:
                inner += output

        return inner + following

register.tag('static_list', StaticListNode)
