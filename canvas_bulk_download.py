"""
canvas_bulk_download.py
Purpose: A tiny script for bulk downloading files from all Canvas courses.
Author: ChatGPT-4o with prompting and cleanup by Jake Anderson
Date: June 17, 2024
License: The Unlicense (see LICENSE)
"""

import os
import re
from concurrent.futures import ThreadPoolExecutor

import requests
from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist, Unauthorized
from colorama import Fore, Style, init
from tqdm import tqdm

CANVAS_TOKEN = ""

init(autoreset=True)

API_URL = ""
canvas = Canvas(API_URL, CANVAS_TOKEN)

MAX_THREADS = 2  # Maximum number of threads


def sanitize_filename(name):
    return re.sub(r"[^\w\-_\. ]", "_", name)


def download_file(file_url, file_name, folder_dir, pbar):
    if not file_url.startswith("http"):
        print(Fore.RED + f"Invalid URL: {file_url}")
        pbar.close()
        return

    dest_path = os.path.join(folder_dir, sanitize_filename(file_name))
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        pbar.close()
        print(Fore.GREEN + f"Successfully downloaded: {dest_path}")
    except Exception as e:
        pbar.close()
        print(Fore.RED + f"Failed to download {file_url}: {e}")


def process_files(files, folder_dir):
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for file in files:
            if not file.url:
                print(Fore.RED + f"Skipping file with no URL: {file}")
                continue
            file_size = int(requests.head(file.url).headers.get("content-length", 0))
            pbar = tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                desc=sanitize_filename(file.display_name),
                colour="blue",
                leave=False,
            )
            future = executor.submit(
                download_file, file.url, file.display_name, folder_dir, pbar
            )
            futures.append(future)

        for future in futures:
            future.result()  # Wait for all futures to complete


def download_folder_contents(folder, folder_dir):
    try:
        files = folder.get_files()
        process_files(files, folder_dir)
        subfolders = folder.get_folders()
        for subfolder in subfolders:
            subfolder_dir = os.path.join(folder_dir, sanitize_filename(subfolder.name))
            os.makedirs(subfolder_dir, exist_ok=True)
            download_folder_contents(subfolder, subfolder_dir)
    except Unauthorized as e:
        print(Fore.RED + f"Unauthorized access to folder {folder.id}: {e}")


def download_course_files(course_id):
    try:
        course = canvas.get_course(course_id)
        print(Fore.YELLOW + f"Processing course: {course.name}")

        course_name = sanitize_filename(course.name)
        course_dir = os.path.join("canvas_downloads", course_name)

        # Skip if the course directory already exists
        if os.path.exists(course_dir):
            print(
                Fore.CYAN
                + f"Skipping course {course.name} because it already has a folder."
            )
            return

        os.makedirs(course_dir, exist_ok=True)

        try:
            folders = course.get_folders()
            root_folder = next(
                f for f in folders if f.full_name == "course files"
            )  # Adjust as needed
            download_folder_contents(root_folder, course_dir)
        except Unauthorized as e:
            print(Fore.RED + f"Unauthorized access in course {course_id}: {e}")
        except Exception as e:
            print(Fore.RED + f"Error processing files in course {course_id}: {e}")

        try:
            modules = course.get_modules()
            for module in modules:
                module_name = sanitize_filename(module.name)
                module_dir = os.path.join(course_dir, module_name)
                os.makedirs(module_dir, exist_ok=True)
                try:
                    module_items = module.get_module_items()
                    for item in module_items:
                        if item.type == "File":
                            try:
                                file = canvas.get_file(item.content_id)
                                if file and file.url:
                                    process_files([file], module_dir)
                                else:
                                    print(
                                        Fore.RED
                                        + f"No URL for file in module item {item.id} in course {course_id}"
                                    )
                            except ResourceDoesNotExist:
                                print(
                                    Fore.RED
                                    + f"File not found for module item {item.id} in course {course_id}"
                                )
                except Unauthorized as e:
                    print(
                        Fore.RED
                        + f"Unauthorized access to module items in module {module.id} in course {course_id}: {e}"
                    )
                except Exception as e:
                    print(
                        Fore.RED
                        + f"Error processing module items in module {module.id} in course {course_id}: {e}"
                    )
        except Unauthorized as e:
            print(
                Fore.RED + f"Unauthorized access to modules in course {course_id}: {e}"
            )
        except Exception as e:
            print(Fore.RED + f"Error processing modules in course {course_id}: {e}")

    except Unauthorized as e:
        print(Fore.RED + f"Unauthorized access to course {course_id}: {e}")
    except ResourceDoesNotExist as e:
        print(Fore.RED + f"Course {course_id} does not exist: {e}")
    except Exception as e:
        print(Fore.RED + f"Error processing course {course_id}: {e}")


if __name__ == "__main__":
    if not os.path.exists("canvas_downloads"):
        os.makedirs("canvas_downloads")

    # Fetch all courses the current user is enrolled in
    courses = canvas.get_courses(enrollment_state=["active", "completed"])
    course_ids = [course.id for course in courses][::-1]

    for course_id in course_ids:
        download_course_files(course_id)
