from brownie import accounts


def get_owner_account():
    return accounts[0]


def get_account(index):
    return accounts[index]