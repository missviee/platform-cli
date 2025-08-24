import boto3

# Tags
CREATED_BY = "platform-cli"
OWNER = "duvie"

def default_tags():
    """Return standard tags for CLI-created resources"""
    return [
        {'Key': 'CreatedBy', 'Value': CREATED_BY},
        {'Key': 'Owner', 'Value': OWNER},
    ]

def is_cli_resource(tags):
    """Return True if resource tags match CLI-created tags"""
    if not tags:
        return False
    tag_dict = {t['Key']: t['Value'] for t in tags}
    return tag_dict.get('CreatedBy') == CREATED_BY and tag_dict.get('Owner') == OWNER

def make_session(profile, region):
    """Create a boto3 session with given profile and region"""
    return boto3.Session(profile_name=profile, region_name=region)

def yes_no_prompt(message):
    """Ask user yes/no, return True only if yes"""
    answer = input(f"{message} (yes/no): ").strip().lower()
    return answer == "yes"
