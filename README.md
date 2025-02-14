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

The export of a large repository could be potentially slow, as every Asset needs to be exported and downloaded. 
The performance can be improved by running multiple export workflows in parallel 

## OPEX

The information stored within the OCFL object depends on the type of OPEX package exported from Preservica.


## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/carj/preservica-ocfl

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



## Usage

The preserva-ocfl module uses the Preservica API to export Assets as OPEX packages. The OPEX packages are then 
downloaded and the OCFL objects are created from the OPEX packages.

The only required parameter is the storage root location for the OCFL objects. 
The storage root is the root directory for the OCFL see https://ocfl.io/1.1/spec/#storage-root

The module requires the Preservica parent collection UUID to be specified. If no collection is specified then the entire
repository is exported.

     $ python -m preserva-ocfl --storage-root "storage_root"  --collection 10f8d7aa-d477-413b-8d52-d2a5632b8e13

The initial OCFL storage root will be created with the following structure:

    [storage_root]
        ├── 0=ocfl_1.1
        ├── ocfl_1.1.html        
        └── ocfl_layout.json    


The --directory-depth parameter can be used to control the number of directories below the storage root before the
objects are stored. The default is 2.  The directory structure is based on the UUID of the Preservica Asset. 
It uses 2 hex digits from the Preservica Asset UUID for each level.

Using 2 levels distributes each OCFL object into one of 65536 (256*256) different folders. 
This means that the export of a Preservica repository with 1 million Assets would result in only around 15 Assets in each folder. 
Preservica uses Version 4 (random) UUIDs.

For example, with depth set to the default 2, the OCFL structure will look like:

    [storage_root]
            ├── 0=ocfl_1.1
            ├── ocfl_1.1.html        
            └── ocfl_layout.json
            └──3b                       <- Level 1
                └──be                   <- Level 2
                    └──3bbe0160-ad3d-48db-8800-632db07249b6
                            └──0=ocfl_object_1.1
                            └──inventory.json
                            └──inventory.json.SHA512
                            └──v1
                                └──inventory.json
                                └──inventory.json.SHA512
                                └──content
                                        └──OPEX Package...   


    
                                
The number of concurrent export workflows can be controlled using the --threads parameter. The default is 2.


        
