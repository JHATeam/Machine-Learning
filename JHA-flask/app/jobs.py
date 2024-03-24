from datetime import datetime

from flask import Blueprint, abort, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField

from app import job_service

jobs_bp = Blueprint('jobs', __name__, template_folder='templates',
                    static_folder='static',)


class JobForm(FlaskForm):
    title = StringField('Job Title')
    company = StringField('Company')
    location = StringField('Location')
    description = TextAreaField('Job Description')


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
