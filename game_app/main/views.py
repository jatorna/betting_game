from django.shortcuts import render, redirect
from .forms import NewUserForm
from .models import CurrentBet, User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from web3 import exceptions
import random


@login_required
def userpage(request):
    balance = settings.JTN_TOKEN.functions.balanceOf(request.user.address).call()
    bet_amount = settings.JTN_TOKEN.functions.balanceOnHold(request.user.address).call()
    return render(request, 'main/user.html', {'Balance': balance, 'Bet_Amount': bet_amount})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("main:userpage")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="main/register.html", context={"register_form": form})


def login_request(request):

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect("main:userpage")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="main/login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    return redirect("main:login")


def bet_request(request):
    if request.method == "POST":

        if CurrentBet.objects.filter(username=request.user.username).count() >= 1:
            messages.error(request, "This user has already bet. Wait for other players.")
            return redirect("main:userpage")

        nonce = settings.W3.eth.getTransactionCount(request.user.address)
        holdId = request.user.username + str(request.user.bets) + str(random.randint(0, 1000))

        try:
            greeting_transaction = settings.JTN_TOKEN.functions.hold(list(settings.ACCOUNTS.keys())[0], 5, holdId).\
            buildTransaction({"chainId": settings.CHAIN_ID, "from": request.user.address, "nonce": nonce})

        except exceptions.ContractLogicError as error:
            messages.error(request, "Error: " + str(error))
            return redirect("main:userpage")

        signed_greeting_txn = settings.W3.eth.account.sign_transaction(
            greeting_transaction, private_key=settings.ACCOUNTS[request.user.address]
        )

        tx_greeting_hash = settings.W3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
        tx_receipt = settings.W3.eth.wait_for_transaction_receipt(tx_greeting_hash)

        request.user.bets += 1
        request.user.save()

        bet = CurrentBet(username=request.user.username, amount=5, holdId=holdId)
        bet.save()

        messages.success(request, "Bet done successfully.")

        if CurrentBet.objects.all().count() > 3:
            players = []
            for bet in CurrentBet.objects.all():
                players.append(bet.username)
                user = User.objects.get(username=bet.username)

                # Execute Hold

                nonce = settings.W3.eth.getTransactionCount(user.address)
                greeting_transaction = settings.JTN_TOKEN.functions.executeHold(bet.holdId). \
                        buildTransaction({"chainId": settings.CHAIN_ID, "from": user.address, "nonce": nonce})

                signed_greeting_txn = settings.W3.eth.account.sign_transaction(
                    greeting_transaction, private_key=settings.ACCOUNTS[user.address]
                )
                tx_greeting_hash = settings.W3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
                tx_receipt = settings.W3.eth.wait_for_transaction_receipt(tx_greeting_hash)

            winner = User.objects.get(username=players[random.randint(0, 3)])

            messages.info(request, "Game complete. The winner is: " + winner.username)

            # Execute transfer to the winner

            nonce = settings.W3.eth.getTransactionCount(list(settings.ACCOUNTS.keys())[0])
            greeting_transaction = settings.JTN_TOKEN.functions.transfer(winner.address, 20). \
                buildTransaction({"chainId": settings.CHAIN_ID, "from": list(settings.ACCOUNTS.keys())[0], "nonce":
                nonce})

            signed_greeting_txn = settings.W3.eth.account.sign_transaction(
                greeting_transaction, private_key=settings.ACCOUNTS[list(settings.ACCOUNTS.keys())[0]]
            )
            tx_greeting_hash = settings.W3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
            tx_receipt = settings.W3.eth.wait_for_transaction_receipt(tx_greeting_hash)

            CurrentBet.objects.all().delete()

        return redirect("main:userpage")