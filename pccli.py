#!/bin/python3
import boto3
import pickle
import click

from botocore.exceptions import ClientError
from pathlib import Path
from pedro import create_instance
from util.constants import *


def _get_service_data():
    try:
        d = pickle.load(Path('{}/.pccdata.p'.format(Path.home())).open('rb'))
        return d
    except IOError as e:
        print('Data file ({}/.pccdata.p) not found, are you running instances already?'\
              .format(Path.home()))
        return False


@click.command()
@click.option('--add', '-a', default=1, type=int)
def add_instances(add):
    data = _get_service_data()
    ec2 = boto3.client('ec2')
    elb = boto3.client('elb')

    instances = create_instance(ec2, IMAGE_ID, INSTANCE_TYPE, data['sg_id'],
                                add, ZONES)
    if len(instances) < add:
        print('Failed to create instances')
