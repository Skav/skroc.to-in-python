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
from .custom_function import ActivationCodeFunctions, check_is_keys_in_request, generate_code
import random, string
from django.forms.models import model_to_dict
from rest_framework.parsers import JSONParser


class ReedemPassword(APIView):
    permission_classes = [permissions.AllowAny]

    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise

    def post(self, request):
        try:
            data = request.data

            if check_is_keys_in_request(data, ['email']):
                user = self.get_user(data['email'])
                if user.is_active == True:
                    activation_code = generate_code(user)
                    code_serializer = ActivateCodeSerializer(data={'activation_code': activation_code, 'code_type': 'r'})
                    if code_serializer.is_valid():
                        code_serializer.save(user_id=user.id)
                        return Response({'data': 'Link for reedem pasword was send to your email'}, status=status.HTTP_200_OK)
                    return Response(code_serializer.errors)
                return Response({'Error': 'User is not active'}, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as error:
            return Response({'Error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'Error': 'User with this email does not exists'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            data = request.data

            if check_is_keys_in_request(data, ['code', 'password']):
                CodeFunctions = ActivationCodeFunctions(data['code'])

            if not CodeFunctions.is_correct_endpoint(code_type='r'):
                return Response({'Error': 'You use wrong endpoint!'}, status=status.HTTP_400_BAD_REQUEST)

            if CodeFunctions.check_is_code_active():
                if not CodeFunctions.is_link_expiresed():

                    CodeFunctions.set_user_password(data['password'])
                    user = CodeFunctions.get_user_object()
                    user_serializer = UserSerializer(user, data=model_to_dict(user))

                    if user_serializer.is_valid():

                        CodeFunctions.deactive_code()
                        code = CodeFunctions.get_code_object()
                        code_serializer = ActivateCodeSerializer(code, data=model_to_dict(code))

                        if code_serializer.is_valid():
                            user_serializer.save()
                            code_serializer.save()
                            return Response({'data': 'Password change succesfully'}, status=status.HTTP_200_OK)

                        return Response(code_serializer.errors, status=status.HTTP_409_CONFLICT)
                    return Response(user_serializer.errors, status=status.HTTP_409_CONFLICT)
                return Response({'Error': 'Links is expired'}, status=status.HTTP_410_GONE)
            return Response({'Error': 'Links is no longer available'}, status=status.HTTP_410_GONE)

        except User.DoesNotExist:
            return Response({'Error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except ActivateCode.DoesNotExist:
            return Response({'Error': 'Code does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as error:
            return Response({'Error': str(error)}, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccount(APIView):
    permission_classes = [permissions.AllowAny]

    def put(self, request):
        try:
            data = request.data

            if check_is_keys_in_request(data, ['code']):
                CodeFunctions = ActivationCodeFunctions(data['code'])

            if not CodeFunctions.is_correct_endpoint('a'):
                return Response({'Error': 'You use wrong endpoint!'}, status=status.HTTP_400_BAD_REQUEST)

            if CodeFunctions.check_is_code_active():
                if not CodeFunctions.is_link_expiresed():

                    CodeFunctions.activate_user()
                    user = CodeFunctions.get_user_object()
                    user_serializer = UserSerializer(user, data=model_to_dict(user))

                    if user_serializer.is_valid():
                        CodeFunctions.deactive_code()
                        code = CodeFunctions.get_code_object()
                        code_serializer = ActivateCodeSerializer(code, data=model_to_dict(code))

                        if code_serializer.is_valid():
                            user_serializer.save()
                            code_serializer.save()
                            return Response({'data': 'Account sucessfully activated'},status=status.HTTP_200_OK)

                        return Response(code_serializer.errors, status=status.HTTP_409_CONFLICT)

                    return Response(user_serializer.errors, status=status.HTTP_409_CONFLICT)

                return Response({'Error': 'Links is expiresed'}, status=status.HTTP_410_GONE)

            return Response({'Error': 'This link is not longer available'}, status=status.HTTP_403_FORBIDDEN)

        except TypeError as e:
            return Response(e.value, status=status.HTTP_409_CONFLICT)
        except User.DoesNotExist:
            return Response({"Error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except ActivateCode.DoesNotExist:
            return Response({"Error": "Code does not exist!"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'user': reverse('user-list', request=request, format=format),
        'link': reverse('link-list', request=request, format=format),
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
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

    def post(self, request):
        data = request.data
        user = UserSerializer(data=data)
        if user.is_valid():
            activation_code = generate_code(user.validated_data)
            link = ActivateCodeSerializer(data={'activation_code': activation_code, 'code_type': 'a'})
            if link.is_valid():
                user.save()
                link.save(user_id=user.data['id'])
                return Response({
                    'Succes': 'To finish creating account verify your account by link we send to your email'},
                    status=status.HTTP_201_CREATED)
            return Response(link.errors, status=status.HTTP_409_CONFLICT)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)




