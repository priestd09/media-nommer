import os
import tempfile
import subprocess
from media_nommer.core.nommers.base_nommer import BaseNommer

class EC2FFmpegNommer(BaseNommer):
    def _start_encoding(self):
        """
        Gets the show on the road.
        """
        print "STARTING TO NOM"
        fobj = self.download_source_file()

        # Encode the file. The return value is a tempfile with the output.
        out_fobj = self.__run_ffmpeg(fobj)
        if not out_fobj:
            # Failure! We're going nowhere.
            fobj.close()
            return False

        # Upload the encoding output file to its final destination.
        self.upload_to_destination(out_fobj)

        # TODO: Check to see if they wanted to delete or copy the original 
        # file after a successful run.

        self.job.set_job_state('FINISHED')
        print "FINE"
        fobj.close()
        out_fobj.close()
        return True

    def __append_inout_opts_to_cmd_list(self, option_dict, cmd_list):
        for key, val in option_dict.items():
            cmd_list.append('-%s' % key)
            cmd_list.append(val)

    def __run_ffmpeg(self, fobj):
        """
        Fire up ffmpeg and toss the results into a temporary file.
        """
        path = fobj.name
        out_fobj = tempfile.NamedTemporaryFile(mode='w+b', delete=True)
        print "OUTPUT", out_fobj.name
        print "ARGS", self.job.job_options

        ffmpeg_cmd = ['ffmpeg', '-y', '-i', path]

        if self.job.job_options.has_key('infile_options'):
            infile_opts = self.job.job_options['infile_options']
            self.__append_inout_opts_to_cmd_list(infile_opts, ffmpeg_cmd)

        if self.job.job_options.has_key('outfile_options'):
            outfile_opts = self.job.job_options['outfile_options']
            self.__append_inout_opts_to_cmd_list(outfile_opts, ffmpeg_cmd)

        ffmpeg_cmd.append(out_fobj.name)

        print "COMMAND TO RUN", ffmpeg_cmd

        process = subprocess.Popen(ffmpeg_cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        cmd_output = process.communicate()

        print "RETURN CODE", process.returncode, type(process.returncode)
        error_happened = process.returncode != 0

        if not error_happened:
            # No errors, return the file object for uploading.
            out_fobj.seek(0)
            return out_fobj
        else:
            # Error found, return nothing so the nommer can die.
            print "!!! ERROR, SETTING ERROR STATE WITH OUTPUT"
            print "STDOUT", cmd_output[0]
            print "STDERROR", cmd_output[1]
            self.job.set_job_state('ERROR', details=cmd_output[1])
            return None