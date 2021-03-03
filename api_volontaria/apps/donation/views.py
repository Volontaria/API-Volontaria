import stripe
from requests import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(['POST'])
def donate(request):
    data = request.data
    print(data['email'])
    payment_intent = stripe.PaymentIntent.create(
        amount=data['amount'], currency='cad',

        payment_method=data['payment_method_id'],
        confirmation_method='manual',
        confirm=True,
        receipt_email=data['email'])
    return Response(status=status.HTTP_200_OK, data=payment_intent)


