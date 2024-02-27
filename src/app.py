import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="CODEX Viewer", page_icon=":bar_chart:", layout="wide")

from drive import get_files, get_graphs, get_inits, get_samples, get_sub_dirs
from firebase import (
    get_db,
    get_message,
    get_reviewers,
    get_sample_data,
    post_message,
    update_message,
)

# from auth import authenticator
from utils import format_graph, format_init, format_sample, read_html

db = get_db()

if "reviewers" not in st.session_state:

    st.session_state.reviewers = get_reviewers(db)

if "selected_reviewer" not in st.session_state:
    st.session_state.selected_reviewer = st.session_state.reviewers[0]

if "samples" not in st.session_state:
    st.session_state.samples = get_samples()  # pull samples from S3

if "selected_sample" not in st.session_state:
    st.session_state.selected_sample = None

if "graphs" not in st.session_state:
    st.session_state.graphs = None

if "selected_graph" not in st.session_state:
    st.session_state.selected_graph = None

if "idx_graph" not in st.session_state:
    st.session_state.idx_graph = None

if "inits" not in st.session_state:
    st.session_state.inits = None

if "selected_init" not in st.session_state:
    st.session_state.selected_init = 0

if "idx_init" not in st.session_state:
    st.session_state.idx_init = None

if "index" not in st.session_state:
    st.session_state.index = 0

if "is_classified" not in st.session_state:
    st.session_state.is_classified = False


def increment_init():
    if st.session_state.idx_init == (len(st.session_state.inits) - 1):
        st.info("Last init")
        # st.session_state.next_init = False
        return
    st.session_state.idx_init += 1
    if st.session_state.idx_init == (len(st.session_state.inits) - 1):
        st.info("Last init")
    st.session_state.selected_init = st.session_state.inits[st.session_state.idx_init]


def decrement_init():
    if st.session_state.idx_init == 0:
        st.info("First init")
        return
    st.session_state.idx_init -= 1
    if st.session_state.idx_init == 0:
        st.info("First init")
    st.session_state.selected_init = st.session_state.inits[st.session_state.idx_init]


def next_graph():
    if st.session_state.idx_graph == (len(st.session_state.graphs) - 1):
        st.info("Last graph")
        return
    # print(st.session_state)
    st.session_state.idx_graph += 1
    if st.session_state.idx_graph == (len(st.session_state.graphs) - 1):
        st.info("Last graph")

    st.session_state.selected_graph = st.session_state.graphs[
        st.session_state.idx_graph
    ]
    # print(st.session_state)
    reset_init()
    # st.info(f'Next graph {format_graph(st.session_state.selected_graph)}')
    # st.session_state.selected_init = st.session_state.inits[0]


def prev_graph():
    if st.session_state.idx_graph == 0:
        st.info("First graph")
        return
    st.session_state.idx_graph -= 1
    if st.session_state.idx_graph == 0:
        st.info("First graph")
    st.session_state.selected_graph = st.session_state.graphs[
        st.session_state.idx_graph
    ]
    reset_init()
    # st.info(f'Prev graph {format_graph(st.session_state.selected_graph)}')
    # st.session_state.selected_init = st.session_state.inits[0]


def reset_graph():

    if st.session_state.selected_sample is None:
        st.session_state.graphs = None
        st.session_state.inits = None
        st.session_state.selected_graph = None
        st.session_state.selected_init = None
        st.session_state.idx_graph = None
        st.session_state.idx_init = None
    else:
        graphs = get_graphs(st.session_state.selected_sample)
        st.session_state.graphs = graphs
        st.session_state.selected_graph = graphs[0]
        st.session_state.idx_graph = st.session_state.graphs.index(
            st.session_state.selected_graph
        )
        inits = get_inits(st.session_state.selected_sample, graphs[0])
        st.session_state.inits = inits
        st.session_state.selected_init = inits[0]
        st.session_state.idx_init = st.session_state.inits.index(
            st.session_state.selected_init
        )
        st.session_state.is_classified = get_message(
            db, st.session_state.selected_sample, st.session_state.selected_graph
        )


def reset_init():
    inits = get_inits(st.session_state.selected_sample, st.session_state.selected_graph)
    st.session_state.inits = inits
    st.session_state.selected_init = inits[0]
    st.session_state.idx_init = st.session_state.inits.index(
        st.session_state.selected_init
    )
    st.session_state.is_classified = get_message(
        db, st.session_state.selected_sample, st.session_state.selected_graph
    )


def do_validate():
    if st.session_state.is_classified:
        update_message(
            db,
            st.session_state.selected_sample,
            st.session_state.selected_graph,
            st.session_state.selected_init,
            st.session_state.selected_reviewer,
        )
        st.warning("Changed initialistion!")
        st.success("Updated database.")
        if not (st.session_state.idx_graph == (len(st.session_state.graphs) - 1)):
            next_graph()
            st.info("Next graph")

    else:
        post_message(
            db,
            st.session_state.selected_sample,
            st.session_state.selected_graph,
            st.session_state.selected_init,
            st.session_state.selected_reviewer,
        )
        #
        st.success("Updated database.")
        if not (st.session_state.idx_graph == (len(st.session_state.graphs) - 1)):
            next_graph()
            st.info("Next graph")


