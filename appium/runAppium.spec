# -*- mode: python -*-

block_cipher = None

def get_pandas_path():
    import pandas
    pandas_path = pandas.__path__[0]
    return pandas_path

a = Analysis(['appiumRun.py'],
             pathex=['C:\\Users\\TestEnC\\Anaconda3\\workspace'],
             binaries=[],
             datas=[('C:\\Users\\TestEnC\\Anaconda3\\Lib\\site-packages\\appium\\*', '.\\appium'),
             ('C:\\Users\\TestEnC\\Anaconda3\\Lib\\site-packages\\Appium_Python_Client-0.44.dist-info\\*', '.\\Appium_Python_Client-0.44.dist-info')],
             hiddenimports=['openpyxl', 'urllib3', 'appium', 'cv2', 'selenium'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

ui_file =  [('main_appium.ui', 'C:\\Users\\TestEnC\\Anaconda3\\workspace\\main_appium.ui', 'DATA')]
icon_file = [('main_icon.ico', 'C:\\Users\\TestEnC\\Anaconda3\\workspace\\main_icon.ico', 'DATA')]
icon_file_2 = [('icon.png', 'C:\\Users\\TestEnC\\Anaconda3\\workspace\\icon.png', 'DATA')]

dict_tree = Tree(get_pandas_path(), prefix='pandas', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'pandas' not in x[0], a.binaries)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='AppiumRunner_v1.3',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='C:\\Users\\TestEnC\\Anaconda3\\workspace\\main_icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas + ui_file,
               a.datas + icon_file,
               a.datas + icon_file_2,
               strip=None,
               upx=True,
               name='AppiumRunner_v1.3')
