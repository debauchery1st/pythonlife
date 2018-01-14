[app]
title = PyLife
package.name = pylife
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py
requirements = kivy
orientation = portrait
author = © Trevor
osx.python_version = 2
osx.kivy_version = 1.9.1

[buildozer]
log_level = 1
warn_on_root = 1