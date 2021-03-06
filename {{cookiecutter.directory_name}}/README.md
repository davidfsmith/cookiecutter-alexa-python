# {{cookiecutter.alexa_skill_name}}

{{cookiecutter.alexa_skill_summary}}

## Prerequsities

* [Alexa Developer Account](https://developer.amazon.com/alexa)
* [AWS account](https://aws.amazon.com/account/)
* [AWS CLI installed](https://aws.amazon.com/cli/)
* [AWS CDK installed](https://aws.amazon.com/cdk/)
* [Docker installed](https://www.docker.com/)
* Python 3.8
* A great idea for an Alexa Skill (optional)

## Local Development

Set up a Python virtualenv in whichever way works for you, I use [pyenv](https://github.com/pyenv/pyenv) with [pyenv-virtual](https://github.com/pyenv/pyenv-virtualenv).  So for me:

    $ pyenv virtualenv 3.8.0 <pyenv-name> && echo '<pyenv-name>' >> .python-version

Then install all of the libraries using the Makefile:

    $ make install

## Deploy the application

AWS CDK is used to build and deploy the application stack, the only manual step is creating the Lambda trigger (not supported by CDK as of writting) for Alexa

First time:

    $ make cdk_bootstrap

Build the lambda layers:

    $ make cdk_layer_build

Then:

    $ make cdk_deploy

Finally paste [en-GB.json](interactionModels/en-GB.json) into the Alexa Developer console, build your skill and give it a test.

Using the Alexa development console, Alexa App or any devices associated with your Amazon developer account you can then interact with your awesome new skill.

**Note:** If your Alexa devices are set to a different locale you'll need to change the interactionModels/*.json as appropriate.

### Loading Data

Source CSV example:

    firstname,lastname,website,twitter,linkedin
    David,Smith,https://www.dave-smith.co.uk,davidfsmith,https://www.linkedin.com/in/davidfsmithy/

Source CSV Map file example:

    destination,source,type,action
    uuid,,,generate_uuid
    firstname
    lastname
    website
    twitter
    linkedin

To load the data (locally):

    $ make docker_start
    $ make local_dynamodb_create
    $ make local_dynamodb_load

To load the data into AWS (CDK is used to create the DynamoDB table):

    $ make dynamodb_load
