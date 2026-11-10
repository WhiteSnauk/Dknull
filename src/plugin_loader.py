"""Загрузка плагинов через importlib с изоляцией и логированием."""

import importlib.util
import logging
import sys
from pathlib import Path

log = logging.getLogger(__name__)


def load_plugins(plugin_dir, registry):
    """Загружает все .py из plugin_dir; register(registry) и NAME обязательны."""
    plugin_dir = Path(plugin_dir)
    if not plugin_dir.exists():
        return []

    loaded = []
    origins = {}
    for py_file in sorted(plugin_dir.glob('*.py')):
        if py_file.name.startswith('_'):
            continue
        mod_name = f"_plugin_{py_file.stem}"
        try:
            spec = importlib.util.spec_from_file_location(mod_name, py_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
            if not hasattr(module, 'register') or not hasattr(module, 'NAME'):
                log.warning(f"Plugin {py_file.name} missing NAME or register(), skipping")
                continue
            name = module.NAME
            if name in origins and origins[name] != str(py_file):
                log.warning(f"Plugin name conflict: {name} already registered, "
                            f"skipping {py_file.name}")
                continue
            module.register(registry)
            origins[name] = str(py_file)
            loaded.append(name)
            log.info(f"Loaded plugin: {name} from {py_file.name}")
        except Exception as e:
            log.warning(f"Failed to load plugin {py_file.name}: {e}")
    return loaded