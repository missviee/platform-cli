import click
from ec2_manager import create_instance, start_instance, stop_instance, list_instances
from s3_manager import create_bucket, list_buckets

@click.group()
def cli():
    """Platform CLI - Self Service AWS Management"""

# EC2
@cli.command()
@click.option("--instance_type", default="t2.micro", help="EC2 instance type")
@click.option("--os_name", default="ubuntu", help="OS: ubuntu or amazon-linux")
def create_ec2(instance_type, os_name):
    """Create an EC2 instance"""
    create_instance(instance_type, os_name, profile="duvie-platform-cli", region="us-east-1")

@cli.command()
@click.option("--instance_id", prompt=True, help="ID of the instance to start")
def start_ec2(instance_id):
    """Start a CLI-created EC2 instance"""
    start_instance(instance_id, profile="duvie-platform-cli", region="us-east-1")

@cli.command()
@click.option("--instance_id", prompt=True, help="ID of the instance to stop")
def stop_ec2(instance_id):
    """Stop a CLI-created EC2 instance"""
    stop_instance(instance_id, profile="duvie-platform-cli", region="us-east-1")

@cli.command()
def list_ec2():
    """List CLI-created EC2 instances"""
    list_instances(profile="duvie-platform-cli", region="us-east-1")

# S3
@cli.command()
@click.option("--bucket_name", prompt=True, help="Name of S3 bucket")
@click.option("--public", default=False, type=bool, help="Public bucket? True/False")
def create_s3(bucket_name, public):
    """Create an S3 bucket"""
    create_bucket(bucket_name, public, profile="duvie-platform-cli", region="us-east-1")

@cli.command()
def list_s3():
    """List CLI-created S3 buckets"""
    list_buckets(profile="duvie-platform-cli", region="us-east-1")

if __name__ == "__main__":
    cli()
