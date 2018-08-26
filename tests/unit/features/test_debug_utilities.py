from neopy import NeoView, console
from core.util.debug import format_component_name, warn
from tests.helpers.to_have_been_warned import has_warned
from unittest.mock import MagicMock, ANY


def test_properly_format_component_names():
    nv = NeoView()
    assert format_component_name(nv) == '<Root>'

    nv().root = None
    nv().options.name = 'hello-there'
    assert format_component_name(nv) == '<HelloThere>'

    nv().options.name = None
    nv().options._componentTag = 'foo-bar-1'
    assert format_component_name(nv) == '<FooBar1>'

    nv().options._componentTag = None
    nv().options.__file = '/foo/bar/baz/SomeThing.vue'
    assert format_component_name(nv) == f'<SomeThing> at {nv().options.__file}'
    assert format_component_name(nv, false) == '<SomeThing>'

    nv().options.__file = 'C:\\foo\\bar\\baz\\windows_file.vue'
    assert format_component_name(nv) == f'<WindowsFile> at {nv().options.__file}'
    assert format_component_name(nv, false) == '<WindowsFile>'


def test_generate_correct_component_hierarchy_trace():
    class Three(NeoView):
        pass

    class Two(NeoView):
        def render(self, h):
            return h(Three)

    class One(NeoView):
        def render(self, h):
            return h(Two)

    class Component(NeoView):
        def render(self, h):
            return h(One)

    assert has_warned(
        """Failed to mount component: template or render function not defined.
found in
---> <Three>
       <Two>
         <One>
           <Root>"""
    )


def test_generate_correct_component_hierarchy_trace_recursive():
    i = 0

    class Three(NeoView):
        pass

    class Two(NeoView):
        def render(self, h):
            return h(Three)

    class One(NeoView):
        def render(self, h):
            i += 1
            return h(One) if i < 5 else h(Two)

    assert has_warned(
        """Failed to mount component: template or render function not defined.
found in
---> <Three>
       <Two>
         <One>... (5 recursive calls)
           <Root>"""
    )

msg = 'message'
nv = NeoView()


def test_warn_calls_warn_handler_if_warn_handler_is_set():
    NeoView.config.warn_handler = MagicMock()
    warn(msg, nv)
    NeoView.config.warn_handler.assert_any_call(msg, nv, ANY)
    NeoView.config.warn_handler = None


def test_calls_console_error_if_silent_is_false():
    NeoView.config.silent = False
    console.error = MagicMock()
    warn(msg, nv)
    console.error.assert_called()
    assert has_warned(msg)


def test_does_not_call_console_error_if_silent_is_true():
    NeoView.config.silent = True
    console.error = MagicMock()
    warn(msg, nv)
    console.error.assert_not_called()
    NeoView.config.silent = False
