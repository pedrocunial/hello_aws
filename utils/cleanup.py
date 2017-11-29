import boto3
import sys

from botocore.exceptions import ClientError

sys.path.append('..')

from pedro import LB_NAME


def delete_elb(client, name):
    try:
        res = client.delete_load_balancer(LoadBalancerName=name)
        return res
    except ClientError as e:
        print(e)
        return None


def cleanup():
    elb = boto3.client('elb')
    res = delete_elb(elb, LB_NAME)
