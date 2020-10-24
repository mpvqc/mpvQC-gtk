project(
    'mpvQC',
    version: 'v1.0',
    meson_version: '>= 0.50.0',
)

###
###  Imports
###
python = import('python')
gnome = import('gnome')
i18n = import('i18n')

###
###  Project configuration
###
APP_ID = 'com.github.mpvqc.mpvQC'
APP_NAME = meson.project_name()
APP_URL = 'https://github.com/mpvqc/mpvQC-gtk'
APP_VERSION = meson.project_version()
DIR_LOCALE = join_paths(get_option('prefix'), get_option('localedir'))
DIR_PKGDATA = join_paths(get_option('prefix'), get_option('datadir'), APP_NAME)
DIR_MODULE = join_paths(DIR_PKGDATA, 'mpvQC')
PYTHON_INSTALLATION = python.find_installation()
PYTHON_PATH = PYTHON_INSTALLATION.path()
PYTHON_DIR = join_paths(get_option('prefix'), PYTHON_INSTALLATION.get_path('purelib'))

git = find_program('git', required : false)
if git.found()
    VCS_HASH = run_command('git', 'rev-parse', '--short', 'HEAD').stdout().strip()
    VCS_TAG = run_command('git', 'tag').stdout().strip()
else
    VCS_HASH = ''
    VCS_TAG = ''
endif

conf = configuration_data()
conf.set('APP_ID', APP_ID)
conf.set('APP_NAME', APP_NAME)
conf.set('APP_URL', APP_URL)
conf.set('APP_VERSION', APP_VERSION)
conf.set('PYTHON_PATH', PYTHON_PATH)
conf.set('DIR_LOCALE', DIR_LOCALE)
conf.set('DIR_PKGDATA', DIR_PKGDATA)
conf.set('VCS_TAG', VCS_TAG)
conf.set('VCS_HASH', VCS_HASH)

###
###  mpvQC.in -> mpvQC
###
configure_file(
  input: 'mpvQC.in',
  output: 'mpvQC',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

###
###  Subdirectories
###
subdir('data')
subdir('po')
install_subdir('mpvqc', install_dir: DIR_PKGDATA)

###
###  Post install
###
meson.add_install_script('build-aux/meson/postinstall.py')
