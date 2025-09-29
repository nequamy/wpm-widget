from setuptools import setup

APP = ['src/wpm_widget/main.py']
DATA_FILES = []
OPTIONS = {
    'iconfile': None,  # You can add an .icns file path here if you have an icon
    'plist': {
        'CFBundleName': 'WPM Widget',
        'CFBundleDisplayName': 'WPM Widget',
        'CFBundleIdentifier': 'com.nequamy.wpm-widget',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'LSUIElement': True,  # This makes it a menubar-only app (no dock icon)
    },
    'packages': ['rumps', 'pynput', 'matplotlib', 'scipy', 'seaborn', 'sqlite3'],
    'includes': ['wpm_widget'],
    'excludes': ['tkinter'],  # Exclude tkinter to reduce bundle size
    'resources': [],
    'optimize': 2,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)