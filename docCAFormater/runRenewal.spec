# -*- mode: python -*-
# hiddenimports=['cython', 'sklearn', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils', 'openpyxl', 'lexrankr', 'pymysql'],
block_cipher = None

a = Analysis(['C:\\Users\\HANRIM\\PycharmProjects\\docBeFormater\\newParser.py'],
             pathex=['C:\\Users\\HANRIM\\PycharmProjects\\docBeFormater'],
             binaries=None,
             datas=[('C:\\Users\\HANRIM\\PycharmProjects\\docBeFormater\\main_window5.ui', 'main_window5.ui'),
                    ('C:\\Users\\HANRIM\\PycharmProjects\\docBeFormater\\main_icon.ico', 'main_icon.ico'),
                    ('C:\\Users\\HANRIM\\PycharmProjects\\docBeFormater\\icon.png', 'icon.png')],
             hiddenimports=['pkg_resources.py2_warn', 'pymysql', 'openpyxl'],
             hookspath=[],
             excludes=['torch', 'tensorflow', 'keras', 'selenium', 'pandas'],
             runtime_hooks=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='DOCFormatter_v1.5',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='C:\\Users\\HANRIM\\PycharmProjects\\docBeFormater\\main_icon.ico')
