# job_portal

# Project setup
* step 1:
Clone the project

* step 2:
install requirements using 
`pip install -r requirements.txt`
* step 3:
start server using 
`python manage.py runserver`
* step 4:
database migration using
`python manage.py makemigrations`
`python manage.py migrate`

# Test Cases
* Run test cases using 
` python manage.py test apps.jobs.tests apps.company.tests apps.user.tests`

# Create Admin
* create admin using`python manage.py createsuperuser`

# API details
* ## User
    * ### Registration
      * endpoint: /user/user/register/ 
      * employer and candidate have access to the api
    * ### Login
      * endpoint: /user/user/login/
      * employer and candidate have access to the api
    * ### Get Role
      * endpoint: /user/user/role/ 
      * employer and candidate have access to the api

* ## Company 
    * ### Company Create 
      * endpoint: /company/company/
      * employer and candidate have access to the api

* ## Job
    * ### Job Create
      * endpoint: /jobs/jobs/
      * employer have access to the api
    * ### Job List
      * endpoint: /jobs/jobs/
      * employer, candidate and admin have access to the api
    * ### Job Update
      * endpoint: /jobs/jobs/job_id/
      * employer have access to the api
    * ### Job Delete
      * endpoint: /jobs/jobs/job_id/
      * employer and admin have access to the api

* ## Job Application
    * ### Job Apply Create
      * endpoint: /jobs/applications/
      * candidate have access to the api
    * ### Job Apply List
      * endpoint: /jobs/applications/
      * candidate have access to the api
    * ### Job Apply Update
      * endpoint:  /jobs/applications/job_id/
      * candidate have access to the api
    * ### Job Apply Delete
      * endpoint: /jobs/applications/job_id/
      *  candidate have access to the api

* ## Job Status
    * ### Applicants for job
      * /jobs/employer/job_id/applicants/
      * employer have access to the api
    * ### Job Status Update
      * /jobs/employer/job_application_id/change-status/
      * employer have access to the api

