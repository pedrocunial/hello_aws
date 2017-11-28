import boto3
from botocore.exceptions import ClientError


SG_NAME = 'apache_server_inbound'
SG_DESC = 'Security group for defining inbound ports for the apache server'


def delete_sg(sg_id):



ec2 = boto3.client('ec2')

res = ec2.describe_vpcs()
vpc_id = res.get('Vpcs', [{}])[0].get('VpcId', '')


# delete security group with name if exists
all_sg = ec2.describe_security_groups()
for sg in all_sg['SecurityGroups']:


try:

    res = ec2.create_security_group(
        GroupName=SG_NAME,
        Description=SG_DESC,
        VpcId=vpc_id
    )
    security_group_id = res['GroupId']
    print('Security group created {} in vpc {}'.format(security_group_id, vpc_id))

    data = ec2.authorize_security_group_ingress(
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

    print('Ingress Successfully set:', data)

except ClientError as e:
    print(e)
    exit(0)
