#!/bin/python3
import boto3
import pickle
import click

from botocore.exceptions import ClientError
from pathlib import Path
from pedro import create_instance, main
from cleanup import cleanup
from util.constants import *


def _get_service_data():
    try:
        d = pickle.load(Path('{}/.pccdata.p'.format(Path.home())).open('rb'))
        return d
    except IOError as e:
        print('Data file ({}/.pccdata.p) not found, are you running instances' +
              ' already?'.format(Path.home()))
        return False


@click.group()
def cli(): pass


@cli.command()
def clean():
    cleanup()


@cli.command()
def start():
    print('starting service with {} instances on {} zone'\
          .format(NUM_INSTANCES, GENERIC_ZONE))
    main()


@cli.command()
@click.option('--number', '-n', default=1, type=int,
              help='Add instances to load balancer',
              prompt='Number of instances')
def add_instances(number):
    data = _get_service_data()
    if not data:
        exit(0)

    ec2 = boto3.client('ec2')
    elb = boto3.client('elb')

    instances = create_instance(ec2, IMAGE_ID, INSTANCE_TYPE,
                                data['sg_id'], number, ZONES)
    if len(instances) < number:
        print('Failed to create instances')
