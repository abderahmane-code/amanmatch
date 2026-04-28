from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from accounts.models import AccountProfile
from matchmaking.models import Interest, Match
from profiles.models import MatchmakingProfile


def _calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def _are_matched(user_a, user_b):
    return Match.objects.filter(
        Q(user1=user_a, user2=user_b) | Q(user1=user_b, user2=user_a),
        is_active=True,
    ).exists()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


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

    results = []
    for u in users:
        acct = u.account_profile
        mp = u.matchmaking_profile
        age = _calculate_age(acct.date_of_birth) if acct.date_of_birth else None
        results.append({"user": u, "account": acct, "profile": mp, "age": age})

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


# ---------------------------------------------------------------------------
# Public profile detail
# ---------------------------------------------------------------------------


@login_required
def public_profile_view(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    acct = get_object_or_404(AccountProfile, user=target_user)
    mp = get_object_or_404(MatchmakingProfile, user=target_user)

    age = _calculate_age(acct.date_of_birth) if acct.date_of_birth else None

    viewer_acct = getattr(request.user, "account_profile", None)
    viewer_verified = viewer_acct.is_identity_verified if viewer_acct else False
    is_own = request.user == target_user
    is_matched = _are_matched(request.user, target_user)

    # Interest state between viewer and target
    sent_interest = Interest.objects.filter(
        sender=request.user, receiver=target_user
    ).exclude(status="rejected").first()

    received_interest = Interest.objects.filter(
        sender=target_user, receiver=request.user
    ).exclude(status="rejected").first()

    interest_state = "none"
    interest_obj = None
    if is_matched or (sent_interest and sent_interest.status == "accepted"):
        interest_state = "matched"
    elif sent_interest and sent_interest.status == "pending":
        interest_state = "sent_pending"
    elif received_interest and received_interest.status == "pending":
        interest_state = "received_pending"
        interest_obj = received_interest

    return render(
        request,
        "matchmaking/profile_detail.html",
        {
            "target_user": target_user,
            "account": acct,
            "profile": mp,
            "age": age,
            "viewer_verified": viewer_verified,
            "is_own_profile": is_own,
            "is_matched": is_matched,
            "interest_state": interest_state,
            "interest_obj": interest_obj,
        },
    )


# ---------------------------------------------------------------------------
# Interest actions (POST-only)
# ---------------------------------------------------------------------------


@login_required
@require_POST
def send_interest_view(request, user_id):
    receiver = get_object_or_404(User, pk=user_id)

    viewer_acct = getattr(request.user, "account_profile", None)
    if not viewer_acct or not viewer_acct.is_identity_verified:
        messages.error(request, _("You must verify your identity before sending interest."))
        return redirect("matchmaking:public_profile", user_id=user_id)

    if request.user == receiver:
        messages.error(request, _("You cannot send interest to yourself."))
        return redirect("matchmaking:public_profile", user_id=user_id)

    existing = Interest.objects.filter(
        sender=request.user,
        receiver=receiver,
        status__in=["pending", "accepted"],
    ).exists()
    if existing:
        messages.warning(request, _("You have already sent interest to this user."))
        return redirect("matchmaking:public_profile", user_id=user_id)

    Interest.objects.create(sender=request.user, receiver=receiver)
    messages.success(request, _("Interest sent successfully."))
    return redirect("matchmaking:public_profile", user_id=user_id)


@login_required
@require_POST
def accept_interest_view(request, interest_id):
    interest = get_object_or_404(Interest, pk=interest_id)

    if interest.receiver != request.user:
        return HttpResponseForbidden(_("You cannot accept this interest."))

    interest.status = "accepted"
    interest.save()

    # Create match if not already exists
    already_matched = Match.objects.filter(
        Q(user1=interest.sender, user2=interest.receiver)
        | Q(user1=interest.receiver, user2=interest.sender)
    ).exists()
    if not already_matched:
        Match.objects.create(user1=interest.sender, user2=interest.receiver)

    messages.success(request, _("Interest accepted. You are now matched!"))
    return redirect("matchmaking:public_profile", user_id=interest.sender.pk)


@login_required
@require_POST
def reject_interest_view(request, interest_id):
    interest = get_object_or_404(Interest, pk=interest_id)

    if interest.receiver != request.user:
        return HttpResponseForbidden(_("You cannot reject this interest."))

    interest.status = "rejected"
    interest.save()

    messages.success(request, _("Interest rejected."))
    return redirect("matchmaking:received_interests")


# ---------------------------------------------------------------------------
# Interest / Match list pages
# ---------------------------------------------------------------------------


def _build_user_card(user_obj):
    acct = getattr(user_obj, "account_profile", None)
    age = _calculate_age(acct.date_of_birth) if acct and acct.date_of_birth else None
    return {"user": user_obj, "account": acct, "age": age}


@login_required
def received_interests_view(request):
    interests = (
        Interest.objects.filter(receiver=request.user)
        .select_related("sender__account_profile")
        .order_by("-created_at")
    )
    items = []
    for i in interests:
        card = _build_user_card(i.sender)
        card["interest"] = i
        items.append(card)
    return render(request, "matchmaking/received_interests.html", {"items": items})


@login_required
def sent_interests_view(request):
    interests = (
        Interest.objects.filter(sender=request.user)
        .select_related("receiver__account_profile")
        .order_by("-created_at")
    )
    items = []
    for i in interests:
        card = _build_user_card(i.receiver)
        card["interest"] = i
        items.append(card)
    return render(request, "matchmaking/sent_interests.html", {"items": items})


@login_required
def matches_view(request):
    match_qs = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user),
        is_active=True,
    ).select_related(
        "user1__account_profile",
        "user2__account_profile",
    ).order_by("-created_at")

    items = []
    for m in match_qs:
        other = m.user2 if m.user1 == request.user else m.user1
        card = _build_user_card(other)
        card["match"] = m
        items.append(card)
    return render(request, "matchmaking/matches.html", {"items": items})
