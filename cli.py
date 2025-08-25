import click
from ec2_manager import create_instance, start_instance, stop_instance, list_instances
from s3_manager import create_bucket, list_buckets, upload_file, list_files
from route53_manager import create_zone, list_zones, list_records, create_record, update_record, delete_record

@click.group()
def cli():
    """Platform CLI - Self Service AWS Management"""
# EC2
@cli.command()
@click.option("--instance_type", default="t2.micro", help="EC2 instance type (t3.micro or t2.small only)")
@click.option("--os_name", default="ubuntu", help="OS: ubuntu or amazon-linux")
@click.option("--region", default="us-east-1", help="AWS region")
def create_ec2(instance_type, os_name, region):
    """Create an EC2 instance"""
    create_instance(instance_type, os_name, profile="duvie-platform-cli", region=region)

@cli.command()
@click.option("--instance_id", prompt=True, help="ID of the instance to start")
@click.option("--region", default="us-east-1", help="AWS region")
def start_ec2(instance_id, region):
    """Start a CLI-created EC2 instance"""
    start_instance(instance_id, profile="duvie-platform-cli", region=region)

@cli.command()
@click.option("--instance_id", prompt=True, help="ID of the instance to stop")
@click.option("--region", default="us-east-1", help="AWS region")
def stop_ec2(instance_id, region):
    """Stop a CLI-created EC2 instance"""
    stop_instance(instance_id, profile="duvie-platform-cli", region=region)

@cli.command()
@click.option("--region", default="us-east-1", help="AWS region")
def list_ec2(region):
    """List CLI-created EC2 instances"""
    list_instances(profile="duvie-platform-cli", region=region)

# S3
@cli.command()
@click.option("--bucket_name", prompt=True, help="Name of S3 bucket")
@click.option("--public", default=False, type=bool, help="Public bucket? True/False")
@click.option("--region", default="us-east-1", help="AWS region for the bucket")
def create_s3(bucket_name, public, region):
    """Create an S3 bucket"""
    create_bucket(bucket_name, public, profile="duvie-platform-cli", region=region)

@cli.command()
@click.option("--region", default="us-east-1", help="AWS region")
def list_s3(region):
    """List CLI-created S3 buckets"""
    list_buckets(profile="duvie-platform-cli", region=region)

@cli.command()
@click.option("--bucket_name", prompt=True, help="Target S3 bucket")
@click.option("--file_path", prompt=True, help="Path to local file")
@click.option("--object_name", default=None, help="S3 object name (optional)")
@click.option("--region", default="us-east-1", help="AWS region")
def upload_s3(bucket_name, file_path, object_name, region):
    """Upload a file to a CLI-created S3 bucket"""
    upload_file(bucket_name, file_path, profile="duvie-platform-cli", region=region, object_name=object_name)

@cli.command()
@click.option("--bucket_name", prompt=True, help="S3 bucket to list files from")
@click.option("--region", default="us-east-1", help="AWS region")
def list_s3_files(bucket_name, region):
    """List files in a CLI-created S3 bucket"""
    list_files(bucket_name, profile="duvie-platform-cli", region=region)

# Route53
@cli.command()
@click.option("--zone_name", prompt=True, help="Domain name for the hosted zone (example.com)")
@click.option("--region", default="us-east-1", help="AWS region")
def create_route53(zone_name, region):
    """Create a Route53 DNS zone"""
    create_zone(zone_name, profile="duvie-platform-cli", region=region)

@cli.command()
@click.option("--region", default="us-east-1", help="AWS region")
def list_route53(region):
    """List CLI-created Route53 DNS zones"""
    list_zones(profile="duvie-platform-cli", region=region)

# Route53 Records
@cli.command()
@click.option("--zone_id", prompt=True, help="Hosted zone ID")
def list_records_cli(zone_id):
    """List records in a CLI-created zone"""
    list_records(zone_id, profile="duvie-platform-cli", region="us-east-1")

@cli.command()
@click.option("--zone_id", prompt=True, help="Hosted zone ID")
@click.option("--name", prompt=True, help="Record name")
@click.option("--type_", prompt=True, help="Record type (A, CNAME, etc.)")
@click.option("--value", prompt=True, help="Record value")
@click.option("--ttl", default=300, help="Record TTL")
def create_record_cli(zone_id, name, type_, value, ttl):
    """Create a record in a CLI-managed zone"""
    create_record(zone_id, name, type_, value, ttl, profile="duvie-platform-cli", region="us-east-1")

@cli.command()
@click.option("--zone_id", prompt=True, help="Hosted zone ID")
@click.option("--name", prompt=True, help="Record name")
@click.option("--type_", prompt=True, help="Record type")
@click.option("--value", prompt=True, help="Record value")
@click.option("--ttl", default=300, help="Record TTL")
def update_record_cli(zone_id, name, type_, value, ttl):
    """Update a record in a CLI-managed zone"""
    update_record(zone_id, name, type_, value, ttl, profile="duvie-platform-cli", region="us-east-1")

@cli.command()
@click.option("--zone_id", prompt=True, help="Hosted zone ID")
@click.option("--name", prompt=True, help="Record name")
@click.option("--type_", prompt=True, help="Record type")
@click.option("--value", prompt=True, help="Record value")
def delete_record_cli(zone_id, name, type_, value):
    """Delete a record in a CLI-managed zone"""
    delete_record(zone_id, name, type_, value, profile="duvie-platform-cli", region="us-east-1")

if __name__ == "__main__":
    cli()
