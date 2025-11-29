from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Match, Team
from .serializers import MatchSerializer



@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"error": "Username and password required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.filter(username=username).first()
    if user and user.check_password(password):
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username})

    return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def match_list_create(request):
    if request.method == 'GET':
        matches = Match.objects.filter(created_by=request.user)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)

    # ---- POST create ----
    data = request.data.copy()

    # Validate overs
    overs = data.get('overs')
    if overs is None or str(overs).strip() == '':
        return Response({"error": "overs is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Accept either team IDs or team names.
    team1_id = data.get('team1')
    team2_id = data.get('team2')
    team1_name = data.get('team1_name')
    team2_name = data.get('team2_name')

    # Resolve Team 1
    if team1_id:
        try:
            team1 = Team.objects.get(pk=int(team1_id))
        except (ValueError, Team.DoesNotExist):
            return Response({"error": f"Invalid team1 id: {team1_id}"}, status=status.HTTP_400_BAD_REQUEST)
    elif team1_name:
        team1, _ = Team.objects.get_or_create(name=team1_name)
    else:
        return Response({"error": "Provide team1 (id) or team1_name."}, status=status.HTTP_400_BAD_REQUEST)

    # Resolve Team 2
    if team2_id:
        try:
            team2 = Team.objects.get(pk=int(team2_id))
        except (ValueError, Team.DoesNotExist):
            return Response({"error": f"Invalid team2 id: {team2_id}"}, status=status.HTTP_400_BAD_REQUEST)
    elif team2_name:
        team2, _ = Team.objects.get_or_create(name=team2_name)
    else:
        return Response({"error": "Provide team2 (id) or team2_name."}, status=status.HTTP_400_BAD_REQUEST)

    # Force ownership
    data['team1'] = team1.id
    data['team2'] = team2.id
    data['created_by'] = request.user.id

    serializer = MatchSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Match Detail
# GET, PUT, PATCH, DELETE

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def match_detail(request, pk):
    # Restrict access to matches owned by current user
    match = get_object_or_404(Match, pk=pk, created_by=request.user)

    if request.method == 'GET':
        return Response(MatchSerializer(match).data)

    if request.method == 'PUT':
        data = request.data.copy()
        data['created_by'] = request.user.id  # enforce
        serializer = MatchSerializer(match, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':
        data = request.data.copy()
        data['created_by'] = request.user.id  # enforce
        serializer = MatchSerializer(match, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    match.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
