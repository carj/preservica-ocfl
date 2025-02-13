# preserva-ocfl

## Replicate a Preservica repository as a local OCFL storage structure

This library provides a Python module which will create a local OCFL storage structure from a Preservica repository.
Content is exported from Preservica using the API and saved locally in a OCFL compliant structure.

This Oxford Common File Layout (OCFL) specification describes an application-independent approach to the 
storage of digital information in a structured, transparent, and predictable manner. 
It is designed to promote long-term object management best practices within digital repositories.

https://ocfl.io/

This project uses the OCFL Core https://github.com/inveniosoftware/ocflcore library to create the OCFL inventory 
metadata.

## Limitations

The preserva-ocfl module creates OCFL specification 1.1 file structures. It does not support the OCFL 1.0 specification.

The library creates OCFL objects from each Preservica Asset. It currently does not look for modifications in Preservica
to create new OCFL versions. Each Asset in Preservica is mapped to a v1 OCFL object. 

If OCFL objects already exist for a Preservica Asset then they will be ignored. 




## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/carj/preserva-ocfl

## Support 

preserva-ocfl is 3rd party open source library and is not affiliated or supported by Preservica Ltd.
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


