from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Contact
from app.storage import save_profile_image

contacts_bp = Blueprint("contacts", __name__)


@contacts_bp.route("/")
@login_required
def list_contacts():
    query = request.args.get("q", "").strip()
    contacts_query = Contact.query.filter_by(user_id=current_user.id)
    if query:
        contacts_query = contacts_query.filter(Contact.name.ilike(f"%{query}%"))
    contacts = contacts_query.order_by(Contact.name.asc()).all()
    return render_template("contacts_list.html", contacts=contacts, query=query)


@contacts_bp.route("/contacts/new", methods=["GET", "POST"])
@login_required
def create_contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("contacts.create_contact"))

        image_url = None
        try:
            image_url = save_profile_image(request.files.get("profile_image"))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("contacts.create_contact"))

        contact = Contact(
            name=name,
            email=request.form.get("email", "").strip(),
            phone=request.form.get("phone", "").strip(),
            notes=request.form.get("notes", "").strip(),
            profile_image_url=image_url,
            user_id=current_user.id,
        )
        db.session.add(contact)
        db.session.commit()
        flash("Contact added.", "success")
        return redirect(url_for("contacts.list_contacts"))

    return render_template("contact_form.html", contact=None)


@contacts_bp.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
@login_required
def edit_contact(contact_id):
    contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        contact.name = request.form.get("name", "").strip()
        contact.email = request.form.get("email", "").strip()
        contact.phone = request.form.get("phone", "").strip()
        contact.notes = request.form.get("notes", "").strip()

        new_image = request.files.get("profile_image")
        if new_image and new_image.filename:
            try:
                contact.profile_image_url = save_profile_image(new_image)
            except ValueError as e:
                flash(str(e), "error")
                return redirect(url_for("contacts.edit_contact", contact_id=contact.id))

        db.session.commit()
        flash("Contact updated.", "success")
        return redirect(url_for("contacts.list_contacts"))

    return render_template("contact_form.html", contact=contact)


@contacts_bp.route("/contacts/<int:contact_id>/delete", methods=["POST"])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first_or_404()
    db.session.delete(contact)
    db.session.commit()
    flash("Contact deleted.", "success")
    return redirect(url_for("contacts.list_contacts"))
