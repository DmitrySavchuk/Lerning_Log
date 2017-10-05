from django.shortcuts import render

from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from .forms import TopicForm, EntryForm
from .models import Topic, Entry


def index(request):
    # Home page
    return render(request, 'DJ/index.html')


@login_required
def topics(request):
    # Topics list
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'DJ/topics.html', context)


@login_required
def topic(request, topic_id):
    # It shows one topic and all its entries
    topic = Topic.objects.get(id=topic_id)

    owner_check(request, topic)

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'DJ/topic.html', context)


@login_required
def new_topic(request):
    # Define new topic
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic_ = form.save(commit=False)
            new_topic_.owner = request.user
            new_topic_.save()
            return HttpResponseRedirect(reverse('DJ:topics'))  # ДОБАВИТЬ ДЕЙСТВИЯ, ЕСЛИ ФОРМА НЕВАЛИДНА

    context = {'form': form}
    return render(request, 'DJ/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    # Add new entry
    topic = Topic.objects.get(id=topic_id)

    owner_check(request, topic)

    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse('DJ:topic', args=[topic_id]))

    context = {'topic': topic, 'form': form}
    return render(request, 'DJ/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    owner_check(request, topic)

    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('DJ:topic', args=[topic.id]))

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'DJ/edit_entry.html', context)


def owner_check(request, topic):
    if topic.owner != request.user:
        raise Http404