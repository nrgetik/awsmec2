#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import click
import logging
import sys
from botocore.exceptions import ClientError
from time import strftime, localtime


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - "
                           "%(message)s")
logger = logging.getLogger(sys.argv[0][2:])
logger.setLevel(logging.WARN)


def get_instance_name(instance):
    for tag in instance.tags:
        if tag["Key"] == "Name":
            return tag["Value"]


@click.group()
@click.option("-id", "--instance-id",
              envvar="MAINFRAME_AWS_INSTANCE_ID")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-d", "--debug", is_flag=True)
@click.pass_context
def cli(ctx, instance_id, verbose, debug):
    if instance_id:
        ctx.obj["instance_id"] = instance_id
    else:
        ctx.obj["instance_id"] = False

    ctx.obj["instance_obj"] = boto3.resource("ec2").Instance(
        ctx.obj["instance_id"])
    ctx.obj["instance_name"] = get_instance_name(ctx.obj["instance_obj"])

    if verbose:
        logger.setLevel(logging.INFO)

    if debug:
        logger.setLevel(logging.DEBUG)


@cli.command()
@click.pass_context
def startup(ctx):
    if ctx.obj["instance_obj"].state["Name"] == "running":
        logger.info("{n}'s state is: {s}, no action taken".format(
            n=ctx.obj["instance_name"],
            s=ctx.obj["instance_obj"].state["Name"]))
    else:
        # Dry run first to verify permissions
        try:
            ctx.obj["instance_obj"].start(DryRun=True)
        except ClientError as e:
            if "DryRunOperation" not in str(e):
                raise e
        # Dry run succeeded, do it live
        try:
            response = ctx.obj["instance_obj"].start(DryRun=False)
            logger.debug(response)
        except ClientError as e:
            logger.exception(e)


@cli.command()
@click.pass_context
def shutdown(ctx):
    if ctx.obj["instance_obj"].state["Name"] == "stopped":
        logger.info("{n}'s state is: {s}, no action taken".format(
            n=ctx.obj["instance_name"],
            s=ctx.obj["instance_obj"].state["Name"]))
    else:
        # Dry run first to verify permissions
        try:
            ctx.obj["instance_obj"].stop(DryRun=True)
        except ClientError as e:
            if "DryRunOperation" not in str(e):
                raise e
        # Dry run succeeded, do it live
        try:
            response = ctx.obj["instance_obj"].stop(DryRun=False)
            logger.debug(response)
        except ClientError as e:
            logger.exception(e)


@cli.command()
@click.pass_context
def reboot(ctx):
    if ctx.obj["instance_obj"].state["Name"] == "stopped":
        logger.info("{n}'s state is: {s}, no action taken".format(
            n=ctx.obj["instance_name"],
            s=ctx.obj["instance_obj"].state["Name"]))
    else:
        # Dry run first to verify permissions
        try:
            ctx.obj["instance_obj"].reboot(DryRun=True)
        except ClientError as e:
            if "DryRunOperation" not in str(e):
                raise e
        # Dry run succeeded, do it live
        try:
            response = ctx.obj["instance_obj"].reboot(DryRun=False)
            logger.debug(response)
        except ClientError as e:
            logger.exception(e)


@cli.command()
@click.option("--description", required=True)
@click.option("-nr", "--no-reboot", is_flag=True)
@click.pass_context
def backup(ctx, description, no_reboot):
    if ctx.obj["instance_obj"].state["Name"] == "stopped":
        logger.info("{n}'s state is: {s}, no action taken".format(
            n=ctx.obj["instance_name"],
            s=ctx.obj["instance_obj"].state["Name"]))
    else:
        ami_name = "{dt}_{n}".format(dt=strftime("%Y%m%d%H%M", localtime()),
                                     n=ctx.obj["instance_name"])
        # Dry run first to verify permissions
        try:
            ctx.obj["instance_obj"].create_image(
                Description=description,
                DryRun=True,
                Name=ami_name,
                NoReboot=no_reboot
            )
        except ClientError as e:
            if "DryRunOperation" not in str(e):
                raise e
        # Dry run succeeded, do it live
        try:
            response = ctx.obj["instance_obj"].create_image(
                Description=description,
                DryRun=False,
                Name=ami_name,
                NoReboot=no_reboot
            )
            logger.debug(response)
        except ClientError as e:
            logger.exception(e)


if __name__ == "__main__":
    cli(obj={})
