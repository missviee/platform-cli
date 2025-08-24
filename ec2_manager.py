from botocore.exceptions import ClientError, BotoCoreError
from utils import default_tags, make_session

ALLOWED_INSTANCE_TYPES = {"t3.micro", "t2.small"}
MAX_RUNNING = 2

AMI_MAP = {
    "ubuntu": "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id",
    "amazon-linux": "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64"
}

def _latest_ami(os_name: str, session):
    """
    Return the latest AMI ID for the chosen OS using SSM public parameters.
    os_name: 'ubuntu' or 'amazon-linux'
    """
    ssm = session.client("ssm")
    os_key = os_name.strip().lower()

    if os_key not in AMI_MAP:
        raise ValueError("Invalid OS. Use 'ubuntu' or 'amazon-linux'.")

    param = AMI_MAP[os_key]
    resp = ssm.get_parameter(Name=param)
    return resp["Parameter"]["Value"]

def _count_running_cli_instances(session) -> int:
    ec2 = session.client("ec2")
    filters = [
        {"Name": "tag:CreatedBy", "Values": ["platform-cli"]},
        {"Name": "tag:Owner", "Values": ["duvie"]},
        {"Name": "instance-state-name", "Values": ["running"]},
    ]
    resp = ec2.describe_instances(Filters=filters)
    return sum(len(r["Instances"]) for r in resp.get("Reservations", []))

def create_instance(instance_type: str, os_name: str, profile: str, region: str):
    """
    Create an EC2 instance following exercise rules:
    - Allowed instance types: t3.micro, t2.small
    - Hard cap of 2 running CLI-created instances
    - AMI: latest Ubuntu or Amazon Linux
    - Tags: CreatedBy=platform-cli, Owner=duvie
    """
    if instance_type not in ALLOWED_INSTANCE_TYPES:
        print("Error: instance type must be 't3.micro' or 't2.small'.")
        return

    session = make_session(profile, region)

    running = _count_running_cli_instances(session)
    if running >= MAX_RUNNING:
        print("Error: cap reached. You already have 2 running instances created by this CLI.")
        return

    try:
        ami_id = _latest_ami(os_name, session)
    except (ClientError, BotoCoreError, ValueError) as e:
        print(f"Error: could not resolve latest AMI ({e}).")
        return

    ec2 = session.client("ec2")
    try:
        resp = ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {"ResourceType": "instance", "Tags": default_tags()}
            ],
        )
        inst = resp["Instances"][0]
        inst_id = inst["InstanceId"]
        state = inst.get("State", {}).get("Name", "pending")
        print(f"Success: created instance {inst_id} (state: {state}).")
    except (ClientError, BotoCoreError) as e:
        print(f"Error: failed to create instance ({e}).")
