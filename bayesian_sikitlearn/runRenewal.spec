# -*- mode: python -*-
# hiddenimports=['cython', 'sklearn', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils', 'openpyxl', 'lexrankr', 'pymysql', 'PyQt5','joblib', 'pickle'],
block_cipher = None

def get_pandas_path():
    import pandas
    pandas_path = pandas.__path__[0]
    return pandas_path

a = Analysis(['newParser.py'],
             pathex=['C:\\Users\\HANRIM\\PycharmProjects\\bayesian_sikitlearn\\'],
             binaries=[],
             datas=[('C:\\Users\\HANRIM\\Anaconda3\\Lib\\site-packages\\konlpy\\', '.\\konlpy'),('C:\\Users\\HANRIM\\Anaconda3\\Lib\\site-packages\\konlpy\\java\\','.\\konlpy\\java'),
                    ('C:\\Users\\HANRIM\\Anaconda3\\Lib\\site-packages\\konlpy\\data\\tagset\\*', '.\\konlpy\\data\\tagset'),
                    ('C:\\Users\\HANRIM\\Anaconda3\\Lib\\site-packages\\lexrankr\\','.\\lexrankr')],
             hiddenimports=['cython', 'sklearn', 'sklearn.tree', 'sklearn.ensemble', 'sklearn.pipeline', 'sklearn.feature_extraction', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree',
             'sklearn.tree._utils', 'sklearn.utils._cython_blas', 'openpyxl', 'lexrankr', 'pymysql', 'PyQt5','joblib', 'pickle'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['torch', 'tensorflow', 'keras', 'selenium'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

ui_file =  [('main_window5.ui', 'C:\\Users\\HANRIM\\PycharmProjects\\bayesian_sikitlearn\\main_window5.ui', 'DATA')]
icon_file = [('main_icon.ico', 'C:\\Users\\HANRIM\\PycharmProjects\\bayesian_sikitlearn\\main_icon.ico', 'DATA')]
icon_file_2 = [('icon.png', 'C:\\Users\\HANRIM\\PycharmProjects\\bayesian_sikitlearn\\icon.png', 'DATA')]


dict_tree = Tree(get_pandas_path(), prefix='pandas', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'pandas' not in x[0], a.binaries)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='VOCParser_v4.3',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='C:\\Users\\HANRIM\\PycharmProjects\\bayesian_sikitlearn\\main_icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas + ui_file,
               a.datas + icon_file,
               a.datas + icon_file_2,
               # a.datas + learner,
               # a.datas + sample,
               strip=None,
               upx=True,
               name='VOCParser_v4.3')
