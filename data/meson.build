###
###  GResource schema
###
gnome.compile_resources('mpvQC',
  'mpvQC.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: DIR_PKGDATA,
)

###
###  Desktop file
###
desktop_file = i18n.merge_file(
  input: 'com.github.mpvqc.mpvQC.desktop',
  output: 'com.github.mpvqc.mpvQC.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

###
###  Desktop file validation
###
desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

###
###  AppStream file
###
appstream_file = i18n.merge_file(
  input: 'com.github.mpvqc.mpvQC.appdata.xml',
  output: 'com.github.mpvqc.mpvQC.appdata.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

###
###  AppStream file validation
###
appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

###
###  Schema file
###
install_data('com.github.mpvqc.mpvQC.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

###
###  Schema file validation
###
compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

###
###  Icon file
###
install_data(
    'com.github.mpvqc.mpvQC.svg',
    install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'icons', 'hicolor', 'scalable', 'apps'),
    rename: '@0@.svg'.format('com.github.mpvqc.mpvQC')
)
