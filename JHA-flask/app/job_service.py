from flask import current_app, jsonify
import app.chat_openai as chat_openai


def get_all_jobs():
    return load_jobs()


def get_job(id):
    return next((job for job in load_jobs() if job['id'] == id), None)


def create_job(job):
    jobs = load_jobs()
    if len(jobs) == 0:
        job['id'] = 1
    else:
        job['id'] = max([job['id'] for job in jobs]) + 1
    job_summary = get_job_summary(job)
    job['summary'] = job_summary['summary']
    job['title'] = job_summary['title']
    job['company'] = job_summary['company']
    job['location'] = job_summary['location']
    job['skills'] = job_summary['skills']
    jobs.append(job)
    save_jobs(jobs)
    return job


def get_job_summary(job):
    # TODO: Update with AI service
    try:
        return chat_openai.tagging_job_description(job['description'])
        # response = requests.get(
        #     'https://my-json-server.typicode.com/Slothbetty/SampleSummaryJsonData/job_summary')
        # if response.status_code == 200:
        #     return response.json()
        # else:
        #     return jsonify({'error': 'Failed to retrieve data from API'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def update_job(id, new_job):
    jobs = load_jobs()
    job = next((job for job in jobs if job['id'] == id), None)
    if not job:
        return
    job.update(new_job)
    save_jobs(jobs)
    return job


def delete_job(id):
    jobs = load_jobs()
    job = next((job for job in jobs if job['id'] == id), None)
    if not job:
        return
    jobs.remove(job)
    save_jobs(jobs)
    return job


def load_jobs():
    try:
        import json
        import os
        file = current_app.config['JOBS']
        file_path = os.path.join(os.path.dirname(current_app.root_path), file)
        with open(file_path) as f:
            return json.load(f)['jobs']
    except:
        return []


def save_jobs(jobs):
    try:
        import json
        import os
        file = current_app.config['JOBS']
        file_path = os.path.join(os.path.dirname(current_app.root_path), file)
        with open(file_path, 'w') as f:
            json.dump({'jobs': jobs}, f)
    except:
        pass
