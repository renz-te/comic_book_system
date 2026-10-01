"""
controllers/comics_ctrl.py

Business logic for the Comics module.
"""

from models.comic_model import (
    get_all_comics, search_comics, add_comic,
    update_comic, delete_comic
)


def load_all_comics():
    """Get all comics from the database."""
    return get_all_comics()


def search_comics_ctrl(keyword):
    """Search comics by keyword."""
    return search_comics(keyword)


def add_comic_ctrl(title, author, issue_number, publisher, category, price,
                   stock_quantity, chapters=1, cover_image="", synopsis=""):
    """Add a new comic."""
    return add_comic(title, author, issue_number, publisher, category, price,
                     stock_quantity, chapters, cover_image, synopsis)


def update_comic_ctrl(comic_id, title, author, issue_number, publisher, category,
                      price, stock_quantity, chapters=1, cover_image="", synopsis=""):
    """Update an existing comic."""
    return update_comic(comic_id, title, author, issue_number, publisher, category,
                        price, stock_quantity, chapters, cover_image, synopsis)


def delete_comic_ctrl(comic_id):
    """Delete a comic by ID."""
    return delete_comic(comic_id)
