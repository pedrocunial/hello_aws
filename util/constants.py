# security group
SG_NAME = 'apache_server_inbound'
SG_DESC = 'Security group for defining inbound ports for the apache server'

# instance
IMAGE_ID = 'ami-5f990425'
INSTANCE_TYPE = 't2.micro'
NUM_INSTANCES = 5
ZONES = [ 'us-east-1a', 'us-east-1b', 'us-east-1c' ]  # different zones for the elb
GENERIC_ZONE = 'us-east-1'

# ELB
I_PORT = 80
LB_PORT = 80
LB_NAME = 'gilftl-loadbalancer'
