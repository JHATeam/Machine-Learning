from datetime import datetime
from flask import Blueprint, abort, redirect, render_template, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField, widgets, SubmitField

from app import job_service

jobs_bp = Blueprint('jobs', __name__, template_folder='templates',
                    static_folder='static',)


class JobForm(FlaskForm):
    title = StringField('Job Title')
    company = StringField('Company')
    location = StringField('Location')
    description = TextAreaField('Job Description')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MultiCheckboxForm(FlaskForm):
    check_options = MultiCheckboxField('Routes', coerce=int)
    submit = SubmitField("Set User Choices")


@jobs_bp.route('/', methods=['GET', 'POST'])
def generate_job_summary():
    try:
        form = JobForm()
        if form.validate_on_submit():
            if form.description.data != "":
                job = {
                    'title': "TODO: title",
                    'company': "TODO: company",
                    'location': "TODO: location",
                    'description': form.description.data,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                }
                job_service.create_job(job)
            return redirect(url_for("jobs.generate_job_summary"))
        jobs = job_service.get_all_jobs()
        return render_template('index.html', form=form, jobs=jobs)
    except:
        abort(404)


@jobs_bp.route('/jobs', methods=['GET'])
def get_all_jobs():
    try:
        jobs = job_service.get_all_jobs()
        return render_template("jobs_list.html", jobs=jobs)
    except:
        abort(404)


@jobs_bp.route('/<int:id>/delete', methods=['GET'])
def delete_job(id):
    try:
        job_service.delete_job(id)
        return redirect(url_for("jobs.get_all_jobs"))
    except:
        abort(404)


@jobs_bp.route('/<int:id>/update', methods=['GET', 'POST'])
def update_job(id):
    try:
        form = JobForm()
        job = job_service.get_job(id)
        if form.validate_on_submit():
            new_job = {
                'title': form.title.data,
                'company': form.company.data,
                'location': form.location.data,
                'description': form.description.data,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            job_service.update_job(id, new_job)
            return redirect(url_for("jobs.get_all_jobs"))
        if job:
            form.title.data = job['title']
            form.company.data = job['company']
            form.location.data = job['location']
            form.description.data = job['description']

            return render_template('create.html', operation="Update", form=form, id=id)
        else:
            return redirect(url_for("jobs.get_all_jobs"))
    except:
        abort(404)


@jobs_bp.route('/create', methods=['GET', 'POST'])
def create_job():
    try:
        form = JobForm()
        if form.validate_on_submit():
            job = {
                'title': form.title.data,
                'company': form.company.data,
                'location': form.location.data,
                'description': form.description.data,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            job_service.create_job(job)
            return redirect(url_for("jobs.get_all_jobs"))
        return render_template('create.html', operation="Create", form=form)
    except:
        abort(404)


@jobs_bp.route("/skills", methods=["GET", "POST"])
def example():
    form = MultiCheckboxForm()
    programming_skills = [
        (1, "Python"),
        (2, "JavaScript"),
        (3, "Java"),
        (4, "C++"),
        (5, "HTML/CSS"),
        (6, "SQL"),
        (7, "Ruby"),
        (8, "PHP"),
        (9, "C#"),
        (10, "Swift"),
        # Add more programming skills as needed
    ]

    user_choices = [(3, "Java"), (4, "C++")]
    form.check_options.choices = [(c[0], c[1]) for c in programming_skills]
    if request.method == 'POST' and form.validate_on_submit():
        accepted = []
        for choice in programming_skills:
            if choice[0] in form.check_options.data:
                accepted.append(choice)
        flash("You selected: " + ", ".join([skill[1] for skill in accepted]))
        return render_template('skills.html', form=form)
    else:
        form.check_options.data = [c[0] for c in user_choices]
        return render_template('skills.html', form=form)
