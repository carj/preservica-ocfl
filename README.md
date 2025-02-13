# preservica-ocfl

This library provides a Python module which will create a local Oxford Common File Layout (OCFL) Specification storage 
structure from a Preservica repository. 
Content is exported from Preservica as OPEX packages using the API and saved locally in a OCFL compliant structure.

## Preservica repository as a local OCFL storage structure

This Oxford Common File Layout (OCFL) specification describes an application-independent approach to the 
storage of digital information in a structured, transparent, and predictable manner. 
It is designed to promote long-term object management best practices within digital repositories.

https://ocfl.io/

This project uses the OCFL Core https://github.com/inveniosoftware/ocflcore library to create the OCFL inventory 
metadata.

## Limitations

The preservica-ocfl module creates OCFL specification 1.1 file structures. It does not support the OCFL 1.0 specification.

The library creates OCFL objects from each Preservica Asset. It currently does not look for modifications in Preservica
to create new OCFL versions. Each Asset in Preservica is mapped to a v1 OCFL object. 

If OCFL objects already exist for a Preservica Asset then they will be ignored. 

## OPEX

The information stored within the OCFL object depends on the type of OPEX package exported from Preservica.


## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/carj/preserva-ocfl

## Support 

preservica-ocfl is 3rd party open source library and is not affiliated or supported by Preservica Ltd.
There is no support for use of the library by Preservica Ltd.
Bug reports can be raised directly on GitHub.

Users of preservica-ocfl should make sure they are licensed to use the Preservica REST APIs. 

## License

The package is available as open source under the terms of the Apache License 2.0

## Installation

preservica-ocfl is available from the Python Package Index (PyPI)

https://pypi.org/project/preserva-ocfl/

To install preservica-ocfl, simply run this simple command in your terminal of choice:

    $ pip install preservica-ocfl



    $ python -m preservica-ocfl -r STORAGE_ROOT -c a7ad52e3-2cb3-4cb5-af2a-3ab08829a2a8
    
    ```
    usage: preservica-ocfl [-h] -r STORAGE_ROOT [-c COLLECTION] [-t THREADS] [-d DIRECTORY_DEPTH] [--parent-folders PARENT_FOLDERS] [-u USERNAME] [-p PASSWORD] [-s SERVER]

    Create a local OCFL storage root from a Preservica repository
    
    options:
      -h, --help            show this help message and exit
      -r STORAGE_ROOT, --storage-root STORAGE_ROOT
                            The OCFL Storage Root
      -c COLLECTION, --collection COLLECTION
                            The Preservica parent collection uuid, ignore to process the entire repository
      -t THREADS, --threads THREADS
                            The number of export threads, defaults to 1
      -d DIRECTORY_DEPTH, --directory-depth DIRECTORY_DEPTH
                            The number of directory components below the storage root, 
                            defaults to 2 Can be any of (1, 2, 3, 4)
      --parent-folders PARENT_FOLDERS
                            The OCFL object includes Preservica Parent Hierarchy information. 
                            This corresponding flag should also be set on the OPEX export workflow
      -u USERNAME, --username USERNAME
                            Your Preservica username if not using credentials.properties
      -p PASSWORD, --password PASSWORD
                            Your Preservica password if not using credentials.properties
      -s SERVER, --server SERVER
                            Your Preservica server domain name if not using credentials.properties
    
    Preservica requires an active Export workflow, which be configured to include "Content" and "Metadata"

    
    
    
    ```