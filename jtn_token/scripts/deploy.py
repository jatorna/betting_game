from brownie import JtnToken
from scripts.helpful_scripts import get_owner_account


def deploy_jtn_token():
    account = get_owner_account()
    jtn_token = JtnToken.deploy(
        {"from": account}, publish_source=False)

    return jtn_token


def main():
    deploy_jtn_token()