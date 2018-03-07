from account.models import EmailAddress


def userinfo(claims, user):
    email_address = EmailAddress.objects.get_primary(user)
    if email_address is None:
        claims["email"] = user.email
    else:
        claims["email"] = email_address.email
        claims["email_verified"] = email_address.verified
    claims["preferred_username"] = user.username
    claims["zoneinfo"] = user.account.timezone
    claims["locale"] = user.account.language
    return claims
