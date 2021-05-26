# -*- mode: python -*-

block_cipher = None

def get_pandas_path():
    import pandas
    pandas_path = pandas.__path__[0]
    return pandas_path

a = Analysis(['MLearner_auto.py'],
             pathex=['D:\\workspace\\scikitlearn'],
             binaries=[],
             datas=[('C:\\Users\\TestEnC\\Anaconda3\\Lib\\site-packages\\konlpy\\', '.\\konlpy'),('C:\\Users\\TestEnC\\Anaconda3\\Lib\\site-packages\\konlpy\\java\\','.\\konlpy\\java'),
                    ('C:\\Users\\TestEnC\\Anaconda3\\Lib\\site-packages\\konlpy\\data\\tagset\\*', '.\\konlpy\\data\\tagset')],
             hiddenimports=['cython', 'sklearn', 'sklearn.tree', 'sklearn.ensemble', 'sklearn.pipeline', 'sklearn.feature_extraction', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils', 'sklearn.utils._cython_blas', 'pickle', 'joblib'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['torch', 'tensorflow', 'keras', 'selenium'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

dict_tree = Tree(get_pandas_path(), prefix='pandas', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'pandas' not in x[0], a.binaries)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Learner_auto_v1.1',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
