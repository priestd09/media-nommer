"""
Classes in this module serve as a basis for Nommers. This should be thought
of as a protocol or a foundation to assist in maintaining a consistent API
between Nommers.
"""
import os
import tempfile
from media_nommer.core.storage_backends import get_storage_backend_for_uri

class BaseNommer(object):
    """
    This is a base class that can be sub-classed by each Nommer to serve
    as a foundation. Required methods raise a NotImplemented exception
    by default, unless overridden by child classes.
    """
    def __init__(self, job):
        self.job = job

    def onomnom(self):
        """
        Start nomming. If you're going to override this, make sure to follow
        the same basic job state updating flow if possible.
        """
        self._start_encoding()

    def _start_encoding(self):
        """
        Call your encoder here, do work. Make sure to update job state as
        it progresses, if you can.
        
        Needs to set one of the two job states: FINISHED, ERROR
        """
        raise NotImplemented

    def download_source_file(self):
        """
        Download the source file to a temporary file.
        """
        self.job.set_job_state('DOWNLOADING')

        file_uri = self.job.source_path
        print "ATTEMPTING TO DOWNLOAD", file_uri
        storage = get_storage_backend_for_uri(file_uri)
        fobj = tempfile.NamedTemporaryFile(mode='w+b', delete=True)
        storage.download_file(file_uri, fobj)
        # flush and fsync to force writing to the file object. Doesn't always
        # happen otherwise.
        fobj.flush()
        os.fsync(fobj.fileno())
        print "DOWNLOADED", fobj, fobj.name
        # As soon as this fobj is garbage collected, it is closed(). Be
        # careful to continue its existence if you need it.
        return fobj

    def upload_to_destination(self, fobj):
        """
        Upload the output file to the destination specified by the user.
        """
        self.job.set_job_state('UPLOADING')
        file_uri = self.job.dest_path
        print "ATTEMPTING TO UPLOAD TO", file_uri, fobj
        storage = get_storage_backend_for_uri(file_uri)
        storage.upload_file(file_uri, fobj)
        print "UPLOADED!"