# canvas_bulk_download.py
A script for downloading almost all files from all of your Canvas courses (past and present). If you are interested in downloading all the material you've submitted to your Canvas courses, you can do so very easily by clicking the "Download Submissions" button on the right side of your Canvas settings page. <ins>I recommend doing this regardless of whether or not you run this repository's script!</ins>

## Prerequisites:
1. A python environment that has the libraries `canvasapi`, `colorama`, and `tqdm` installed. Once you install Python 3 (and activate your virtual environment if applicable), you can run `pip install canvasapi colorama tqdm` to install the necessary packages.
2. A Canvas API token. You can get one by visiting your Canvas settings page and clicking "+ New Access Token" under the "Approved Integrations" section. Copy the token to your clipboard, then open `canvas_bulk_download.py` and paste the token between the double quotes in the line `CANVAS_TOKEN = ""` (line 19).

    **Warning!** Like all API tokens, keep this secret. If you paste your Canvas API token elsewhere, someone could end up accessing your Canvas account!

## Usage:
1. Paste your institutional Canvas URL (e.g. https://canvas.ucsd.edu for UCSD) inside the double quotes in the line `API_URL = ""` (line 23).
2. In the command line, activate your Python environment.
3. Run `python canvas_bulk_download.py`. By default, all files from all courses you have access to will be downloaded to a subdirectory called `canvas_downloads`. From there, downloads are organized into courses and further into modules. This script does not download any part of Canvas quizzes, so if you have the ability to view your previous quizzes and wish to download them you'll have to modify the script.
