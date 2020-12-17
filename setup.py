from distutils.core import setup
setup(
  name = 'linear-spider',
  packages = ['linearspider'],
  version = '0.1.3',
  license='MIT',
  description = 'Linear spider checks website, searching error pages (e.g. http 500) and reports slow loading pages.',
  author = 'Piotr Wasilewski',
  author_email = 'piotr@wasilewski.net.pl',
  url = 'https://github.com/ardin/linear-spider',
  download_url = 'https://github.com/ardin/linear-spider/archive/0.1.3.tar.gz',
  keywords = ['spider', 'test page', 'speed test'],
  install_requires=[
          'validators',
          'requests',
          'bs4',
      ],
  classifiers=[  # Optional
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    # 'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish
    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  scripts=['bin/linear-spider']
)
