from django.utils import timezone
from .models import ActivateCode, User
from .serializers import UserSerializer, ActivateCodeSerializer
from django.contrib.auth.hashers import hashlib
from datetime import datetime


def check_is_keys_in_request(request_dict: dict, requirement: list):

    lost_keys = ''

    for key in requirement:
        if not key in request_dict:
            lost_keys += "{}, ".format(key)

    if lost_keys != '':
        raise ValueError('This keys is require: {}'.format(lost_keys))

    return True

def generate_code(userObject):
    return hashlib.sha256("{}{}".format(userObject.username, datetime.now()).encode('utf-8')).hexdigest()

class ActivationCodeFunctions():

    def __init__(self, code):
        self.__code = self.__get_code(code)
        self.__user = self.__get_user(self.__code.user_id)

    def is_correct_endpoint(self, code_type):
        if self.__code.code_type == code_type:
            return True
        else:
            return False

    def __get_code(self, code):
        try:
            return ActivateCode.objects.get(activation_code=code)
        except ActivateCode.DoesNotExist:
            raise

    def __get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise

    def get_user_object(self):
        return self.__user

    def get_code_object(self):
        return self.__code

    def check_is_code_active(self):
        try:
            if self.__code.is_active:
                return True
            else:
                return False
        except self.__code is None:
            raise TypeError

    def is_link_expiresed(self):
        try:
            if self.__code.expires_at >= timezone.now():
                return False
            else:
                return True
        except self.__code is None:
            raise TypeError

    def deactive_code(self):
        self.__code.is_active = False
        self.__code.updated_at = timezone.now()

    def set_user_password(self, password):
        self.__user.set_password(raw_password=password)

    def activate_user(self):
        self.__user.is_active = True