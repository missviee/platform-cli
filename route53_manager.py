import boto3
from botocore.exceptions import ClientError, BotoCoreError
from utils import default_tags, make_session

def get_resource_id(full_id: str) -> str:
    """Extract the actual resource ID from /hostedzone/..."""
    return full_id.split('/')[-1]

# zone functions
def create_zone(zone_name: str, profile: str, region: str):
    """Create a Route53 hosted zone."""
    session = make_session(profile, region)
    r53 = session.client("route53")

    try:
        resp = r53.create_hosted_zone(
            Name=zone_name,
            CallerReference=zone_name,
            HostedZoneConfig={
                "Comment": "CLI-created zone",
                "PrivateZone": False
            }
        )

        # Add CLI tags
        r53.change_tags_for_resource(
            ResourceType="hostedzone",
            ResourceId=get_resource_id(resp['HostedZone']['Id']),
            AddTags=default_tags()
        )

        print(f"Success: created zone {zone_name} ({resp['HostedZone']['Id']})")
    except (ClientError, BotoCoreError) as e:
        print(f"Error: failed to create zone ({e})")

def list_zones(profile: str, region: str):
    """List only CLI-created Route53 zones."""
    session = make_session(profile, region)
    r53 = session.client("route53")

    try:
        resp = r53.list_hosted_zones()
        zones = resp.get("HostedZones", [])
        for z in zones:
            try:
                tags_resp = r53.list_tags_for_resource(
                    ResourceType="hostedzone",
                    ResourceId=get_resource_id(z['Id'])
                )
                tag_set = tags_resp.get("ResourceTagSet", {}).get("Tags", [])
                if all(any(t['Key'] == d['Key'] and t['Value'] == d['Value'] for t in tag_set)
                       for d in default_tags()):
                    print(f"{z['Name']} - {z['Id']}")
            except ClientError as e:
                if e.response['Error']['Code'] == "AccessDenied":
                    continue
                else:
                    raise
    except (ClientError, BotoCoreError) as e:
        print(f"Error: could not list zones ({e})")

# record functions
def is_cli_zone(r53, zone_id):
    """Check if the hosted zone is CLI-created"""
    try:
        tags_resp = r53.list_tags_for_resource(ResourceType="hostedzone", ResourceId=get_resource_id(zone_id))
        tag_set = tags_resp.get("ResourceTagSet", {}).get("Tags", [])
        return all(any(t['Key'] == d['Key'] and t['Value'] == d['Value'] for t in tag_set)
                   for d in default_tags())
    except ClientError:
        return False

def list_records(zone_id: str, profile: str, region: str):
    """List records of a CLI-created zone"""
    session = make_session(profile, region)
    r53 = session.client("route53")

    if not is_cli_zone(r53, zone_id):
        print(f"Zone {zone_id} is not managed by CLI.")
        return

    try:
        resp = r53.list_resource_record_sets(HostedZoneId=get_resource_id(zone_id))
        for record in resp.get("ResourceRecordSets", []):
            print(f"{record['Name']} - {record['Type']} - {record.get('TTL', '')} - {record.get('ResourceRecords', '')}")
    except (ClientError, BotoCoreError) as e:
        print(f"Error: could not list records ({e})")

def create_record(zone_id: str, name: str, type_: str, value: str, ttl: int, profile: str, region: str):
    """Create a record in a CLI-managed zone"""
    session = make_session(profile, region)
    r53 = session.client("route53")

    if not is_cli_zone(r53, zone_id):
        print(f"Zone {zone_id} is not managed by CLI.")
        return

    try:
        r53.change_resource_record_sets(
            HostedZoneId=get_resource_id(zone_id),
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": name,
                            "Type": type_,
                            "TTL": ttl,
                            "ResourceRecords": [{"Value": value}]
                        }
                    }
                ]
            }
        )
        print(f"Success: created record {name} ({type_}) in {zone_id}")
    except (ClientError, BotoCoreError) as e:
        print(f"Error: failed to create record ({e})")

def update_record(zone_id: str, name: str, type_: str, value: str, ttl: int, profile: str, region: str):
    """Update a record in a CLI-managed zone"""
    session = make_session(profile, region)
    r53 = session.client("route53")

    if not is_cli_zone(r53, zone_id):
        print(f"Zone {zone_id} is not managed by CLI.")
        return

    try:
        r53.change_resource_record_sets(
            HostedZoneId=get_resource_id(zone_id),
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": name,
                            "Type": type_,
                            "TTL": ttl,
                            "ResourceRecords": [{"Value": value}]
                        }
                    }
                ]
            }
        )
        print(f"Success: updated record {name} ({type_}) in {zone_id}")
    except (ClientError, BotoCoreError) as e:
        print(f"Error: failed to update record ({e})")

def delete_record(zone_id: str, name: str, type_: str, value: str, profile: str, region: str):
    """Delete a record in a CLI-managed zone"""
    session = make_session(profile, region)
    r53 = session.client("route53")

    if not is_cli_zone(r53, zone_id):
        print(f"Zone {zone_id} is not managed by CLI.")
        return

    try:
        r53.change_resource_record_sets(
            HostedZoneId=get_resource_id(zone_id),
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": name,
                            "Type": type_,
                            "TTL": 300,
                            "ResourceRecords": [{"Value": value}]
                        }
                    }
                ]
            }
        )
        print(f"Success: deleted record {name} ({type_}) in {zone_id}")
    except (ClientError, BotoCoreError) as e:
        print(f"Error: failed to delete record ({e})")
