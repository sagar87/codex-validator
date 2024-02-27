import os
from collections import OrderedDict, defaultdict

import s3fs
import streamlit as st
from dotenv import load_dotenv
from natsort import natsorted

load_dotenv(".env")

AWS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_KEY_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_URL = os.getenv("AWS_URL")
AWS_PATH = os.getenv("AWS_PATH")

fs = s3fs.S3FileSystem(anon=False, client_kwargs={"endpoint_url": AWS_URL})


@st.cache_data
def get_samples():
    """Returns sample paths dict."""
    return natsorted([f for f in fs.glob(AWS_PATH + "/*")])


@st.cache_data
def get_graphs(path):
    paths = []
    for f in natsorted(fs.glob(path + "/*")):
        # print(f)
        graph = "_".join(f.split("_")[:-1])
        # print('FILE', f.split("_"))
        if graph not in paths:
            paths.append(graph)

    return paths


@st.cache_data
def get_inits(path, graph):
    return natsorted([f for f in fs.glob(path + "/*") if f.startswith(graph)])


@st.cache_data
def get_files(path):
    paths = natsorted([f for f in fs.glob(path + "/*.png")])
    file_dict = defaultdict(list)
    for p in paths:
        fname = p.split("/")[-1]
        url = AWS_URL + "/" + p
        file_dict["_".join(fname.split("_")[1:-1])].append(url)

    return file_dict


def get_sub_dirs(path):
    """Returns sample paths dict."""

    sample_data = defaultdict(OrderedDict)
    for path in natsorted(fs.glob(os.path.join(path, "*"))):
        file = os.path.basename(os.path.normpath(path))
        name, ext = os.path.splitext(file)
        if ext:
            continue

        splitted = file.split("_")
        sub, source_node, init = "_".join(splitted[:-2]), splitted[-2], splitted[-1]
        sample_data[sub][int(init)] = path

    return sample_data
