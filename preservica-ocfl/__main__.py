"""
preservica-ocfl  module definition

A python module for creating a local OCFL storage root from a Preservica repository

author:     James Carr
licence:    Apache License 2.0

"""
import argparse
import os.path
import pathlib
import queue
import sys
import uuid
import logging
import zipfile
from concurrent.futures import ThreadPoolExecutor, Future
from io import BytesIO
from typing import Generator

from ocflcore import *
from datetime import datetime, timezone

from ocflcore.persistence.transaction import Transaction
from pyPreservica import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SPEC_FILE: str = "https://ocfl.io/1.1/spec/"
ROOT_NAMASTE: str = "0=ocfl_1.1"
OBJECT_NAMASTE: str = "0=ocfl_object_1.1"
ROOT_LAYOUT: str = "ocfl_layout.json"


class ThreadPoolExecutorWithQueueSizeLimit(ThreadPoolExecutor):
    """
        Extend the ThreadPoolExecutor to add a work queue size limit
        This stops the queue from growing too large and causing memory issues

    """

    def __init__(self, maxsize=50, *args, **kwargs):
        super(ThreadPoolExecutorWithQueueSizeLimit, self).__init__(*args, **kwargs)
        self._work_queue = queue.Queue(maxsize=maxsize)


class PreservicaRoot(StorageRoot):
    @property
    def human_text(self):
        """Human readable text of the OCFL spec."""
        # See 4.2
        r = requests.get("https://ocfl.io/1.1/spec/")
        if r.status_code == 200:
            return r.content
        return None

    @property
    def human_text_filename(self):
        """Filename of the OCFL spec."""
        # See 4.2
        return f"ocfl_{self.version}.html"


class PreservicaRepository(OCFLRepository):
    """
        Extend the OCFLRepository to add a method to check if an object exists in the storage root
    """

    def initialize(self):
        """Initialize OCFL repository."""
        # Write root conformace declaration - See 4.2
        self.storage.write(self.root.namaste, BytesIO(f"ocfl_{self.root.version}\n".encode()))
        # Write optional human readable text - See 4.1
        if self.root.human_text is not None:
            self.storage.write(
                self.root.human_text_filename, BytesIO(self.root.human_text)
            )
        # Write optional layout file - See 4.1
        layout_json = self.root.layout.json_bytes
        if layout_json is not None:
            self.storage.write("ocfl_layout.json", BytesIO(layout_json))

    def exists(self, obj_id):
        o = OCFLObject(obj_id)
        with Transaction(self, o) as trans:
            object_path = os.path.join(trans.repository.storage._root, trans.object_path)
            if os.path.exists(object_path):
                ver_file: str = os.path.join(object_path, OBJECT_NAMASTE)
                inventory_file: str = os.path.join(object_path, "inventory.json")
                if os.path.isfile(ver_file) and os.path.exists(inventory_file):
                    return True
        return False

    def list(self) -> Generator:
        """List objects in an OCFL object root."""
        root_path = Path(self.storage._root)
        pattern = "/".join(["*"] * (self.root.layout.parts + 1))
        for o in root_path.glob(pattern):
            if o.is_dir():
                if os.path.exists(os.path.join(o, f"0=ocfl_object_{self.root.version}")):
                    yield os.path.basename(o)


class PreservicaVersion(OCFLVersion):
    """
        Extend the OCFLVersion to add the user and system metadata

        Use the Preservica username for the OCFL user address
    """

    def __init__(self, creation_time, username: str, system: str, message: str = "Initial Export"):
        """Constructor."""
        super().__init__(creation_time)
        self._user = {"address": username, "name": system}
        self._message = message


class TruncatedNTripleUuid(StorageLayout):
    """
    Truncated n-tuple Tree use 2 hex digits for each level of the first (32 bits) part of the uuid

    """

    def __init__(self, parts: int = 1):
        self.parts = parts
        self.description = f"""Object structure is a truncated n-tuple Tree which use {self.parts} hex digits for each 
                level of the first (32 bits) part of the Preservica uuid"""

    extension = ""

    def parts(self):
        return self.parts

    def path_for(self, obj):
        object_id = uuid.UUID(obj.id)
        dir_paths = str(hex(object_id.fields[0])).replace("0x", "")
        object_path = "."
        for i in range(0, (self.parts * 2) - 1, 2):
            object_path = os.path.join(object_path, dir_paths[i:i + 2])
        object_path = os.path.join(object_path, obj.id)

        return object_path


