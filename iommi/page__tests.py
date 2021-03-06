from django.test import override_settings
from tri_struct import Struct

from iommi import (
    Fragment,
    html,
    Page,
)
from iommi._web_compat import (
    Template,
)
from iommi.part import as_html
from iommi.traversable import declared_members
from tests.helpers import (
    prettify,
    req,
)


def test_page_constructor():
    class MyPage(Page):
        h1 = html.h1()

    my_page = MyPage(
        parts__foo=html.div(_name='foo'),
        parts__bar=html.div()
    )

    assert ['h1', 'foo', 'bar'] == list(declared_members(my_page).parts.keys())
    my_page = my_page.bind(request=None)
    assert ['h1', 'foo', 'bar'] == list(my_page.parts.keys())


@override_settings(
    MIDDLEWARE_CLASSES=[],
)
def test_page_render():
    class MyPage(Page):
        header = html.h1('Foo')
        body = html.div('bar bar')

    my_page = MyPage()
    request = req('get')
    request.user = Struct()
    my_page = my_page.bind(request=request)

    response = my_page.render_to_response()

    expected_html = '''
        <html>
            <head></head>
            <body>
                 <h1> Foo </h1>
                 <div> bar bar </div>
            </body>
        </html>
    '''

    prettified_expected = prettify(expected_html)
    prettified_actual = prettify(response.content)
    assert prettified_expected == prettified_actual


def test_promote_str_to_fragment_for_page():
    class MyPage(Page):
        foo = 'asd'

    page = MyPage()
    assert isinstance(declared_members(page).parts.foo, Fragment)


def test_as_html_integer():
    assert as_html(part=123, context={}) == '123'


def test_page_context():
    class MyPage(Page):
        part1 = Template('Template: {{foo}}\n')
        part2 = html.div(template=Template('Template2: {{foo}}'))

        class Meta:
            context__foo = 'foo'

    assert MyPage().bind(request=req('get')).__html__() == 'Template: foo\nTemplate2: foo'
