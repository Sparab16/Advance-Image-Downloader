# Importing the necessary imports
import re
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
            no_images = request.form['images']

            is_valid, error = validate_inputs(search_query, date, time, email, no_images)

            if is_valid:
                # Creating the unique ID for the request generated
                req_id = uuid.uuid4()

                # Creating a object for th e scheduler
                schedule_job = ScheduleJob()

                # Adding the job in the scheduler
                schedule_job.insert_request(search_query, date, time, int(no_images), email, req_id)

                logger_obj.print_log('Schedule is added for adding the job in queue', 'info')

                # Rendering the Job Submitted template
                logger_obj.print_log('Rendering the job_submitted.html template', 'info')
                return render_template('job_submitted.html')
            else:
                logger_obj.print_log('(app.py) - Something went wrong ' + error, 'exception')
                return render_template('error.html', msg=error)

        else:
            logger_obj.print_log('(app.py) - Something went wrong Method is not allowed', 'exception')
            return render_template('error.html', msg='Method not allowed')

    except ValueError:
        logger_obj.print_log('(app.py) - Something went wrong. No of images must be a number', 'exception')
        return render_template('error.html', msg='No of images must be a number')

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


def validate_inputs(search_query, date, time, email, no_images):
    """
    Function is responsible for validating the inputs given by the user
    :param search_query: search term by the user
    :param date: Date for scheduling the job
    :param time: Time for scheduling the job
    :param email: Email address of the user
    :param no_images: No of images given by the user
    :return: Boolean if the input's are valid
    """
    try:
        # Checking if the queries passed are empty
        if search_query != '' and date != '' and time != '' and email != '' and no_images != '':

            no_images = int(no_images)  # Converting into integer for further processing
            # Number of images should be in between 1 and 500
            if 1 <= no_images <= 500:
                # Validating the email address
                if re.search('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
                    return True, None
                else:
                    logger_obj.print_log('(app.py (validate_inputs)) - Something went wrong. Email address is invalid',
                                         'exception')
                    return False, 'Invalid email address'
            else:
                logger_obj.print_log('(app.py (validate_inputs)) - Something went wrong. No of images must be in '
                                     'between 1 and 500',
                                     'exception')
                return False, 'No of images must be in between 1 and 500'
        else:
            logger_obj.print_log('(app.py (validate_inputs)) - Something went wrong. One of the inputs is empty',
                                 'exception')
            return False, 'One of inputs is empty'

    except Exception as e:
        raise Exception(e)


if __name__ == '__main__':
    app.debug = True
    app.run()
