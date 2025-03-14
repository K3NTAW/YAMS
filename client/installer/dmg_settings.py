# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path

# Use custom volume icon
icon = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'app.icns')

# Volume format (see hdiutil create -help)
format = 'UDBZ'

# Volume size
size = '200M'

# Files to include
files = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist', 'YAMS.app'),
]

# Symlinks to create
symlinks = {
    'Applications': '/Applications'
}

# Volume icon
badge_icon = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'app.icns')

# Window configuration
window_rect = ((100, 100), (640, 280))
background = 'builtin-arrow'

# Icon view configuration
icon_size = 128
text_size = 14
icon_locations = {
    'YAMS.app': (120, 120),
    'Applications': (500, 120)
}
