# -*- coding: utf-8 -*-
import os

# Set the application name
application = 'YAMS'

# Set paths
icon = '/Users/taawake2/projects/personal/yams/client/assets/icons/app.icns'
app_path = '/Users/taawake2/projects/personal/yams/client/dist/YAMS.app'

# Volume format (don't change)
format = 'UDBZ'

# Volume size (don't change)
size = '250M'

# Files to include
files = [
    (app_path, 'YAMS.app')
]

# Symlinks to create
symlinks = {
    'Applications': '/Applications'
}

# Volume icon
badge_icon = icon

# Window configuration
window_rect = ((100, 100), (640, 480))
icon_locations = {
    'YAMS.app': (140, 120),
    'Applications': (500, 120)
}

# Set the background
background = 'builtin-arrow'

# Volume name
volume_name = 'YAMS Installer'

# DMG name
filename = 'YAMS.dmg'

# Icon size
icon_size = 128

# Text size
text_size = 12

# Show item info
show_item_info = False

# Include icon view settings
include_icon_view_settings = True

# Include background
include_background = True

# Show status bar
show_status_bar = False

# Show tab view
show_tab_view = False

# Show toolbar
show_toolbar = False

# Show pathbar
show_pathbar = False

# Show sidebar
show_sidebar = False

# Sidebar width
sidebar_width = 180
