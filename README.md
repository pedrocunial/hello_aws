# hello_aws
To install just run:
    `pip3 install -e .`

Then, make sure you have awscli configured correctly in your machine (both secret key and access id) with the region set to us-east-1 (north virginia). You can do that by running:
    `aws configure`

With all of that done, you should be able to access the pccli command anywhere in your machine. Use `pccli start` to start the service, `pccli terminate` to terminate it, `pccli add_instances` to add instances to the service and `pccli terminate_instance` to remove instances from the client. For further informations, use `pccli <command_name> --help`.
