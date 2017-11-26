from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from libcloud.loadbalancer.providers import get_driver as elb_get_driver
from libcloud.loadbalancer.types import Provider as ELB_Provider
from libcloud.loadbalancer.base import Member, Algorithm

from os.path import expanduser


try:
    with open('{}/amazon.txt'.format(expanduser('~'), 'r')) as f:
        ACCESS_KEY = f.readline().strip()
        SECRET_KEY = f.readline().strip()
except IOError as e:
    print(e)
    exit(0)

IMAGE_ID = 'ami-da05a4a0'
SIZE_ID = 't2.micro'
REGION_ID = 'us-east-1'  # north virginia

# create instance
cls = get_driver(Provider.EC2)
driver = cls(ACCESS_KEY, SECRET_KEY, region=REGION_ID)

sizes = driver.list_sizes()
images = driver.list_images()

size = [s for s in sizes if s.id == SIZE_ID][0]
image = [i for i in images if i.id == IMAGE_ID][0]

node = driver.create_node(name='libcloud-test00', image=image, size=size)

## Load Balancer
LB_NAME = 'libcloud-lbtest00'
elb_cls = elb_get_driver(ELB_Provider.ELB)
elb_driver = elb_cls(ACCESS_KEY, SECRET_KEY, region=REGION_ID)

balancers = elb_driver.list_balancers()
print(balancers)

if len(balancers) == 0:   # create balancer
    members = (Member(None, '192.168.88.1', 8080),
               Member(None, '192.168.88.2', 8080))
    new_balancer = elb_driver.create_balancer(
        name=LB_NAME,
        algorithm=Algorithm.ROUND_ROBIN,
        port=80,
        protocol='http',
        members=members
    )
    print('created:')
    print(new_balancer)


# allocate and associate elastic IP
# elastic_ip = driver.ex_allocate_address()
# driver.ex_associate_address_with_node(node, elastic_ip)


