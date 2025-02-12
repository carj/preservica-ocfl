# preserva-ocfl

## Create a Preservica repository as a local OCFL storage structure

This library provides a Python module which will create a local OCFL storage structure from a Preservica repository.
Content is exported from Preservica using the API and saved locally in a OCFL compliant structure.

This Oxford Common File Layout (OCFL) specification describes an application-independent approach to the storage of digital information in a structured, transparent, and predictable manner. It is designed to promote long-term object management best practices within digital repositories.

https://ocfl.io/

Specifically, the benefits of the OCFL include:

* Completeness, so that a repository can be rebuilt from the files it stores
* Parsability, both by humans and machines, to ensure content can be understood in the absence of original software
* Robustness against errors, corruption, and migration between storage technologies
* Versioning, so repositories can make changes to objects allowing their history to persist
* Storage diversity, to ensure content can be stored on diverse storage infrastructures including conventional filesystems and cloud object stores

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/carj/preserva-ocfl

## Support 

preserva-ocfl is 3rd party open source client and is not affiliated or supported by Preservica Ltd.
There is no support for use of the library by Preservica Ltd.
Bug reports can be raised directly on GitHub.

Users of preserva-ocfl should make sure they are licensed to use the Preservica REST APIs. 

## License

The package is available as open source under the terms of the Apache License 2.0

## Installation

preserva-ocfl is available from the Python Package Index (PyPI)

https://pypi.org/project/preserva-ocfl/

To install preserva-ocfl, simply run this simple command in your terminal of choice:

    $ pip install preserva-ocfl


