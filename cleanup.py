import boto3

from botocore.exceptions import ClientError
from pedro import LB_NAME, SG_NAME
from pprint import pprint
from pathlib import Path


def delete_elb(client, name):
    try:
        res = client.delete_load_balancer(LoadBalancerName=name)
        return res
    except ClientError as e:
        print(e)
        return False


def format_idlist(instances):
    ids = []
    for inst in instances['Reservations']:
        for i in inst['Instances']:
            ids.append(i['InstanceId'])
    return ids


def delete_sg_instances(client, sg_name):
    try:
        instances = client.describe_instances(
            Filters=[{
                'Name': 'instance.group-name',
                'Values': [sg_name]
            }])
        res = client.terminate_instances(InstanceIds=format_idlist(instances))
        return True
    except ClientError as e:
        print(e)
        return False


def cleanup():
    elb = boto3.client('elb')
    ec2 = boto3.client('ec2')

    succ = delete_sg_instances(ec2, 'apache_server_inbound')
    res = delete_elb(elb, LB_NAME)

    # remove data file
    Path('{}/.pccdata.p'.format(Path.home())).unlink()
    print(res)


if __name__ == '__main__':
    cleanup()