def export_opex(entity: EntityAPI, reference: str, repository: PreservicaRepository, parent_folders: bool) -> str:
    """
    Export the asset as an OPEX package

    :param entity:              The Preservica EntityAPI object
    :param reference:           The Preservica Asset object reference
    :param repository:          The OCFL Repository object
    :param parent_folders:      Include the parent folders in the OCFL object

    :return: The stored OCFL object id
    """
    # Export the Asset block waiting for the opex package to be downloaded.
    asset: Asset = entity.asset(reference)
    opex_package = entity.export_opex_sync(asset, IncludeContent="Content", IncludeMetadata="Metadata",
                                           IncludedGenerations="All", IncludeParentHierarchy=str(parent_folders))

    # Create the OCFL object
    ocfl_version = PreservicaVersion(datetime.now(timezone.utc), entity.username, f"{entity.server} ({entity.tenant})")

    # Unzip the OPEX package into the correct folders
    with zipfile.ZipFile(opex_package, "r") as zip_ref:

        if parent_folders:
            for ff in zip_ref.filelist:
                if ff.is_dir() is False:
                    ocfl_file: StreamDigest = StreamDigest(BytesIO(zip_ref.read(ff)))
                    ocfl_version.files.add(ff.filename, ocfl_file.stream, ocfl_file.digest)
        else:
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

    ocfl_object = OCFLObject(reference)
    ocfl_object.versions.append(ocfl_version)
    repository.add(ocfl_object)
    os.remove(opex_package)

    return ocfl_object.id


def object_added(future: Future):
    obj_id = future.result()
    logger.info(f"Object {obj_id} added to OCFL storage root")


def populate(repository: PreservicaRepository, folder: Folder, entity: EntityAPI, search: ContentAPI, num_threads: int,
             parent_folders: bool = False):
    """
    Search the repository for Assets and export them as OPEX packages

    """

    filter_values = {"xip.document_type": "IO"}
    if folder is not None:
        filter_values["xip.parent_hierarchy"] = folder.reference

    num_hits: int = search.search_index_filter_hits(query="%", filter_values=filter_values)

    logger.info(f"Found {num_hits} objects to export")

    count: int = 0

    with ThreadPoolExecutorWithQueueSizeLimit(max_workers=num_threads, maxsize=num_threads * 2) as executor:

        for hit in search.search_index_filter_list(query="%", filter_values=filter_values):

            count += 1
            reference: str = hit['xip.reference']

            # Does the object exist in the OCFL storage root
            if repository.exists(reference):
                logger.info(f"Object {reference} already exists in the OCFL storage root. Skipping...")
                continue

            future: Future = executor.submit(export_opex, entity, reference, repository, parent_folders)
            future.add_done_callback(object_added)

            logger.info(f"Processing item {count} of {num_hits}:  Asset {reference}")


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
    if 'include_parent_folders' in cmd_line:
        parent_folders: bool = cmd_line['include_parent_folders']
    else:
        parent_folders: bool = False

    num_threads = int(cmd_line['threads'])

    directory_depth = int(cmd_line['directory_depth'])
    if directory_depth not in [1, 2, 3, 4]:
        directory_depth = 2

    # Limit the number of OPEX export workflows
    if num_threads < 1:
        num_threads = 1
    if num_threads > 8:
        num_threads = 8

    # create the pyPreservica objects
    if (username is not None) and (password is not None) and (server is not None):
        logger.info(f"Using credentials from command line")
        entity: EntityAPI = EntityAPI(username=username, password=password, server=server)
        search: ContentAPI = ContentAPI(username=username, password=password, server=server)
    else:
        entity: EntityAPI = EntityAPI()
        search: ContentAPI = ContentAPI()

    logger.info(entity)

    folder: Folder = None
    if collection is not None:
        folder = entity.folder(collection)
        logger.info(f"Populating OCFL storage root with objects from collection: {folder.title}")
    else:
        logger.info(f"Populating OCFL storage root with objects from all collections")

    root = PreservicaRoot(TruncatedNTripleUuid(directory_depth))

    storage_root = cmd_line['storage_root']
    logger.info(f"Creating OCFL storage root at {storage_root}")

    storage = FileSystemStorage(storage_root)
    workspace_storage = FileSystemStorage(f"{storage_root}_WRKSP")
    repository: PreservicaRepository = PreservicaRepository(root, storage, workspace_storage=workspace_storage)
    repository.initialize()

    populate(repository, folder, entity, search, num_threads, parent_folders)


def main():
    """
    Entry point for the module when run as python -m preserva-ocfl

    Sets up the command line arguments and starts the export process

    :return: None

    """
    cmd_parser = argparse.ArgumentParser(
        prog='preserva-ocfl',
        description='Create a local OCFL storage root from a Preservica repository',
        epilog='Preservica requires an active Preservica Export Workflow, which must be configured to include "Content" and "Metadata"')

    cmd_parser.add_argument("-r", "--storage-root", type=pathlib.Path, help="The OCFL Storage Root",
                            required=True)

    cmd_parser.add_argument("-c", "--collection", type=str,
                            help="The Preservica parent collection uuid, ignore to process the entire repository",
                            required=False)

    cmd_parser.add_argument("-t", "--threads", type=int, help="The number of export threads, defaults to 2",
                            required=False, default=2)

    cmd_parser.add_argument("-d", "--directory-depth", type=int,
                            help="The number of directory components below the storage root, defaults to 2 "
                                 "Can be any of (1, 2, 3, 4)",
                            required=False, default=2)

    cmd_parser.add_argument("--include-parent-folders", type=bool,
                            help="The OCFL object includes Preservica Parent Hierarchy information. "
                                 "This corresponding flag should also be set on the OPEX export workflow ",
                            required=False, default=False)

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
