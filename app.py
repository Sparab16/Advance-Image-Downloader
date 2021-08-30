# Importing the necessary imports

import uuid
from flask import Flask, render_template, request, send_file
from flask_cors import cross_origin

from Scheduler import ScheduleJob
from Logger import Logging

# Configuring the logger
logger_obj = Logging('Advance Image Downloader')  # Creating a custom based logger
logger_obj.initialize_logger()  # Instantiating the logger object

app = Flask(__name__)  # Initializing the Flask App with the name 'app'


# Home Page Route
@app.route('/', methods=['GET'])
@cross_origin()
def index():
    """
    Function is responsible for showing the index page
    """
    try:
        if request.method == 'GET':
            logger_obj.print_log('Inside the index function', 'info')
            logger_obj.print_log('Rendering the index.html template', 'info')
            return render_template('index.html')
        else:
            logger_obj.print_log('(app.py) - Something went wrong Method not allowed', 'exception')
            return render_template('error.html', msg='Method not allowed')
    except Exception as e:
        logger_obj.print_log('(app.py) - Something went wrong ' + str(e), 'exception')
        return render_template('error.html', msg=str(e))


#  Submitted Page Route
@app.route('/job_submitted', methods=['POST'])
@cross_origin()
def job_submitted():
    """
    The function is responsible for performing the various actions after the job is submitted by the user
    """
    try:
        if request.method == 'POST':
            logger_obj.print_log('Inside the job_submitted function', 'info')

            # Handling the user input
            search_query = request.form['search-query'].lower()
            date = request.form['date']
            time = request.form['time']
            email = request.form['email'].lower()
            no_images = int(request.form['images'])

            # Creating the unique ID for the request generated
            req_id = uuid.uuid4()

            # Creating a object for th e scheduler
            schedule_job = ScheduleJob()

            # Adding the job in the scheduler
            schedule_job.insert_request(search_query, date, time, no_images, email, req_id)

            logger_obj.print_log('Schedule is added for adding the job in queue', 'info')
            # Todo - Use request id to populate Image URl or Just add right away in the database when doing the
            #  insertion operation

            # Todo - To implement logs inside the cassandra database

            # Rendering the Job Submitted template
            logger_obj.print_log('Rendering the job_submitted.html template', 'info')
            return render_template('job_submitted.html')
        else:
            logger_obj.print_log('(app.py) - Something went wrong Method is not allowed', 'exception')
            return render_template('error.html', msg='Method not allowed')

    except Exception as e:
        logger_obj.print_log('(app.py) - Something went wrong ' + str(e), 'exception')
        return render_template('error.html', msg=str(e))


# Downloading the images route
@app.route('/download/<search_term>/<uuid:req_id>', methods=['GET'])
@cross_origin()
def download(search_term, req_id):
    """
    Function is responsible for sending the zip file to the user
    :param search_term: Search query of the user
    :param req_id: Unique request ID of the user
    :return: Zip file created
    """
    try:
        logger_obj.print_log('Inside the download route', 'info')
        str_req_id = str(req_id)

        # Sending the downloadable file to the user
        return send_file(str_req_id + '_zipfile.zip', as_attachment=True, attachment_filename=search_term + '.zip')

    except Exception as e:
        logger_obj.print_log('(app.py) - Something went wrong ' + str(e), 'exception')
        return render_template('error.html', msg='This link has expired')


if __name__ == '__main__':
    app.debug = True
    app.run()
