from .models import Link
from .serializers import LinkSerializer, UserSerializer
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
import random, string


class LinkList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def generateRandomString(self, lenght=5):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(lenght))

    def isSlugAvailable(self, slug):
        try:
            Link.objects.get(slug=slug)
            return False
        except Link.DoesNotExist:
            return True

    def generateLink(self, slug):
        baseUrl = 'http://skroc.to/'
        return baseUrl+slug

    def get(self, request, format=None):
        links = Link.objects.all()
        serializer = LinkSerializer(links, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        print(data)
        if not Link.objects.filter(original_link=data['original_link']):

            i = 0
            while True:
                slug = self.generateRandomString(5)
                if self.isSlugAvailable(slug):
                    url = self.generateLink(slug)
                    break;
                elif i == 20:
                    return Response({"Error": "Cannot find free slug, please try later"},
                                    status=status.HTTP_508_LOOP_DETECTED)
                i+=1

            serializer = LinkSerializer(data={'original_link': data['original_link'], 'shorted_link': url, 'slug': slug})
            if serializer.is_valid():
                serializer.save(user_id=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"Error": "Link already exist"}, status=status.HTTP_409_CONFLICT)


class LinkDetail(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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


#TODO
class LinkRedirect(APIView):
    def get(self, request, slug):
        try:
            link = Link.objects.get(slug=slug)
            print(link.original_link)
            url = link.original_link
            return redirect(url)
        except Link.DoesNotExist:
            raise Response({"Error": "Link with this slug doesnt exist"}, status=status.HTTP_404_NOT_FOUND)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
