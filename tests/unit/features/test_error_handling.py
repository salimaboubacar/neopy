import asyncio

from neopy import NeoView, Prop, console
from tests.helpers.wait_for_update import wait_for_update


def create_error_test_components():

    components = {}

    class DataComponent(NeoView):
        def __init__(self):
            raise RuntimeError('data')

        def render(self, h):
            return h('div')

    components['data'] = DataComponent

    class RenderComponent(NeoView):
        def render(self, h):
            raise RuntimeError('render')

    components['render'] = RenderComponent

    for timing in ['before', 'after']:
        for hook in ['create', 'mount', 'update', 'destroy']:
            hook_name = f'{timing}_{hook}'

            class HookComponent(NeoView):
                n = Prop(required=True)

                def render(self, h):
                    return h('div', self.n)

            def fn(self):
                raise RuntimeError(hook_name)

            setattr(HookComponent, hook_name, fn)
            components[hook_name] = HookComponent

    for hook in ['bind', 'update', 'unbind']:
        key = f'directive {hook}'

        class HookComponent(NeoView):
            n = Prop(required=True)
            template = '<div np-foo="n">{{{{ n }}}}</div>'

        def fn(self):
            raise RuntimeError(key)

        HookComponent.directives = {
            'foo': {
                hook: fn
            }
        }
        components[key] = HookComponent

    class UserWatcherGetterComponent(NeoView):
        n = Prop(required=True)

        def created(self):
            self().watch(
                lambda: self.n + self.a.b.c,
                lambda val: console.log(f'user watcher fired: {val}')
            )

    components['userWatcherGetter'] = UserWatcherGetterComponent

    class UserWatcherCallbackComponent(NeoView):
        n = Prop(required=True)

        @watch(n)
        def throw_error(self, val):
            raise RuntimeError('userWatcherCallback error')

        def render(self, h):
            return h('div', self.n)

    components['userWatcherCallback'] = UserWatcherCallbackComponent

    class EventComponent(NeoView):
        def before_create(self):
            self().on('e', lambda: exec('raise RuntimeError("event"))'))

        def mounted(self):
            self().emit('e')

        def render(self, h):
            return h('div')

    return components


def create_test_instance(component_cls):
    class TestInstance(NeoView):
        def __init__(self):
            self.n = 0
            self.ok = True

        def render(self, h):
            return h('div', [
                'n:' + self.n + '\n',
                h(component_cls(ref='child', n=self.n)) if self.ok
                else None
            ])
    test_instance = TestInstance()
    return test_instance.mount()


async def assert_root_instance_active(nv, chain):
    assert 'n:1\n' in nv().el.innerHTML
    nv.n += 1
    await wait_for_update(nv)
    assert 'n:1\n' in nv().el.innerHTML
