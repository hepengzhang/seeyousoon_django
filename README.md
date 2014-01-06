README.md
=========
Hepeng's Dev IDE: Eclipse+PyDev

Current Server structure:
* EC2 instance: AWS Micro Linux AMI
* database: AWS RDS(mysql)
* web server: Nginx + uwsgi + Django 1.6

To do list:
- Continuous deployment
- API Documentation (Swagger)
- Automatic package dependencies (virtualenv and pip):

    http://stackoverflow.com/questions/12069336/does-django-have-an-equivalent-of-railss-bundle-install

    http://stackoverflow.com/questions/8726207/what-are-the-python-equivalents-to-rubys-bundler-perls-carton

