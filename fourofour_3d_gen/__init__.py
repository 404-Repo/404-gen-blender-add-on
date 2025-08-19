from . import dependencies
from . import preferences

modules = []


def register():
    preferences.register()
    modules.append(preferences)
    
    if dependencies.installed():
        from . import props, ui, ops

        ui.register()
        props.register()
        ops.register()
        modules.append(ops)
        modules.append(ui)
        modules.append(props)

        try:
            from .spz_loader import init_spz
            from pathlib import Path

            pkg_dir = Path(__file__).resolve().parent
            print(f"Initializing SPZ with library path: {pkg_dir}")
            init_spz(str(pkg_dir))
        except Exception as e:
            # Report failure to load native SPZ library to console only
            print(f"SPZ initialization failed: {e}")


def unregister():
    for m in modules:
        m.unregister()
