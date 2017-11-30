from setuptools import setup

setup(
    name='pccli',
    version='0.3',
    py_modules=['pccli'],
    install_requires=[
        'Click',
        'boto3',
        'pathlib',
        'awscli',
    ],
    entry_points='''
    [console_scripts]
    pccli=pccli:cli
    ''',
)
