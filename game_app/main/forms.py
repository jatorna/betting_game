from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.conf import settings

# Create your forms here.


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.address = list(settings.ACCOUNTS.keys())[settings.NEXT_ADDRESS_INDEX]
        user.bets = 0
        if commit:
            user.save()

        # Transfer 100 tokens from owner to user address
        nonce = settings.W3.eth.getTransactionCount(list(settings.ACCOUNTS.keys())[0])
        greeting_transaction = settings.JTN_TOKEN.functions.transfer(user.address,
                                                                     100).buildTransaction(
            {"chainId": settings.CHAIN_ID, "from": list(settings.ACCOUNTS.keys())[0], "nonce": nonce}
        )
        signed_greeting_txn = settings.W3.eth.account.sign_transaction(
            greeting_transaction, private_key=settings.ACCOUNTS[list(settings.ACCOUNTS.keys())[0]]
        )

        tx_greeting_hash = settings.W3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
        tx_receipt = settings.W3.eth.wait_for_transaction_receipt(tx_greeting_hash)

        settings.NEXT_ADDRESS_INDEX += 1

        return user
