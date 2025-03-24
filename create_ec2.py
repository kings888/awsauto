import boto3
import os
import sys

def create_ec2_instance():
    # Get variables from environment
    instance_name = os.environ.get('EC2_NAME')
    region = os.environ.get('EC2_REGION')
    volume_size = int(os.environ.get('EC2_VOLUME_SIZE'))
    vpc_id = os.environ.get('EC2_VPC_ID')
    public_ip = os.environ.get('EC2_PUBLIC_IP').lower() == 'true'
    instance_type = os.environ.get('EC2_INSTANCE_TYPE')

    # Validate required inputs
    if not all([instance_name, region, volume_size, vpc_id, instance_type]):
        print("Error: Missing required parameters")
        sys.exit(1)

    try:
        # Initialize AWS client
        ec2_client = boto3.client('ec2', region_name=region)
        ec2_resource = boto3.resource('ec2', region_name=region)

        # Get the latest Amazon Linux 2 AMI
        response = ec2_client.describe_images(
            Filters=[
                {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                {'Name': 'state', 'Values': ['available']}
            ],
            Owners=['amazon']
        )
        ami_id = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)[0]['ImageId']

        # Get subnet from VPC
        response = ec2_client.describe_subnets(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [vpc_id]
                }
            ]
        )
        if not response['Subnets']:
            print(f"Error: No subnets found in VPC {vpc_id}")
            sys.exit(1)
        subnet_id = response['Subnets'][0]['SubnetId']

        # Create instance
        instance = ec2_resource.create_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MaxCount=1,
            MinCount=1,
            NetworkInterfaces=[{
                'SubnetId': subnet_id,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': public_ip
            }],
            BlockDeviceMappings=[{
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'VolumeSize': volume_size,
                    'VolumeType': 'gp2'
                }
            }],
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{
                    'Key': 'Name',
                    'Value': instance_name
                }]
            }]
        )[0]

        # Wait for instance to be running
        instance.wait_until_running()
        
        print(f"Successfully created EC2 instance!")
        print(f"Instance ID: {instance.id}")
        print(f"Instance State: {instance.state['Name']}")
        if public_ip:
            instance.reload()  # Reload to get the public IP
            print(f"Public IP: {instance.public_ip_address}")
            
    except Exception as e:
        print(f"Error creating EC2 instance: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_ec2_instance()