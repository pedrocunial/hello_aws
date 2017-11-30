#!/bin/python3
import boto3
import pickle
import click

from random import choice
from botocore.exceptions import ClientError
from pathlib import Path
from pedro import create_instance, main, add_instances_to_elb
from cleanup import cleanup
from util.constants import *


def _get_service_data():
    '''
    fetches for saved service data (vpc_id, instance_ids
    sg_ids, lb_name)
    '''
    try:
        d = pickle.load(Path('{}/.pccdata.p'.format(Path.home())).open('rb'))
        return d
    except IOError as e:
        print('Data file ({}/.pccdata.p) not found, are'.format(Path.home()) +
              ' you running instances already?')
        return False


def _append_new_instances(data, ids):
    [data['instance_ids'].append(x) for x in ids]
    pickle.dump(data, Path('{}/.pccdata.p'.format(Path.home())).open('wb'))


@click.group()
def cli(): pass


@cli.command()
@click.option('--force', '-f', default=False)
def terminate(force):
    print('terminating all instances and loadbalancer...')
    succ = _get_service_data() if not force else True
    if succ:
        cleanup()


@cli.command()
def start():
    print('starting service with {} instances on {} zone...'\
          .format(NUM_INSTANCES, GENERIC_ZONE))
    main()


@cli.command()
@click.option('--id', '-i', default=None, type=str,
              help='Remove instances with given id from the loadbalancer')
@click.option('--number', '-n', default=1, type=int,
              help='Number of instances to be removed from the loadbalancer')
def terminate_instances(id, number):
    if number < 1:
        print('are you really trying to add {} instances? get out!')
        return

    print('fetching existing data')
    data = _get_service_data()
    user_id = True

    if id is None:
        user_id = False
        ids = [choice(data['instance_ids']) for i in range(number) ]
        ids = [i['InstanceId'] for i in ids]
    else:
        ids = [id]

    try:
        ec2 = boto3.client('ec2')
    except:
        print('Have you configured awscli? Try $ aws configure')
        return

    print('terminating instances with ids:', ids)
    try:
        res = ec2.terminate_instances(InstanceIds=ids)
    except ClientError as e:
        print(e)
        return


@cli.command()
@click.option('--number', '-n', default=1, type=int,
              help='Add instances to load balancer',
              prompt='Number of instances')
def add_instances(number):
    ''' add instances to existing loadbalancer '''
    if number < 1:
        print('are you really trying to add {} instances? get out!')
        return

    print('fetching existing data')
    data = _get_service_data()
    if not data:
        return

    try:
        ec2 = boto3.client('ec2')
        elb = boto3.client('elb')
    except:
        print('Have you configured awscli? Try $ aws configure')
        return

    print('creating {} new instances'.format(number))
    instances = create_instance(ec2, IMAGE_ID, INSTANCE_TYPE,
                                data['sg_id'], number, ZONES)
    if len(instances) < number:
        print('Failed to create instances')
        return

    ids = [{'InstanceId': i['Instances'][0]['InstanceId']} for i in instances]

    print('adding {} new instances to elb'.format(number))
    inst = add_instances_to_elb(elb, data['lb_name'], ids)
    if not inst:
        print('Failed adding instances {} to existing ELB {}'\
              .format(ids, data['lb_name']))
        return

    _append_new_instances(data, ids)
