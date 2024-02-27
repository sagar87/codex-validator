import os
from datetime import datetime

import streamlit as st
from google.cloud.firestore import Client
from google.cloud.firestore_v1.base_query import FieldFilter, Or
from google.oauth2 import service_account

from utils import format_graph, format_init, format_sample

my_credentials = {
    "type": "service_account",
    "project_id": "celligator-791c1",
    "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
    "private_key": os.environ.get("PRIVATE_KEY").replace("`", ""),  # CHANGE HERE
    "client_email": os.environ.get("CLIENT_EMAIL"),
    "client_id": os.environ.get("CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL"),
    "universe_domain": "googleapis.com",
}

# print(my_credentials)


@st.cache_resource
def get_db():
    creds = service_account.Credentials.from_service_account_info(my_credentials)
    db = Client(credentials=creds, project="celligator-791c1")
    return db


def get_reviewers(db):
    query = db.collection("reviewer").get()

    return [q.to_dict()["name"] for q in query]


def get_sample_data(db, sample):
    docs = (
        db.collection("validation")
        .where(filter=FieldFilter("sample", "==", format_sample(sample)))
        .get()
    )  # Get all documents with age >=40
    # print([ q.to_dict() for q in docs ])
    return [q.to_dict() for q in docs]


def post_message(db, sample, graph, init, reviewer):
    payload = {
        "sample": format_sample(sample),
        "marker": format_graph(graph),
        "initialisation": format_init(init),
        "reviewer": reviewer,
        # "comment": comment,
        # "date": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
    }
    doc_ref = db.collection("validation").document()
    res = doc_ref.set(payload)
    return res


def get_message(db, sample, graph):
    query = (
        db.collection("validation")
        .where(filter=FieldFilter("sample", "==", format_sample(sample)))
        .where(filter=FieldFilter("marker", "==", format_graph(graph)))
        .get()
    )
    # print(query)
    if len(query) > 0:
        return query[0].to_dict()['initialisation']
    else:
        return False


def update_message(db, sample, graph, init, reviewer):
    docs = (
        db.collection("validation")
        .where(filter=FieldFilter("sample", "==", format_sample(sample)))
        .where(filter=FieldFilter("marker", "==", format_graph(graph)))
        .where(filter=FieldFilter("reviewer", "==", reviewer))
        .get()
    )  # Get all documents with age >=40
    doc = docs[0]
    # print(docs)
    key = doc.id
    res = (
        db.collection("validation")
        .document(key)
        .update({"initialisation": format_init(init)})
    )
    return res
