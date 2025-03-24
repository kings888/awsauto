from flask import Flask, render_template, request, jsonify
import boto3
import os
from datetime import datetime

app = Flask(__name__)

def create_ec2_instance(params):
    try:
        # Initialize AWS client
        ec2_client = boto3.client('ec2', 
                                region_name=params['region'],
                                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
        ec2_resource = boto3.resource('ec2', 
                                    region_name=params['region'],
                                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

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
        subnets = list(ec2_resource.vpc(params['vpc_id']).subnets.all())
        if not subnets:
            return {"error": f"No subnets found in VPC {params['vpc_id']}"}
        subnet_id = subnets[0].id

        # Create instance
        instance = ec2_resource.create_instances(
            ImageId=ami_id,
            InstanceType=params['instance_type'],
            MaxCount=1,
            MinCount=1,
            NetworkInterfaces=[{
                'SubnetId': subnet_id,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': params['need_public_ip']
            }],
            BlockDeviceMappings=[{
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'VolumeSize': int(params['volume_size']),
                    'VolumeType': 'gp2'
                }
            }],
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{
                    'Key': 'Name',
                    'Value': params['instance_name']
                }]
            }]
        )[0]

        # Wait for instance to be running
        instance.wait_until_running()
        instance.reload()  # Reload to get the public IP if assigned

        result = {
            "success": True,
            "instance_id": instance.id,
            "state": instance.state['Name']
        }
        
        if params['need_public_ip'] and instance.public_ip_address:
            result["public_ip"] = instance.public_ip_address

        return result

    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_instance', methods=['POST'])
def create_instance():
    try:
        params = {
            'instance_name': request.form['instance_name'],
            'region': request.form['region'],
            'volume_size': request.form['volume_size'],
            'vpc_id': request.form['vpc_id'],
            'need_public_ip': request.form['need_public_ip'] == 'true',
            'instance_type': request.form['instance_type']
        }
        
        result = create_ec2_instance(params)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True) 