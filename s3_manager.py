from botocore.exceptions import ClientError, BotoCoreError
from utils import default_tags, make_session, yes_no_prompt
from typing import List, Dict

def create_bucket(bucket_name: str, public: bool, profile: str, region: str):
    """
    Create an S3 bucket. Only allows CLI-managed buckets.
    If public=True, ask for explicit confirmation.
    """
    session = make_session(profile, region)
    s3 = session.client("s3")

    if public:
        if not yes_no_prompt(f"Bucket {bucket_name} will be public. Are you sure?"):
            print("Aborted: bucket creation canceled by user.")
            return

    try:
        kwargs = {"Bucket": bucket_name}
        if region != "us-east-1":
            kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}

        s3.create_bucket(**kwargs)

        # Add CLI tags
        s3.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={"TagSet": default_tags()}
        )

        print(f"Success: created bucket {bucket_name} ({'public' if public else 'private'}).")
    except (ClientError, BotoCoreError) as e:
        print(f"Error: failed to create bucket ({e}).")

def list_buckets(profile: str, region: str):
    """
    List only CLI-managed S3 buckets.
    """
    session = make_session(profile, region)
    s3 = session.client("s3")

    try:
        resp = s3.list_buckets()
        buckets = resp.get("Buckets", [])

        for b in buckets:
            try:
                # Get bucket tags
                tags_resp = s3.get_bucket_tagging(Bucket=b["Name"])
                tag_set: List[Dict[str, str]] = tags_resp.get("TagSet", [])

                # Only show buckets with all CLI default tags
                default_tags_list = default_tags()
                is_cli_bucket = all(
                    any(t['Key'] == d['Key'] and t['Value'] == d['Value'] for t in tag_set)
                    for d in default_tags_list
                )

                if is_cli_bucket:
                    print(f"{b['Name']}")

            except ClientError as e:
                # Skip buckets without tags or without permission
                if e.response['Error']['Code'] in ("NoSuchTagSet", "AccessDenied"):
                    continue
                else:
                    raise
    except (ClientError, BotoCoreError) as e:
        print(f"Error: could not list buckets ({e}).")
