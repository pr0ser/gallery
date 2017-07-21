# gallery
Django photo gallery app.

## Setup
* Create env.conf with following variables
  * POSTGRES_USER
  * POSTGRES_PASSWORD
  * POSTGRES_DB
  * DB_NAME
  * DB_USER
  * DB_PASS
  * DB_HOST=db
  * DB_PORT
  * DEBUG (True or False)
  * SECRET_KEY (for Django settings)
  * ASYNC_THREADS
  * UPLOAD_PERMISSIONS=664
  * DIRECTORY_PERMISSIONS=775

Note that UPLOAD_PERMISSIONS and DIRECTORY_PERMISSIONS needs to be specified like 644, or 755 in the env file. Not as Django specifies it (0o664 or 0664).

### Build Docker images
`docker-compose build`

### Start Docker containers
`docker-compose up`