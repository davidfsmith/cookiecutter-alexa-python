PROJECT_NAME={{cookiecutter.skill_name}}
DYNAMODB_TABLE_NAME={{cookiecutter.dynamodb_table_name}}
ALEXA_SKILL={{cookiecutter.alexa_skill_id}}
CDK_PROFILE={{cookiecutter.cdk_profile}}
PKG_DIR=layers/python

install:
	pip install -r requirements-dev.txt

clean:
	pip freeze --local | xargs pip uninstall -y

test:
	python -m pytest

dialogue:
	ask dialog --skill-id $(ALEXA_SKILL) --stage development --locale en-GB

# CDK

cdk_bootstrap:
	cdk bootstrap --profile $(CDK_PROFILE)

cdk_deploy:
	cdk deploy --profile $(CDK_PROFILE)

cdk_destroy:
	cdk destroy --profile $(CDK_PROFILE)

cdk_layer_build:
	rm -rf $(PKG_DIR) && mkdir -p $(PKG_DIR)
	docker run --rm -v $(shell pwd):/foo -w /foo lambci/lambda:build-python3.8 \
		sh ./install_python_libs.sh $(PKG_DIR)

dynamodb_load:
	./tools/data.py Load tools/people_example.csv $(DYNAMODB_TABLE_NAME) --dryrun=False --overwrite=True

# Local stuff

docker_start:
	docker-compose up -d dynamodb

docker_log:
	docker-compose logs -f

docker_stop:
	docker-compose down

local_dynamodb_create:
	aws dynamodb create-table --table-name $(DYNAMODB_TABLE_NAME) \
		--attribute-definitions \
			AttributeName=uuid,AttributeType=S \
		--key-schema \
			AttributeName=uuid,KeyType=HASH \
		--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
		--endpoint-url http://localhost:8000 | jq

local_dynamodb_load:
	./tools/data.py Load tools/people_example.csv $(DYNAMODB_TABLE_NAME) --dryrun=False --local=True --overwrite=True

local_dynamodb_delete:
	aws dynamodb delete-table --table-name $(DYNAMODB_TABLE_NAME) --endpoint-url http://localhost:8000 | jq

.PHONY: install clean test dialogue cdk_bootstrap cdk_deploy cdk_destroy cdk_layer_build dynamodb_load docker_start docker_log docker_stop local_dynamodb_create local_dynamodb_load local_dynamodb_delete
