"""
preserva-ocfl  module definition

A python module for creating a local OCFL storage root from a Preservica repository

author:     James Carr
licence:    Apache License 2.0

"""
import argparse
import os.path
import pathlib
import sys
import uuid
import zipfile
from io import BytesIO
from ocflcore import *
from datetime import datetime, timezone

from ocflcore.persistence.transaction import Transaction
from pyPreservica import *

SPEC_FILE: str = "https://ocfl.io/1.1/spec/"
ROOT_NAMASTE: str = "0=ocfl_1.1"
OBJECT_NAMASTE: str = "0=ocfl_object_1.1"
ROOT_LAYOUT: str = "ocfl_layout.json"

class PreservicaRepository(OCFLRepository):

    def exists(self, obj_id):
        o = OCFLObject(obj_id)
        with Transaction(self, o) as trans:
            object_path = os.path.join(trans.repository.storage._root, trans.object_path)
            if os.path.exists(object_path):
                ver_file: str =  os.path.join(object_path, OBJECT_NAMASTE)
                inventory_file: str = os.path.join(object_path,"inventory.json")
                if os.path.isfile(ver_file) and os.path.exists(inventory_file):
                    return True
        return False



class PreservicaVersion(OCFLVersion):

    def __init__(self, creation_time, username: str, system: str, message: str = "Initial Export"):
        """Constructor."""
        super().__init__(creation_time)
        self._user = {"address": username, "name": system}
        self._message = message


class TruncatedNTripleUuid(StorageLayout):
    """
    Truncated n-tuple Tree use 2 hex digits for each level of the first (32 bits) part of the uuid
    """

    description = "Object structure is truncated n-tuple Tree which use 2 hex digits for each level of the first (32 bits) part of the Preservica uuid"
    extension = ""

    def path_for(self, obj):
        object_id = uuid.UUID(obj.id)
        dir_paths = str(hex(object_id.fields[0])).replace("0x", "")
        object_path = "."
        for i in range(0, 7, 2):
            object_path = os.path.join(object_path, dir_paths[i:i + 2])
        object_path = os.path.join(object_path, obj.id)

        return object_path


def populate(repository: PreservicaRepository, folder: Folder, entity: EntityAPI, search: ContentAPI):

    filter_values = {"xip.document_type": "IO"}
    if folder is not None:
        filter_values["xip.parent_hierarchy"] = folder.reference
    search.callback = search.ReportProgressCallBack()
    for hit in search.search_index_filter_list(query="%", filter_values=filter_values):
        reference: str = hit['xip.reference']

        # Does the object exist in the OCFL storage root
        if repository.exists(reference):
            print(f"Object {reference} already exists in the OCFL storage root")
            continue

        # Export the Asset
        asset: Asset = entity.asset(reference)
        opex_package = entity.export_opex_sync(asset, IncludeContent="Content", IncludeMetadata="Metadata",
                                               IncludedGenerations="All", IncludeParentHierarchy="false")

        # Create the OCFL object
        ocfl_version = PreservicaVersion(datetime.now(timezone.utc), entity.username, f"{entity.server} ({entity.tenant})")

        ocfl_object = OCFLObject(reference)

        # Unzip the OPEX package into the correct folders
        with zipfile.ZipFile(opex_package, "r") as zip_ref:
            for f in zip_ref.filelist:
                if f.filename.endswith(".pax.zip.opex"):
                    ocfl_file: StreamDigest = StreamDigest(BytesIO(zip_ref.read(f)))
                    ocfl_version.files.add(f.filename, ocfl_file.stream, ocfl_file.digest)
                elif f.filename.endswith("pax.zip"):
                    zfiledata = BytesIO(zip_ref.read(f.filename))
                    with zipfile.ZipFile(zfiledata, "r") as zip_pax_ref:
                        for ff in zip_pax_ref.filelist:
                            if ff.is_dir() is False:
                                ocfl_file: StreamDigest = StreamDigest(BytesIO(zip_pax_ref.read(ff)))
                                ocfl_version.files.add(ff.filename, ocfl_file.stream, ocfl_file.digest)
                else:
                    sys.exit("Unexpected file in OPEX package")

        ocfl_object.versions.append(ocfl_version)
        repository.add(ocfl_object)
        os.remove(opex_package)


def init(args):
    """
    Create the OCFL storage root

    :param args: The command line arguments
    :return:
    """
    cmd_line = vars(args)
    collection = cmd_line['collection']

    username = cmd_line['username']
    password = cmd_line['password']
    server = cmd_line['server']

    if (username is not None) and (password is not None) and (server is not None):
        print(f"Using credentials from command line")
        entity: EntityAPI = EntityAPI(username=username, password=password, server=server)
        search: ContentAPI = ContentAPI(username=username, password=password, server=server)
    else:
        entity: EntityAPI = EntityAPI()
        search: ContentAPI = ContentAPI()

    folder: Folder = None
    if collection is not None:
        folder = entity.folder(collection)
        print(f"Populating OCFL storage root with objects from {folder.title}")
    else:
        print(f"Populating OCFL storage root with objects from all collections")

    root = StorageRoot(TruncatedNTripleUuid())

    storage_root = cmd_line['storage_root']
    print(f"Creating OCFL storage root at {storage_root}")

    storage = FileSystemStorage(storage_root)
    workspace_storage = FileSystemStorage(f"{storage_root}_WRKSP")
    repository: PreservicaRepository = PreservicaRepository(root, storage, workspace_storage=workspace_storage)
    repository.initialize()
    if os.path.exists(f"{storage_root}/ocfl_1.1.html") is False:
        r = requests.get("https://ocfl.io/1.1/spec/")
        if r.status_code == 200:
            with open(f"{storage_root}/ocfl_1.1.html", "wt", encoding="utf-8") as f:
                f.write(r.text)


    populate(repository, folder, entity, search)


def main():
    """
    Entry point for the module when run as python -m preserva-ocfl

    Sets up the command line arguments and starts either the ingest or validation

    :return: 0
    """
    cmd_parser = argparse.ArgumentParser(
        prog='preserva-ocfl',
        description='Create a local OCFL storage root from a Preservica repository',
        epilog='')

    cmd_parser.add_argument("-r", "--storage-root", type=pathlib.Path, help="The OCFL Storage Root", required=True)
    cmd_parser.add_argument("-c", "--collection", type=str, help="The Preservica parent collection uuid",
                            required=False)

    cmd_parser.add_argument("-u", "--username", type=str,
                            help="Your Preservica username if not using credentials.properties", required=False)
    cmd_parser.add_argument("-p", "--password", type=str,
                            help="Your Preservica password if not using credentials.properties", required=False)
    cmd_parser.add_argument("-s", "--server", type=str,
                            help="Your Preservica server domain name if not using credentials.properties",
                            required=False)

    args = cmd_parser.parse_args()

    init(args)


if __name__ == "__main__":
    sys.exit(main())
