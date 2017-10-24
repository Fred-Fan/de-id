from setuptools import setup

setup(
    name='philter',    # This is the name of your PyPI-package.
    version='0.1.3',  # Update the version number for new releases
    packages=['philter'],
    #include_package_data=True,
    package_data={'philter': ['whitelist.pkl'],
    },
    entry_points={
        'console_scripts': [
            'philter = philter.philter:main',
            'philter-annotation = philter.philter_annotator:main',
            'philter-eval = philter.philter_eval:main']
            },
        # The name of your scipt, and also the command you'll be using for calling it
    zip_safe = False,
    install_requires=[
          'nltk',
          'spacy'
      ],
    author='UCSF-ICHS',
    author_email='beaunorgeot@gmail.com'
)
