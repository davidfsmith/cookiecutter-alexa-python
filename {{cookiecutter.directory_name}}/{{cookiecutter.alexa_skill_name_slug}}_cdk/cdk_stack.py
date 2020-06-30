from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_assets as s3_assets,
    core
)
from aws_cdk.core import App, Stack, Tag


class AlexaCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        app = App()
        alexa_stack = Stack(app, "AlexaStack")

        layer_ask = _lambda.LayerVersion(
            self, "layer_ask",
            description = "Alexa Skills Kit SDK and XRay",
            layer_version_name = "python_ask",
            code = _lambda.AssetCode('layers/layer-ask.zip'),
            compatible_runtimes = [_lambda.Runtime.PYTHON_3_8]
        )

        layer_utils = _lambda.LayerVersion(
            self, "layer_inflect",
            description = "Util libraries = inflect, pendulum, requests",
            layer_version_name = "python_inflect",
            code = _lambda.AssetCode('layers/layer-utils.zip'),
            compatible_runtimes = [_lambda.Runtime.PYTHON_3_8]
        )

        alexa_lambda = _lambda.Function(
            self, "alexa_lambda",
            function_name = "{{cookiecutter.alexa_skill_name_slug}}_lambda",
            description = "{{cookiecutter.alexa_skill_summary}} lambda code",
            runtime = _lambda.Runtime.PYTHON_3_8,
            code = _lambda.AssetCode("lambda_alexa/{{cookiecutter.alexa_skill_name_slug}}"),
            handler = "app.lambda_handler",
            layers = [layer_ask, layer_utils],
            memory_size = 128,
            timeout = core.Duration.seconds(3),
            tracing = _lambda.Tracing.ACTIVE
        )

        # FIXME - Manual step to add ASK trigger to Lambda (limitation of CDK)
        # lambda_alexa_wireless.add_event_source_mapping()
        alexa_lambda.add_environment("LOGGING", "DEBUG")
        alexa_lambda.add_environment("ENV", "PROD")

        dynamo_table = dynamodb.Table(
            self, "dynamo_table",
            table_name = "{{cookiecutter.dynamodb_table_name}}",
            partition_key = {
                "name": "uuid",
                "type": dynamodb.AttributeType.STRING
            },
            removal_policy = core.RemovalPolicy.DESTROY
        )

        alexa_lambda.add_environment("DYNAMODB", dynamo_table.table_name)
        dynamo_table.grant_read_write_data(alexa_lambda)

        Tag.add(AlexaStack, "Project", "{{cookiecutter.alexa_skill_name}}")

        # Outputs
        core.CfnOutput(
            self, "lambda_arn",
            value = alexa_lambda.function_arn
        )
