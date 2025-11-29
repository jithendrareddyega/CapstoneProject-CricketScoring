from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Match, Team, Player, BallByBall


# Auth Views

def register(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password']
        if not username:
            messages.error(request, 'Username is required.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    return render(request, 'scoring/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'scoring/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')



# App Views

@login_required
def home(request):
    matches = Match.objects.filter(created_by=request.user)
    return render(request, 'scoring/home.html', {'matches': matches})


@login_required
def create_match(request):
    if request.method == 'POST':
        team1_name = request.POST['team1'].strip()
        team2_name = request.POST['team2'].strip()
        overs = int(request.POST['overs'])

        team1 = Team.objects.create(name=team1_name)
        team2 = Team.objects.create(name=team2_name)

        match = Match.objects.create(
            team1=team1,
            team2=team2,
            overs=overs,
            created_by=request.user
        )
        return redirect('add_players', match.id)

    return render(request, 'scoring/create_match.html')


@login_required
def add_players(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    team1_players = Player.objects.filter(team=match.team1)
    team2_players = Player.objects.filter(team=match.team2)

    if request.method == 'POST':
        team_choice = request.POST['team']
        player_name = request.POST['player_name'].strip()
        if player_name:
            team_obj = match.team1 if team_choice == 'team1' else match.team2
            Player.objects.create(team=team_obj, name=player_name)
        return redirect('add_players', match_id=match.id)

    return render(
        request,
        'scoring/add_players.html',
        {
            'match': match,
            'team1_players': team1_players,
            'team2_players': team2_players,
        },
    )


@login_required
def match_dashboard(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    balls = BallByBall.objects.filter(match=match).order_by('over', 'ball')

    # ----- Handle new ball submission -----
    if request.method == 'POST':
        batsman_id = request.POST['batsman']
        bowler_id = request.POST['bowler']
        runs = int(request.POST['runs'])
        is_wicket = 'is_wicket' in request.POST

        # Determine next over/ball
        last_ball = BallByBall.objects.filter(match=match).order_by('-over', '-ball').first()
        if last_ball:
            over = last_ball.over
            ball = last_ball.ball + 1
            if ball > 6:  # new over
                over += 1
                ball = 1
        else:
            over, ball = 1, 1

        BallByBall.objects.create(
            match=match,
            over=over,
            ball=ball,
            batsman_id=batsman_id,
            bowler_id=bowler_id,
            runs=runs,
            is_wicket=is_wicket,
        )
        return redirect('match_dashboard', match_id=match.id)

    # ----- Player lists (simple assumption: team1 batting vs team2 bowling) -----
    team1_players = Player.objects.filter(team=match.team1)
    team2_players = Player.objects.filter(team=match.team2)

    # ----- Totals -----
    total_runs = sum(b.runs for b in balls)
    wickets = sum(1 for b in balls if b.is_wicket)

    # ----- Stats Aggregation -----
    batsman_stats = {}  # {name: {runs, fours, sixes}}
    bowler_stats = {}   # {name: {balls, runs, wickets}}

    for b in balls:
        # Batsman
        bs = batsman_stats.setdefault(b.batsman.name, {'runs': 0, 'fours': 0, 'sixes': 0})
        bs['runs'] += b.runs
        if b.runs == 4:
            bs['fours'] += 1
        if b.runs == 6:
            bs['sixes'] += 1

        # Bowler
        bw = bowler_stats.setdefault(b.bowler.name, {'balls': 0, 'runs': 0, 'wickets': 0})
        bw['balls'] += 1
        bw['runs'] += b.runs
        if b.is_wicket:
            bw['wickets'] += 1

    # Build bowler rows list to make template simple
    bowler_rows = []
    for name, stats in bowler_stats.items():
        overs = f"{stats['balls'] // 6}.{stats['balls'] % 6}"
        bowler_rows.append({
            'name': name,
            'overs': overs,
            'runs': stats['runs'],
            'wickets': stats['wickets'],
        })

    context = {
        'match': match,
        'balls': balls,
        'team1_players': team1_players,
        'team2_players': team2_players,
        'total_runs': total_runs,
        'wickets': wickets,
        'batsman_stats': batsman_stats,
        'bowler_rows': bowler_rows,
    }
    return render(request, 'scoring/match_dashboard.html', context)
