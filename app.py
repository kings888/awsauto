from flask import Flask, render_template, request, jsonify
import boto3
import os
from datetime import datetime

app = Flask(__name__)

def create_ec2_instance(params):
    try:
        logs = []
        def log_message(message):
            logs.append(message)
            
        # Initialize AWS client
        log_message("正在初始化AWS客户端...")
        ec2_client = boto3.client('ec2', 
                                region_name=params['region'],
                                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
        ec2_resource = boto3.resource('ec2', 
                                    region_name=params['region'],
                                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

        # Get the latest Amazon Linux 2 AMI
        log_message("正在获取最新的Amazon Linux 2 AMI...")
        response = ec2_client.describe_images(
            Filters=[
                {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                {'Name': 'state', 'Values': ['available']}
            ],
            Owners=['amazon']
        )
        ami_id = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)[0]['ImageId']
        log_message(f"已选择AMI: {ami_id}")

        # Get subnet from VPC
        log_message(f"正在从VPC {params['vpc_id']} 获取子网信息...")
        response = ec2_client.describe_subnets(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [params['vpc_id']]
                }
            ]
        )
        if not response['Subnets']:
            return {"error": f"No subnets found in VPC {params['vpc_id']}", "logs": logs}
        subnet_id = response['Subnets'][0]['SubnetId']
        log_message(f"已选择子网: {subnet_id}")

        # Create instance
        log_message("开始创建EC2实例...")
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
                'Tags': [
                    {'Key': 'Name', 'Value': params['instance_name']},
                    {'Key': 'Owner', 'Value': params['owner']},
                    {'Key': 'Team', 'Value': params['team']},
                    {'Key': 'ApplicationName', 'Value': params['application_name']},
                    {'Key': 'Environment', 'Value': params['environment']}
                ]
            }]
        )[0]

        # Wait for instance to be running
        log_message("等待实例启动...")
        instance.wait_until_running()
        instance.reload()  # Reload to get the public IP if assigned
        log_message("实例已成功启动！")

        result = {
            "success": True,
            "instance_id": instance.id,
            "state": instance.state['Name'],
            "logs": logs
        }
        
        if params['need_public_ip'] and instance.public_ip_address:
            result["public_ip"] = instance.public_ip_address

        return result

    except Exception as e:
        return {"error": str(e), "logs": logs}

def get_aws_regions():
    try:
        # Initialize AWS client in a default region
        ec2_client = boto3.client('ec2',
                                region_name='us-east-1',
                                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
        
        # Get all regions
        response = ec2_client.describe_regions()
        regions = [{
            'id': region['RegionName'],
            'name': region['RegionName']
        } for region in response['Regions']]
        
        # Sort regions by name
        regions.sort(key=lambda x: x['name'])
        return regions
    except Exception as e:
        print(f"Error getting AWS regions: {str(e)}")
        return []

@app.route('/')
def index():
    regions = get_aws_regions()
    return render_template('index.html', regions=regions)

@app.route('/create_instance', methods=['POST'])
def create_instance():
    try:
        params = {
            'instance_name': request.form['instance_name'],
            'region': request.form['region'],
            'volume_size': request.form['volume_size'],
            'vpc_id': request.form['vpc_id'],
            'need_public_ip': request.form['need_public_ip'] == 'true',
            'instance_type': request.form['instance_type'],
            'owner': request.form['owner'],
            'team': request.form['team'],
            'application_name': request.form['application_name'],
            'environment': request.form['environment']
        }
        
        result = create_ec2_instance(params)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)