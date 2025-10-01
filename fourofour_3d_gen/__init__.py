import bpy
from pathlib import Path

from . import preferences
from . import ops, ui, props
from .spz_updater import SPZUpdater
from .spz_loader import init_spz


modules = [
    preferences,
    ops,
    ui,
    props,
]

def register():
    if SPZUpdater.need_update():
        SPZUpdater.update()

    for m in modules:
        m.register()

    try:
        pkg_dir = Path(__file__).resolve().parent
        print(f"Initializing SPZ with library path: {pkg_dir}")
        init_spz(str(pkg_dir))
    except Exception as e:
        print(f"SPZ initialization failed: {e}")   
    
def unregister():
    for m in reversed(modules):
        m.unregister()
