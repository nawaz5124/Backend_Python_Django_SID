import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.serializers.stripe_serializer import StripePaymentIntentSerializer
from api.utils.stripe import create_payment_intent
from stripe.error import CardError, RateLimitError, InvalidRequestError
from api.utils.jwt_custom_authentication import JWTAuthentication  #  Custom JWT authentication
from api.models.stripe_intent_models import StripeIntentModel  #  Import the new model

logger = logging.getLogger(__name__)

class StripePaymentIntentAPIView(APIView):
    """
    Handles Stripe PaymentIntent creation with session-based tracking.
    Requires authentication.
    """

    authentication_classes = [JWTAuthentication]  #  Apply authentication

    def post(self, request):
        """
        Processes a Stripe PaymentIntent request.
        Checks if a PaymentIntent already exists for the session_id.
        """

        logger.info(f"[Stripe View] Authenticated User: {request.user}")

        #  Step 1: Validate request payload
        serializer = StripePaymentIntentSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"[Stripe View] Validation failed: {serializer.errors}")
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data
        amount = validated_data["amount"]
        currency = validated_data["currency"]
        session_id = validated_data.get("session_id")  #  This is the new addition for session tracking

        try:
            #  Step 2: Check if there's already an intent for this session
            existing_session = StripeIntentModel.objects.filter(session_id=session_id).first()

            if existing_session:
                logger.info(f"[Stripe View] Existing PaymentIntent found for session: {session_id}")
                return Response(
                    {
                        "session_id": existing_session.session_id,
                        "client_secret": existing_session.client_secret,
                        "payment_intent_id": existing_session.payment_intent_id,
                        "status": existing_session.status,
                        "message": "Existing PaymentIntent retrieved successfully!",
                    },
                    status=status.HTTP_200_OK,
                )

            #  Step 3: No existing session, create a new PaymentIntent
            payment_intent = create_payment_intent(amount, currency)
            logger.info(f" Stripe PaymentIntent created: {payment_intent['id']} for session: {session_id}")

            #  Step 4: Save PaymentIntent with session_id in database
            stripe_session = StripeIntentModel.objects.create(
                session_id=session_id,
                payment_intent_id=payment_intent["id"],
                client_secret=payment_intent["client_secret"],
                status=payment_intent["status"],
                amount=amount / 100,  # Store amount in pounds (if amount is in pence)
                currency=currency,
            )
            logger.info(f"[Stripe View] PaymentIntent saved to database for session: {session_id}")

            return Response(
                {
                    "session_id": stripe_session.session_id,
                    "client_secret": stripe_session.client_secret,
                    "payment_intent_id": stripe_session.payment_intent_id,
                    "status": stripe_session.status,
                    "message": "PaymentIntent created successfully!",
                },
                status=status.HTTP_201_CREATED,
            )

        except CardError as e:
            logger.error(f"[Stripe View] Card declined: {e.user_message}")
            return Response({"error": e.user_message}, status=status.HTTP_400_BAD_REQUEST)
        except RateLimitError as e:
            logger.error(f"[Stripe View] Rate limit exceeded: {str(e)}")
            return Response({"error": "Too many requests, please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except InvalidRequestError as e:
            logger.error(f"[Stripe View] Invalid request to Stripe: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"[Stripe View] Unexpected error: {str(e)}")
            return Response(
                {"error": "An internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RetrievePaymentIntentBySessionAPIView(APIView):
    """
    Retrieve an existing PaymentIntent by session_id to support resuming abandoned payments.
    Authentication can be optional based on your use case.
    """

    authentication_classes = [JWTAuthentication]  #  Optional, remove if unauthenticated retrieval is allowed

    def get(self, request, session_id):
        """
        Retrieve a PaymentIntent if it exists for a given session_id.
        """

        try:
            stripe_session = StripeIntentModel.objects.get(session_id=session_id)
            logger.info(f"[Stripe View] Retrieved PaymentIntent for session: {session_id}")

            return Response(
                {
                    "session_id": stripe_session.session_id,
                    "client_secret": stripe_session.client_secret,
                    "payment_intent_id": stripe_session.payment_intent_id,
                    "status": stripe_session.status,
                    "message": "PaymentIntent retrieved successfully!",
                },
                status=status.HTTP_200_OK,
            )

        except StripeIntentModel.DoesNotExist:
            logger.warning(f"[Stripe View] No PaymentIntent found for session: {session_id}")
            return Response(
                {"error": "No PaymentIntent found for this session."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"[Stripe View] Error retrieving PaymentIntent for session {session_id}: {str(e)}")
            return Response(
                {"error": "An internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )