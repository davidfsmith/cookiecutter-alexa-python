#!/usr/bin/env python3

from aws_cdk import core

from {{cookiecutter.alexa_skill_name_slug}}_cdk.cdk_stack import AlexaCdkStack as CdkStack


app = core.App()
CdkStack(
    app,
    "{{cookiecutter.alexa_skill_cdk_stack_name}}",
    stack_name = "{{cookiecutter.alexa_skill_cdk_stack_name}}",
    description = "Lambda / DynamoDB stack for {{cookiecutter.alexa_skill_name}}"
)

app.synth()
