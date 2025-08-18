from . import dependencies
from . import preferences

modules = []


def register():
    preferences.register()
    modules.append(preferences)
    # if dependencies.installed():
    #     from . import props, ui, ops

    #     ui.register()
    #     props.register()
    #     ops.register()
    #     modules.append(ops)
    #     modules.append(ui)
    #     modules.append(props)


def unregister():
    for m in modules:
        m.unregister()
