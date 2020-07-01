# CookieCutter Alexa Python

Starting template for creating an Alexa skill using Python and Alexa Skills Kit

## Features

* Deployment into AWS using CDK
* Tools - Lambda Layer building using Docker
* Tools - Local DynamoDB
* Tools - DynamoDB data loader (local and AWS)
* Alexa skill - Persistence using DynamoDB
* Alexa skill - Accessing user data

## Prerequsities

* [Alexa Developer Account](https://developer.amazon.com/alexa)
* [AWS account](https://aws.amazon.com/account/)
* [AWS CLI installed](https://aws.amazon.com/cli/)
* [AWS CDK installed](https://aws.amazon.com/cdk/)
* [Docker installed](https://www.docker.com/)
* Python 3.8
* [Cookiecutter installed](https://github.com/cookiecutter/cookiecutter)
* A great idea for an Alexa Skill (optional)

## Usage

Create your Alexa skill on [developer.amazon.com/alexa](https://developer.amazon.com/alexa/console/ask)

## Create your initial skill code

Use `cookiecutter` to create your intial code:

    $ cookiecutter https://github.com/davidfsmith/cookiecutter-alexa-python

## TODO

* Testing
* Automate more of the building (when possible)
* Move output to templates (Using Alexa Presentation Language)