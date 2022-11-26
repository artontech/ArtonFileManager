''' ffmpeg wrapper '''
import os
import subprocess

from backend import config

options = config.get_options()

def stream2thumb(data, thumb_type="webp"):
    ''' video sream to thumb '''
    command = [
        os.path.join(options.ffmpeg_path, "ffmpeg"),
        "-i", "pipe:0",
        "-f", thumb_type,
        "-loglevel", "error",
        "-threads", str(os.cpu_count()),
        "-s", "100x100",
        "-y",
        "pipe:1"
    ]
    proc = subprocess.run(
        command,
        check=False,
        input=data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return proc.stdout, proc.stderr
 