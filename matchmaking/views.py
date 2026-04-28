from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render

from accounts.models import AccountProfile
from profiles.models import MatchmakingProfile


def _calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


@login_required
def search_view(request):
    users = (
        User.objects.filter(
            account_profile__isnull=False,
            matchmaking_profile__isnull=False,
        )
        .exclude(pk=request.user.pk)
        .select_related("account_profile", "matchmaking_profile")
    )

    # Apply filters
    gender = request.GET.get("gender", "")
    country = request.GET.get("country", "")
    city = request.GET.get("city", "")
    age_min = request.GET.get("age_min", "")
    age_max = request.GET.get("age_max", "")
    marital_status = request.GET.get("marital_status", "")
    education_level = request.GET.get("education_level", "")
    serious_intention = request.GET.get("serious_intention", "")

    if gender:
        users = users.filter(account_profile__gender=gender)
    if country:
        users = users.filter(account_profile__country__icontains=country)
    if city:
        users = users.filter(account_profile__city__icontains=city)
    if marital_status:
        users = users.filter(matchmaking_profile__marital_status=marital_status)
    if education_level:
        users = users.filter(
            matchmaking_profile__education_level__icontains=education_level
        )
    if serious_intention:
        users = users.filter(
            matchmaking_profile__serious_intention=serious_intention
        )

    # Age filtering (based on date_of_birth)
    today = date.today()
    if age_min:
        try:
            min_age = int(age_min)
            max_dob = date(today.year - min_age, today.month, today.day)
            users = users.filter(account_profile__date_of_birth__lte=max_dob)
        except (ValueError, OverflowError):
            pass
    if age_max:
        try:
            max_age = int(age_max)
            min_dob = date(today.year - max_age - 1, today.month, today.day)
            users = users.filter(account_profile__date_of_birth__gte=min_dob)
        except (ValueError, OverflowError):
            pass

    # Build result cards
    results = []
    for u in users:
        acct = u.account_profile
        mp = u.matchmaking_profile
        age = _calculate_age(acct.date_of_birth) if acct.date_of_birth else None
        results.append(
            {
                "user": u,
                "account": acct,
                "profile": mp,
                "age": age,
            }
        )

    return render(
        request,
        "matchmaking/search.html",
        {
            "results": results,
            "result_count": len(results),
            "filters": {
                "gender": gender,
                "country": country,
                "city": city,
                "age_min": age_min,
                "age_max": age_max,
                "marital_status": marital_status,
                "education_level": education_level,
                "serious_intention": serious_intention,
            },
            "gender_choices": AccountProfile.GENDER_CHOICES,
            "marital_choices": MatchmakingProfile.MARITAL_STATUS_CHOICES,
            "intention_choices": MatchmakingProfile.INTENTION_CHOICES,
        },
    )


@login_required
def public_profile_view(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    acct = get_object_or_404(AccountProfile, user=target_user)
    mp = get_object_or_404(MatchmakingProfile, user=target_user)

    age = _calculate_age(acct.date_of_birth) if acct.date_of_birth else None

    viewer_verified = getattr(
        getattr(request.user, "account_profile", None),
        "is_identity_verified",
        False,
    )

    return render(
        request,
        "matchmaking/profile_detail.html",
        {
            "target_user": target_user,
            "account": acct,
            "profile": mp,
            "age": age,
            "viewer_verified": viewer_verified,
            "is_own_profile": request.user == target_user,
        },
    )
