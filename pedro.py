import boto3
import pickle

from botocore.client import Config
from pathlib import Path
from botocore.exceptions import ClientError
from random import choice
from util.constants import *


def delete_sg(client, id_, name):
    ''' delete security group '''
    try:
        res = client.delete_security_group(
            GroupId=str(id_),
            GroupName=str(name),
            DryRun=False
        )
        return res
    except ClientError as e:
        print(e)
        return False


def create_sg(client, name, desc, vpc_id):
    ''' create security group with given name, description and vpc_id '''
    try:
        res = client.create_security_group(
            GroupName=name,
            Description=desc,
            VpcId=vpc_id
        )
        security_group_id = res['GroupId']
        print('security group created {} in vpc {}'.format(security_group_id, vpc_id))

        data = client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{ 'CidrIp': '0.0.0.0/0' }]},
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{ 'CidrIp': '0.0.0.0/0' }]}
            ])

        print('ingress Successfully set for SG with id', security_group_id)
        return security_group_id
    except ClientError as e:
        print(e)
        return False


def create_instance(client, image_id, type_, sg_id, n, zones):
    '''
    create ec2 instance
    note that this function could have used the Min and MaxCount
    args to create multiple instances in one request, but they
    would all be in the same availability zone, which is not wanted
    '''
    instances = []
    try:
        for i in range(n):
            instance = client.run_instances(
                ImageId=str(image_id),
                InstanceType=str(type_),
                Placement = { 'AvailabilityZone': str(choice(zones)) },
                MinCount=1,
                MaxCount=1,
                DryRun=False,
                SecurityGroupIds=[ str(sg_id) ]
            )
            print('created Instance:', instance['Instances'][0]['InstanceId'])
            instances.append(instance)
    except ClientError as e:
        print(e)
    finally:
        return instances


def create_elb(client, name, zones, iport, lbport):
    '''
    create new elastic load balancer
    returns the DNS name for the ELB
    '''
    try:
        res = client.create_load_balancer(
            LoadBalancerName=name,
            Listeners=[
                {'Protocol': 'HTTP',
                 'LoadBalancerPort': lbport,
                 'InstancePort': iport}
            ],
            AvailabilityZones=zones
        )
        print('created elasic load balancer with name', name)
        return res['DNSName']
    except ClientError as e:
        print(e)
        return False


def add_instances_to_elb(client, elb, instances):
    '''
    add listed instances to elb by their ids
    '''
    try:
        res = client.register_instances_with_load_balancer(
            LoadBalancerName=elb,
            Instances=instances
        )
        print('added {} instances to loadbalancer {}'\
              .format(len(instances), elb))
        return res
    except ClientError as e:
        print(e)
        return False


def save_service_data(instance_ids, sg_id, vpc_id, lb_name):
    print('saving service data into {}/.pccdata.p'.format(Path.home()))
    pickle.dump({
        'instance_ids': instance_ids,
        'sg_id': sg_id,
        'vpc_id': vpc_id,
        'lb_name': lb_name,
    }, Path('{}/.pccdata.p'.format(Path.home())).open('wb'))


def main():
    #### Begin of script
    try:
        config = Config(connect_timeout=50, read_timeout=70)  # insper net...
        ec2 = boto3.client('ec2', config=config)
    except:
        print('Have you configured awscli? Try $ aws configure')
        return

    ### Configure Security Groups
    res = ec2.describe_vpcs()
    vpc_id = res.get('Vpcs', [{}])[0].get('VpcId', '')

    # delete security group with name if exists
    all_sg = ec2.describe_security_groups()
    for sg in all_sg['SecurityGroups']:
        sgname = sg['GroupName']
        if sgname.strip() == SG_NAME:
            succ = delete_sg(ec2, sg['GroupId'], sgname)
            if not succ:
                print('Deleting SG {} failed'.format(sgname))
                exit(0)

    # create new security groups
    sg_id = create_sg(ec2, SG_NAME, SG_DESC, vpc_id)
    if not sg_id:
        print('Failed to create SG with name', SG_NAME)
        exit(0)

    ### Create instance using custom image and add it to the SG
    instances = create_instance(ec2, IMAGE_ID, INSTANCE_TYPE, sg_id,
                        NUM_INSTANCES, ZONES)
    if len(instances) < NUM_INSTANCES:
        print('Failed to create instances with image', IMAGE_ID)


    ### ElasticLoadBalancing (ELB)
    elb = boto3.client('elb', config=config)

    dns_name = create_elb(elb, LB_NAME, ZONES, I_PORT, LB_PORT)
    if not dns_name:
        print('Failed creating LB with name', LB_NAME)
        exit(0)

    instance_ids = [{'InstanceId': i['Instances'][0]['InstanceId']} for i in instances]
    inst = add_instances_to_elb(elb, LB_NAME, instance_ids)
    if not inst:
        print('Failed adding instances {} to existing ELB'.format(instance_ids))

    save_service_data(instance_ids, sg_id, vpc_id, LB_NAME)


if __name__ == '__main__':
    main()
