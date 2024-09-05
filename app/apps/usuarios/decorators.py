from django.contrib.auth.decorators import user_passes_test


def business_account_required(function=None, login_url='error_403'):
    actual_decorator = user_passes_test(
        lambda u: u.flag_estabelecimento,
        login_url=login_url
     )
    if function:
        return actual_decorator(function)
    return actual_decorator


def master_user_required(function=None, login_url='error_403'):
    actual_decorator = user_passes_test(
        lambda u: u.user_type == 1,
        login_url=login_url
     )
    if function:
        return actual_decorator(function)
    return actual_decorator


def buyer_user_required(function=None, login_url='error_403'):
    actual_decorator = user_passes_test(
        #lambda u: u.user_type == 1 or u.user_type == 2 or u.user_type == 3,
        lambda u: u.user_type in [1, 2, 3],
        login_url=login_url
     )
    if function:
        return actual_decorator(function)
    return actual_decorator


def buyer_or_worker_required(function=None, login_url='error_403'):
    actual_decorator = user_passes_test(
        #lambda u: u.user_type == 1 or u.user_type == 2 or u.user_type == 3,
        lambda u: u.user_type in [1, 2, 3, 4],
        login_url=login_url
     )
    if function:
        return actual_decorator(function)
    return actual_decorator


def fabrica_user_required(function=None, login_url='error_403'):
    actual_decorator = user_passes_test(
        #lambda u: u.user_type == 1 or u.user_type == 2 or u.user_type == 3,
        lambda u: u.user_type in [1, 5],
        login_url=login_url
     )
    if function:
        return actual_decorator(function)
    return actual_decorator