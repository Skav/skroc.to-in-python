from .models import Link, ActivateCode
from .serializers import LinkSerializer, UserSerializer, ActivateCodeSerializer
from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from .custom_permissions import IsOwner, IsOwnerOrReadOnly
import random, string
from datetime import datetime
from django.utils import timezone
from django.forms.models import model_to_dict
from django.core.mail import send_mail
from django.contrib.auth.hashers import hashlib

# TODO clean code
class ActivateAccount(APIView):

    def get_code(self, code):
        try:
            return ActivateCode.objects.get(activation_code=code)
        except ActivateCode.DoesNotExist:
            return False

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return False

    def check_is_code_active(self, codeObject):
        if codeObject.is_active:
            return True
        else:
            return False


    def check_is_link_expiresed(self, codeObject):
        if codeObject.expires_at >= timezone.now():
            return False
        else:
            return True


    def put(self, request):
        data = request.data
        code = self.get_code(data['code'])

        if not code:
            return Response({'Error': 'Code does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if not code.code_type == 'a':
            return Response({'Error': 'You use wrong endpoint!'}, status=status.HTTP_400_BAD_REQUEST)

        if self.check_is_code_active(code):
            if not self.check_is_link_expiresed(code):

                user = self.get_user(code.user_id)
                if not user:
                    return Response({'Error': 'User does not exist'}, status=status.HTTP_409_CONFLICT)

                user.is_active = True
                user_serializer = UserSerializer(user, data=model_to_dict(user))

                if user_serializer.is_valid():
                    code.is_active = False
                    code.updated_at = timezone.now()
                    code_serializer = ActivateCodeSerializer(code, data=model_to_dict(code))

                    if code_serializer.is_valid():
                        user_serializer.save()
                        code_serializer.save()
                        return Response({'data': 'Account sucessfully activated'},status=status.HTTP_200_OK)
                    return Response(code_serializer.errors, status=status.HTTP_409_CONFLICT)

                else:
                    return Response(user_serializer.errors, status=status.HTTP_409_CONFLICT)
            else:
                return Response({'Error': 'Links is expiresed'}, status=status.HTTP_410_GONE)
        else:
            return Response({'Error': 'This link is not longer available'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'user': reverse('user-list', request=request, format=format),
        'link': reverse('link-list', request=request, format=format),
    })


@api_view(['GET'])
def link_redirect(request, slug, format=None):
        try:
            link = Link.objects.values('original_link').get(slug=slug)
            return HttpResponseRedirect('http://'+link['original_link'])
        except Link.DoesNotExist:
            raise Response({"Error": "Link with this slug doesnt exist"}, status=status.HTTP_404_NOT_FOUND)


class LinkList(APIView):
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
        serializer = LinkSerializer(links, many=True, context={'request': request})
        return Response(serializer.data)


    def post(self, request, format=None):
        data = request.data
        data['original_link'] = data['original_link'].strip()

        if not Link.objects.filter(original_link = data['original_link']).exists():

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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer

# TODO add send email
class Register(APIView):
    permission_classes = [permissions.AllowAny]

    def generate_code(self, userObject):
        return hashlib.sha256("{}{}".format(userObject['username'], datetime.now()).encode('utf-8')).hexdigest()

    def post(self, request):
        data = request.data
        user = UserSerializer(data=data)
        if user.is_valid():
            activation_code = self.generate_code(user.validated_data)
            link = ActivateCodeSerializer(data={'activation_code': activation_code, 'code_type': 'a'})
            if link.is_valid():
                user.save()
                link.save(user_id=user.data['id'])
                return Response({
                    'Succes': 'To finish creating account verify your account by link we send to your email'},
                    status=status.HTTP_201_CREATED)
            return Response(link.errors, status=status.HTTP_409_CONFLICT)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)




