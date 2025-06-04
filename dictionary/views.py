from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from .models import Word, SearchHistory, Note
from django.contrib.auth.decorators import login_required
import requests

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('search')  # Redirect to search page after signup
    else:
        form = UserCreationForm()
    return render(request, 'dictionary/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('search')  # Redirect to search page after login
    else:
        form = AuthenticationForm()
    return render(request, 'dictionary/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('search')  # Redirect to search page after logout

def search(request):
    import logging
    query = request.GET.get('q', '').strip()  # Get the searched word
    language = request.GET.get('language', 'en').strip()  # Get the selected language, default to 'en'
    word_data = None  # Default to None if no word is searched
    synonyms = []
    antonyms = []
    recent_searches = []
    error_message = None
    linguistic_features = []

    from .models import Word, LinguisticFeature

    if query:
        import logging
        # Try to get word from local DB with language
        try:
            word_obj = Word.objects.get(word__iexact=query, language=language)
            logging.info(f"Found local word data for '{query}' in language '{language}'")
            # Prepare word_data in the same structure as API response for template compatibility
            word_data = [{
                'word': word_obj.word,
                'meanings': [{
                    'partOfSpeech': word_obj.part_of_speech,
                    'definitions': [{
                        'definition': word_obj.meaning,
                        'example': None
                    }]
                }]
            }]
            synonyms = word_obj.synonyms.split(',') if word_obj.synonyms else []
            antonyms = word_obj.antonyms.split(',') if word_obj.antonyms else []

            # Get linguistic features for this word and language
            linguistic_features = LinguisticFeature.objects.filter(word=word_obj, language=language)

        except Word.DoesNotExist:
            logging.info(f"No local word data found for '{query}' in language '{language}'")
            # If not found locally, fallback to external API
            try:
                from django.conf import settings
                headers = {}
                if language == 'en':
                    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{query}"
                    response = requests.get(url)
                    response.raise_for_status()
                    word_data = response.json()
                    synonyms = []
                    antonyms = []
                    if 'meanings' in word_data[0]:
                        for meaning in word_data[0]['meanings']:
                            if 'synonyms' in meaning:
                                synonyms.extend(meaning['synonyms'])
                            if 'antonyms' in meaning:
                                antonyms.extend(meaning['antonyms'])
                else:
                    # Fallback to Wiktionary API
                    url = f"https://{language}.wiktionary.org/w/api.php?action=query&format=json&titles={query}&prop=extracts&exintro=1"
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()
                    pages = data.get('query', {}).get('pages', {})
                    extract = ''
                    for page_id, page_data in pages.items():
                        extract = page_data.get('extract', '')
                        break
                    word_data = [{
                        'word': query,
                        'meanings': [{
                            'partOfSpeech': 'N/A',
                            'definitions': [{
                                'definition': extract,
                                'example': None
                            }]
                        }]
                    }]
                    synonyms = []
                    antonyms = []
            except Exception as e:
                logging.error(f"Error fetching data from API: {e}")
                word_data = None
                error_message = "Sorry, could not fetch data for the selected language at this time."

        # Save search history if user is logged in
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, word=query, language=language)

    # Fetch recent searches if user is authenticated
    if request.user.is_authenticated:
        recent_searches = SearchHistory.objects.filter(user=request.user).order_by('-search_time')[:5]

    return render(request, 'dictionary/search_results.html', {
        'word_data': word_data, 'query': query, 'language': language, 'synonyms': synonyms, 'antonyms': antonyms,
        'recent_searches': recent_searches, 'error_message': error_message, 'linguistic_features': linguistic_features
    })


@login_required
def add_note(request, word_id):
    word = get_object_or_404(Word, id=word_id)

    if request.method == 'POST':
        note_text = request.POST.get('note', '').strip()
        if note_text:
            Note.objects.create(user=request.user, word=word, text=note_text)

    return redirect('search')  # Redirect back to search page after adding note


from django.http import JsonResponse
from django.db.models import Q

def user_profile(request):
    if request.user.is_authenticated:
        recent_searches = SearchHistory.objects.filter(user=request.user).order_by('-search_time')[:5]
        return render(request, 'user/profile.html', {'recent_searches': recent_searches})

def autocomplete(request):
    query = request.GET.get('q', '').strip()
    suggestions = []
    import logging
    logging.debug(f"Autocomplete query received: {query}")  # Debug log
    if query:
        words = Word.objects.filter(word__istartswith=query).order_by('word')[:10]
        suggestions = [word.word for word in words]
    logging.debug(f"Autocomplete suggestions: {suggestions}")  # Debug log
    response = JsonResponse(suggestions, safe=False)
    response["Access-Control-Allow-Origin"] = "*"  # Allow CORS for testing
    return response
