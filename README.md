# gallery
Simple dockerized Django photo gallery with Semantic UI styles. 

## Features

* Create public or private albums
* Upload photos to albums
  * Preview images and thumbnails are generated with Pillow SIMD
  * Mass uploaded photos are created asynchronously with django-background-tasks
  * Creates also HiDPI images and uses them with srcset
* Edit albums and photos titles and descriptions
* Delete albums and photos
* Ability to scan album directories for new photos (if uploaded directly to server for example with SCP)

## Setup

To setup development environment:

* Create env file gallery.env with following variables to the same directory as docker-compose.yml
  
Variable name | Comments
--- | --- |
POSTGRES_USER | Postgres database username
POSTGRES_PASSWORD | Postgres database password
POSTGRES_DB | Postgres database name
DB_NAME | Database name in Django settings
DB_USER | Database username in Django settings
DB_PASS | Database password in Django settings
DB_HOST | Database hostname in Django settings. Set as "db" for docker-compose to work properly
DB_PORT | Database port in Django settings
DEBUG | Django debug. Set as True or False
SECRET_KEY | Django secret key. Needs to be generated separately
ASYNC_THREADS | django-background-tasks thread count. For example "3"
UPLOAD_PERMISSIONS | Django upload permissions. Specify like 644 or 660, not as Django specifies it (0o664 or 0664)
DIRECTORY_PERMISSIONS | Django directory permissions Specify like 755 or 750, not as Django specifies it (0o755 or 0770)
ALLOWED_HOSTS | Django allowed hosts, for example ['example.com', 'www.example.com'] or just ['localhost']

As a default the docker-compose.yml file is configured to build Pillow SIMD with AVX2 instructions. **If your host CPU doesn't support AVX2 instructions, change _SIMD_LEVEL_ arg to _"sse4"_**.

### Build Docker images
`docker-compose build`

### Create Django superuser
`docker-compose run django python manage.py createsuperuser`

### Start Docker containers
`docker-compose up`

### Accessing shell for debug purposes
`docker-compose run django sh`
