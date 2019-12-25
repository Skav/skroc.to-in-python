from .models import Link
from .serializers import LinkSerializer, UserSerializer
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth.models import User
from django.http import Http404


class LinkList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        links = Link.objects.all()
        serializer = LinkSerializer(links, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if not Link.objects.filter(slug=data['slug']):
            serializer = LinkSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user_id=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"Error": "Link already exist"}, status=status.HTTP_409_CONFLICT)


class LinkDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def getLink(self, slug):
        try:
            return Link.objects.get(slug=slug)
        except Link.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        link = self.getLink(slug)
        serializer = LinkSerializer(link)
        return Response(serializer.data)

    def put(self, request, slug, format=None):
        link = self.getLink(slug)
        serializer = LinkSerializer(link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, format=None):
        link = self.getLink(slug)
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
