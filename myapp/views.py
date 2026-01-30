# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
import socket
from django.db.models import Avg
from .models import Application, Review, Category, Feedback

# ==================== NLTK Sentiment Functions  ====================
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet, sentiwordnet as swn
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('sentiwordnet')
# nltk.download('averaged_perceptron_tagger')

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def analyze_sentiment(text):
    if not text.strip():
        print("Review is empty → Neutral, 0.0")
        return "Neutral", 0.0

    tokens = word_tokenize(text.lower())
    lemmatizer = WordNetLemmatizer()
    pos_total = 0
    neg_total = 0
    valid_words = 0

    print("\n=== Sentiment Analysis Details ===")
    print(f"Review Text: {text}\n")

    for token in tokens:
        if len(token) < 3:
            continue
        tag = pos_tag([token])[0][1]
        wn_tag = get_wordnet_pos(tag)
        lemma = lemmatizer.lemmatize(token, wn_tag)

        synsets = list(swn.senti_synsets(lemma, wn_tag))
        if not synsets:
            continue

        senti = synsets[0]
        pos_score = senti.pos_score()
        neg_score = senti.neg_score()
        pos_total += pos_score
        neg_total += neg_score
        valid_words += 1

        print(f"Word: '{token}' | Lemma: '{lemma}' | POS Score: {pos_score} | NEG Score: {neg_score}")

    if valid_words == 0:
        print("No valid words found → Neutral, 0.0")
        return "Neutral", 0.0

    score = (pos_total - neg_total) / valid_words

    if score >= 0.2:
        label = "Positive"
    elif score <= -0.2:
        label = "Negative"
    else:
        label = "Neutral"

    print("\nTotal Positive Score:", round(pos_total, 3))
    print("Total Negative Score:", round(neg_total, 3))
    print("Valid Words Count:", valid_words)
    print("Average Sentiment Score:", round(score, 3))
    print("Final Label:", label)
    print("===============================\n")

    return label, round(score, 3)


# ==================== Views ====================

def register_view(request):
    if request.method == 'POST':
        from .forms import CustomUserCreationForm
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please log in.")
            return redirect('login')
    else:
        from .forms import CustomUserCreationForm
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')



# views.py
from django.db.models import Q, Avg

@login_required
def dashboard(request):
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')

    # Base queryset with sentiment score
    apps = Application.objects.annotate(
        avg_score=Avg('reviews__sentiment_score')
    )

    # Search by name or category
    if query:
        apps = apps.filter(
            Q(name__icontains=query) | 
            Q(category__name__icontains=query)
        )

    if category_filter:
        apps = apps.filter(category__id=category_filter)

    # Rank by sentiment score (highest = most positive)
    apps = apps.order_by('-avg_score')

    # Recent apps for carousel
    recent_apps = Application.objects.order_by('-added_on')[:8]

    # Categories for filter dropdown
    categories = Category.objects.all()

    context = {
        'apps': apps,
        'recent_apps': recent_apps,
        'categories': categories,
        'query': query,
        'selected_category': category_filter,
    }
    return render(request, 'dashboard.html', context)

@login_required
def app_detail(request, app_id):
    app = get_object_or_404(Application, id=app_id)
    reviews = Review.objects.filter(application=app).order_by('-created_at')

    total = reviews.count()
    positive = reviews.filter(sentiment_score__gte=0.2).count()
    negative = reviews.filter(sentiment_score__lte=-0.2).count()
    neutral = total - positive - negative

    context = {
        'app': app,
        'reviews': reviews,
        'total_reviews': total,
        'positive': positive,
        'negative': negative,
        'neutral': neutral,
    }
    return render(request, 'app_detail.html', context)


 

@login_required
def post_review(request, app_id):
    app = get_object_or_404(Application, id=app_id)

    if request.method == 'POST':
        text = request.POST.get('review_text', '').strip()
        rating_str = request.POST.get('rating', '').strip()

        if not text:
            messages.error(request, "Review text cannot be empty.")
            return redirect('app_detail', app_id=app_id)

        # ----------------------------
        # Rating Validation
        # ----------------------------
        rating = None
        if rating_str.isdigit():
            rating = int(rating_str)
            if rating < 1 or rating > 5:
                rating = None

        # ----------------------------
        # IP Address Capture (Socket)
        # ----------------------------
        try:
            ip_address = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip_address = None

        # ----------------------------
        # Sentiment Analysis
        # ----------------------------
        sentiment_label, sentiment_score = analyze_sentiment(text)

        # ----------------------------
        # Count existing reviews by user for same app
        # ----------------------------
        review_count = Review.objects.filter(
            user=request.user,
            application=app
        ).count()

        # ----------------------------
        # Fake Review Logic
        # ----------------------------
        is_fake = review_count >= 3
        admin_note = (
            "Auto-flagged: User posted more than 3 reviews on same application."
            if is_fake else None
        )

        # ----------------------------
        # Create Review (DO NOT update)
        # ----------------------------
        Review.objects.create(
            user=request.user,
            application=app,
            text=text,
            rating=rating,
            ip_address=ip_address,
            sentiment=sentiment_label,
            sentiment_score=sentiment_score,
            is_fake=is_fake,
            admin_note=admin_note
        )

        if is_fake:
            messages.warning(
                request,
                "Your review was posted but flagged for moderation due to multiple submissions."
            )
        else:
            messages.success(request, "Your review has been posted successfully!")

        return redirect('app_detail', app_id=app_id)

    return redirect('app_detail', app_id=app_id)


@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_reviews.html', {'reviews': reviews})


@login_required
def give_feedback(request):
    if request.method == 'POST':
        msg = request.POST.get('message', '').strip()
        if msg:
            Feedback.objects.create(user=request.user, message=msg)
            messages.success(request, "Thank you for your feedback!")
        else:
            messages.error(request, "Feedback cannot be empty.")
    return redirect('dashboard')



# ==================== USER FEEDBACK SYSTEM ====================

@login_required
def submit_feedback(request):
    """User submits feedback about the system"""
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            Feedback.objects.create(
                user=request.user,
                message=message
            )
            messages.success(request, "Thank you! Your feedback has been sent.")
        else:
            messages.error(request, "Please write a message.")
        return redirect('submit_feedback')

    # Count unread feedback for admin (optional badge)
    unread_count = Feedback.objects.filter(is_read=False).count() if request.user.is_staff else 0

    return render(request, 'feedback.html', {
        'unread_count': unread_count
    })


