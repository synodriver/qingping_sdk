# -*- coding: utf-8 -*-


class QingpingException(Exception):
    pass


class RequestException(QingpingException):
    pass


class AuthException(QingpingException):
    pass


class NotFoundException(QingpingException):
    pass


class ConflictException(QingpingException):
    pass


class ExpiredException(QingpingException):
    pass


class ServerException(QingpingException):
    pass
