from scripts.helpful_scripts import get_owner_account, get_account
from scripts.deploy import deploy_jtn_token
from brownie import exceptions
import pytest


def test_deploy():
    account = get_owner_account()
    jtn_token = deploy_jtn_token()
    balance_owner = jtn_token.balanceOf(account, {"from": account})
    total_supply = jtn_token.totalSupply()

    assert total_supply == 10000000000000000
    assert total_supply == balance_owner


def test_transfer():
    account_owner = get_owner_account()
    account_user = get_account(1)
    jtn_token = deploy_jtn_token()

    with pytest.raises(exceptions.VirtualMachineError):
        jtn_token.transfer(account_user, 10000000000000001, {"from": account_owner})

    jtn_token.transfer(account_user, 200, {"from": account_owner})

    assert jtn_token.balanceOf(account_owner, {"from": account_owner}) == 10000000000000000 - 200
    assert jtn_token.balanceOf(account_user, {"from": account_owner}) == 200


def test_transfer_from():
    account_owner = get_owner_account()
    account_user = get_account(1)
    account_user2 = get_account(2)
    jtn_token = deploy_jtn_token()
    jtn_token.transfer(account_user, 200, {"from": account_owner})

    with pytest.raises(exceptions.VirtualMachineError):
        jtn_token.transferFrom(account_user, account_user2, 200, {"from": account_owner})

    jtn_token.approve(account_owner, 200, {"from": account_user})

    jtn_token.transferFrom(account_user, account_user2, 200, {"from": account_owner})

    assert jtn_token.balanceOf(account_user, {"from": account_owner}) == 0
    assert jtn_token.balanceOf(account_user2, {"from": account_owner}) == 200


def test_hold():
    account_owner = get_owner_account()
    account_user = get_account(1)
    jtn_token = deploy_jtn_token()
    jtn_token.transfer(account_user, 200, {"from": account_owner})

    with pytest.raises(exceptions.VirtualMachineError):
        jtn_token.hold(account_owner, 210, "testid", {"from": account_user})

    jtn_token.hold(account_owner, 5, "testid", {"from": account_user})

    assert jtn_token.balanceOf(account_user, {"from": account_user}) == 200 - 5
    assert jtn_token.netBalanceOf(account_user, {"from": account_owner}) == 200
    assert jtn_token.balanceOnHold(account_user, {"from": account_owner}) == 5


def test_hold_from():
    account_owner = get_owner_account()
    account_user = get_account(1)
    jtn_token = deploy_jtn_token()
    jtn_token.transfer(account_user, 200, {"from": account_owner})

    with pytest.raises(exceptions.VirtualMachineError):
        jtn_token.holdFrom(account_user, account_owner, 5, "testid", {"from": account_owner})

    jtn_token.holdApprove(account_owner, 5, {"from": account_user})
    jtn_token.holdFrom(account_user, account_owner, 5, "testid", {"from": account_owner})

    assert jtn_token.balanceOf(account_user, {"from": account_owner}) == 200 - 5


def test_execute_hold():
    account_owner = get_owner_account()
    account_user = get_account(1)
    jtn_token = deploy_jtn_token()
    jtn_token.transfer(account_user, 200, {"from": account_owner})
    jtn_token.hold(account_owner, 5, "testid", {"from": account_user})
    jtn_token.executeHold("testid", {"from": account_user})

    assert jtn_token.balanceOf(account_owner, {"from": account_owner}) == 10000000000000000 - 200 + 5
    assert jtn_token.balanceOf(account_user, {"from": account_user}) == 200 - 5
    assert jtn_token.netBalanceOf(account_user, {"from": account_owner}) == 200 - 5
    assert jtn_token.balanceOnHold(account_user, {"from": account_owner}) == 0


def test_remove_hold():
    account_owner = get_owner_account()
    account_user = get_account(1)
    jtn_token = deploy_jtn_token()
    jtn_token.transfer(account_user, 200, {"from": account_owner})
    jtn_token.hold(account_owner, 5, "testid", {"from": account_user})

    with pytest.raises(exceptions.VirtualMachineError):
        jtn_token.removeHold("testid", {"from": account_user})

    jtn_token.removeHold("testid", {"from": account_owner})

    assert jtn_token.balanceOf(account_owner, {"from": account_owner}) == 10000000000000000 - 200
    assert jtn_token.balanceOf(account_user, {"from": account_user}) == 200
    assert jtn_token.netBalanceOf(account_user, {"from": account_owner}) == 200
    assert jtn_token.balanceOnHold(account_user, {"from": account_owner}) == 0
