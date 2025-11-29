from django.shortcuts import render


def index(request):
    # Render `index.html` from the templates directory
    return render(request, 'index.html')


def about(request):
    # Render the About page template (file is named 'about page.html')
    # It's better to reference it via a URL route than by a space-containing filename in hrefs.
    return render(request, 'about page.html')

def committee(request):
    # Render the Committee page template (file is named 'committee.html')
    return render(request, 'comittee.html')


def notices(request):
    # Render the Notices page copied from index section
    return render(request, 'notices.html')


def events(request):
    # Render the Events page copied from index section
    return render(request, 'events.html')


def services_page(request):
    # Render the Services page (existing template)
    return render(request, 'services.html')


def contact(request):
    # Render a standalone contact page
    return render(request, 'contact.html')