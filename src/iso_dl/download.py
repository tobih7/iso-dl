from cgi import parse_header
from os import unlink
from urllib.parse import urlsplit
from urllib.request import urlopen, urlretrieve
import progressbar


def download_torrent(url: str):
    """
    Download the ISO using a torrent file.
    """

    try:
        urlretrieve(url, filename=(filename := get_filename_from_url(url)))
    except BaseException as e:
        unlink(filename)
        raise

    print(f"Torrent file saved to: ./{filename}")


def download_url(url: str):
    """
    Download the ISO using a direct URL.
    """
    filename = get_filename_from_url(url)

    print(f"Writing to: ./{filename}\n")
    try:
        urlretrieve(url, filename=filename, reporthook=ProgressBar())
    except BaseException as e:
        unlink(filename)
        raise


def get_filename_from_url(url: str) -> str:
    if content_disposition := urlopen(url).getheader("Content-Disposition"):
        return parse_header(content_disposition)[1]["filename"]
    else:
        return urlsplit(url).path.split("/")[-1]


class ProgressBar:
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar = progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()
