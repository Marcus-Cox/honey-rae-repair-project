"""View module for handling requests for serviceticket data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket


class ServiceTicketView(ViewSet):
    """Honey Rae API servicetickets view"""

    def list(self, request):
        """Handle GET requests to get all servicetickets

        Returns:
            Response -- JSON serialized list of servicetickets
        """

        service_tickets = ServiceTicket.objects.all()
        serialized = ServiceTicketSerializer(service_tickets, many=True)

        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()
            if "status" in request.query_params:
                if request.query_params['status'] == "done":
                    service_tickets = service_tickets.filter(
                        date_completed__isnull=False)

        else:
            service_tickets = ServiceTicket.objects.filter(
                customer__user=request.auth.user)

        serialized = ServiceTicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single serviceticket

        Returns:
            Response -- JSON serialized serviceticket record
        """

        serviceticket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(
            serviceticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)


class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for servicetickets"""
    class Meta:
        model = ServiceTicket
        fields = ('id', 'description', 'emergency',
                  'date_completed', 'employee', 'customer', )
        depth = 1
