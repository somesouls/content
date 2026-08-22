"""Aksi review konten."""
from . import store


def pending():
    return store.list_items("pending")


def approve(item_id):
    store.set_status(item_id, "approved")
    return store.get(item_id)


def reject(item_id):
    store.set_status(item_id, "rejected")
    return store.get(item_id)
