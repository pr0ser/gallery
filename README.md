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
  * DB_HOST
  * DB_PORT
  * DEBUG (0 or 1)
  * SECRET_KEY (for Django settings)

### Build Docker images
`docker-compose build`

### Start Docker containers
`docker-compose up`