def mark_bad():
    if st.session_state.is_classified:
        update_message(
            db,
            st.session_state.selected_sample,
            st.session_state.selected_graph,
            '-1',
            st.session_state.selected_reviewer,
        )
        st.warning("Marked bad channel!")
        st.success("Updated database.")
        if not (st.session_state.idx_graph == (len(st.session_state.graphs) - 1)):
            next_graph()
            st.info("Next graph")
    else:
        post_message(
            db,
            st.session_state.selected_sample,
            st.session_state.selected_graph,
            "-1",
            st.session_state.selected_reviewer,
        )
        st.warning("Marked bad channel")
        st.success("Updated database.")
        if not (st.session_state.idx_graph == (len(st.session_state.graphs) - 1)):
            next_graph()


st.title("CODEX VALIDATOR")

if st.session_state.selected_sample is None:
    st.write("Please select a sample ... ")
else:
    components.html(read_html(), height=0, width=0)
    # files = get_files(SAMPLES[st.session_state.selected_sample])
    if (st.session_state.selected_graph is not None) and (
        st.session_state.selected_init is not None
    ):
        if not st.session_state.is_classified:
            status =  ':question:'
        elif st.session_state.is_classified == '-1':
            status = ':x:'
        else:
            status = ':white_check_mark:' 
        st.subheader(
            f"Sample {format_sample(st.session_state.selected_sample)} | SubGraph {format_graph(st.session_state.selected_graph)} 	{status} | Init {format_init(st.session_state.selected_init)}"
        )

    if (st.session_state.selected_graph is not None) and (
        st.session_state.selected_init is not None
    ):
        # graph_idx = st.session_state.graphs.index(st.session_state.selected_graph)
        # init_idx = st.session_state.inits.index(st.session_state.selected_init)

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.button(
                "Prev init",
                on_click=decrement_init,
                disabled=True if st.session_state.idx_init == 0 else False,
            )

        with col2:
            st.button(
                "Next init",
                on_click=increment_init,
                disabled=True
                if st.session_state.idx_init == (len(st.session_state.inits) - 1)
                else False,
            )

        with col3:
            st.button(
                "Next graph",
                on_click=next_graph,
                disabled=True
                if st.session_state.idx_graph == (len(st.session_state.graphs) - 1)
                else False,
            )

        with col4:
            st.button(
                "Prev graph",
                on_click=prev_graph,
                disabled=True if st.session_state.idx_graph == 0 else False,
            )
        with col5:
            #     # select initialisation
            st.button("Select init", on_click=do_validate)

        with col6:
            #     # select initialisation
            st.button("Mark bad", on_click=mark_bad)

        files = get_files(st.session_state.selected_init)

        for i, (k, v) in enumerate(files.items()):
            with st.expander(k, expanded=True if i == 0 else False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.image(v[0])

                with col2:
                    st.image(v[1])

                with col3:
                    st.image(v[2])

with st.sidebar:
    reviewer = st.selectbox(
        "Select Reviewer",
        st.session_state.reviewers,
        index=0,
        key="selected_reviewer",
        placeholder="Select a Reviewer...",
    )

    option = st.selectbox(
        "Select Sample",
        st.session_state.samples,
        index=None,
        format_func=format_sample,
        key="selected_sample",
        on_change=reset_graph,
        placeholder="Select Sample...",
    )

    st.write(
        "You selected:",
        format_sample(st.session_state.selected_sample)
        if st.session_state.selected_sample is not None
        else st.session_state.selected_sample,
    )

    if st.session_state.selected_sample is not None:
        sub_option = st.selectbox(
            "Select Subgraph",
            st.session_state.graphs,
            index=0,
            key="selected_graph",
            format_func=format_graph,
            on_change=reset_init,
            placeholder="Select Graph...",
        )

        st.write("You selected:", format_graph(st.session_state.selected_graph))

        init = st.selectbox(
            "Select init",
            st.session_state.inits,
            index=0,
            placeholder="Select init",
            format_func=format_init,
            key="selected_init",
        )

        st.write("You selected:", format_init(st.session_state.selected_init))

        sample_data = get_sample_data(db, st.session_state.selected_sample)
        classified_graphs = [k["marker"] for k in sample_data]
        for sub_graph in st.session_state.graphs:
            if format_graph(sub_graph) in classified_graphs:
                current_data = sample_data[
                    classified_graphs.index(format_graph(sub_graph))
                ]
                st.markdown(
                    f'G: {format_graph(sub_graph)} { ":white_check_mark:" if current_data["initialisation"] != "-1" else ":x:" } ({current_data["initialisation"]}) | {current_data["reviewer"]}'
                )
            else:
                st.markdown(f"G: {format_graph(sub_graph)} :question:")
