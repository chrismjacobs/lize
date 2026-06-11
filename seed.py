"""
Run this once to initialise the database and seed starter data.
Usage:  python seed.py
"""
import json
from datetime import datetime
from app import create_app
from models import db, User, Event, Page, Attendance
from config import Config


def desc(intro, details='', expect=None, closing=''):
    """Build a structured description dict for storage as JSON."""
    return json.dumps({
        'intro':   intro,
        'details': details,
        'expect':  expect or [],
        'closing': closing,
    })


EVENTS = [
    {
        'title': 'Welcome to My Home',
        'short_description': 'Visit a local Taiwanese family and experience home life, food, and warm hospitality first-hand.',
        'description': desc(
            intro='One of the most personal activities in the Li-Ze Academy programme, Welcome to My Home connects international students with local Taiwanese families for a genuine home visit experience.',
            details='You will share a meal, explore the home, hear family stories, and discover the everyday rhythms of life in Taiwan — things no classroom can teach you.',
            expect=[
                'A warm welcome at a local family home near MCUT',
                'A home-cooked Taiwanese meal together',
                'Conversation, games, or activities organised by the family',
                'Plenty of photos and memories to take home',
            ],
        ),
        'date': datetime(2025, 4, 12, 14, 0),
        'location': 'New Taipei City (host family homes)',
        'capacity': 24,
        'registered_count': 18,
        'reflection_prompts': [
            'What did you notice about how the family organised their home?',
            'Was there a moment that surprised you?',
            'How did the experience compare to family life in your home country?',
            'What is one thing you would like to remember from today?',
        ],
    },
    {
        'title': 'NIHAO School Buddy',
        'short_description': 'Visit a local primary school and become a global friend to young Taiwanese students.',
        'description': desc(
            intro='NIHAO School Buddy takes Li-Ze Academy participants to a nearby primary school to interact with young students who are curious about the world beyond Taiwan.',
            details='You will lead simple cultural activities, share a few words in your home language, and experience the joy of cross-cultural connection at its most genuine.',
            expect=[
                'A guided visit to a local New Taipei primary school',
                'Small-group interactions with pupils aged 8–12',
                'A short activity you co-design (craft, song, or a short talk about your country)',
                'Time for questions and gifts of drawings or notes from the children',
            ],
        ),
        'date': datetime(2025, 3, 22, 9, 0),
        'location': 'Local primary school, New Taipei City',
        'capacity': 20,
        'registered_count': 20,
        'reflection_prompts': [
            "What questions did the children ask that you didn't expect?",
            'How did you feel when language was a barrier?',
            'What did their curiosity teach you about your own culture?',
        ],
    },
    {
        'title': 'Multicultural Roommate',
        'short_description': 'Spend a night living alongside students from different countries in the international dormitory.',
        'description': desc(
            intro='Multicultural Roommate is an overnight dormitory experience where participants from different nationalities are paired as temporary roommates.',
            details='Share your evening routines, your music, your snacks, and your stories. By morning you will have a better understanding of daily life across cultures.',
            expect=[
                'Check-in at the MCUT international dormitory in the evening',
                'Structured show-and-tell activity — each student brings one item that represents home',
                'Free time to cook, talk, watch a film, or play games together',
                'Debrief breakfast the next morning',
            ],
        ),
        'date': datetime(2025, 5, 3, 18, 0),
        'location': 'MCUT International Dormitory',
        'capacity': 30,
        'registered_count': 22,
        'reflection_prompts': [
            'What habit or routine of your roommate surprised you most?',
            'Was there a moment of genuine connection despite cultural differences?',
            'What would you do differently if you did this again?',
        ],
    },
    {
        'title': 'MCUT Toastmasters',
        'short_description': 'Practise public speaking in English in a supportive, international setting.',
        'description': desc(
            intro='The MCUT Toastmasters session is a welcoming English-language speaking club meeting open to all Li-Ze Academy participants.',
            details='Whether you are a confident speaker or terrified of the microphone, Toastmasters provides a structured and encouraging environment to practise.',
            expect=[
                'A prepared short speech (1–2 minutes) on any topic you choose',
                'Table Topics — impromptu 1-minute responses to surprise questions',
                'Positive, constructive feedback from fellow participants',
                'No experience required — first-timers are especially welcome',
            ],
        ),
        'date': datetime(2025, 4, 25, 18, 30),
        'location': 'Room A302, MCUT Administration Building',
        'capacity': 25,
        'registered_count': 15,
        'reflection_prompts': [
            'What was the most difficult part of speaking in front of others?',
            'What feedback did you receive that you want to act on?',
            'How does public speaking feel different in English vs your home language?',
        ],
    },
    {
        'title': 'Good Night, MCUT Buddy',
        'short_description': 'An informal evening meet-up pairing international and local students for a city night out.',
        'description': desc(
            intro='Good Night, MCUT Buddy is a relaxed, student-led evening where international students are paired with local MCUT buddies to explore New Taipei City together.',
            details='No formal itinerary — just good company, local food stalls, night markets, and conversations that flow naturally when the pressure is off.',
            expect=[
                'Meeting your MCUT local buddy at the campus main gate at 7pm',
                'A self-guided evening out — night market, bubble tea, a walk along the river',
                'A small challenge card with optional activities to try together',
                'Back to campus by 10:30pm',
            ],
        ),
        'date': datetime(2025, 3, 29, 19, 0),
        'location': 'MCUT Main Gate → New Taipei City',
        'capacity': 40,
        'registered_count': 35,
        'reflection_prompts': [
            'What surprised you most about a night out in Taiwan?',
            'Did you and your buddy find any common ground? What was it?',
            'What would you recommend to a friend visiting Taiwan for the first time?',
        ],
    },
    {
        'title': 'Get the Picture',
        'short_description': 'A visual storytelling workshop exploring cultural identity through photography.',
        'description': desc(
            intro='Get the Picture is a half-day photography and storytelling workshop. You will use your phone and a set of prompts to capture images that represent your culture, your identity, and your experience in Taiwan.',
            details='At the end of the session, the group shares and discusses the images together — often the most interesting part.',
            expect=[
                'A short introduction to visual storytelling',
                'Two hours of free photography around campus and the neighbourhood',
                'A group sharing session — each person presents 3 photos and explains their meaning',
                'A printed photo zine combining everyone\'s best shots (given out at the final event)',
            ],
        ),
        'date': datetime(2025, 4, 5, 10, 0),
        'location': 'MCUT Campus & surroundings',
        'capacity': 20,
        'registered_count': 14,
        'reflection_prompts': [
            'Which photo are you most proud of, and why did you take it?',
            'Was there a moment you wanted to photograph but chose not to? Why?',
            'What does your set of photos say about how you see Taiwan?',
        ],
    },
    {
        'title': 'Global Learners',
        'short_description': 'Join a structured cross-cultural dialogue series with students from 10+ countries.',
        'description': desc(
            intro='Global Learners is a series of facilitated conversations where students from different national backgrounds tackle real questions together — education, family, money, identity, and more.',
            details='Sessions are designed to go deeper than small talk and surface the genuine differences (and surprising similarities) in how people around the world see everyday life.',
            expect=[
                'Small mixed-nationality groups of 4–5 students',
                'A new discussion theme each session (e.g. "How did you choose your university?")',
                'A facilitator to keep things moving and respectful',
                'A short written reflection after each session',
            ],
        ),
        'date': datetime(2025, 3, 15, 14, 0),
        'location': 'International Lounge, MCUT',
        'capacity': 30,
        'registered_count': 28,
        'reflection_prompts': [
            "What assumption about another culture did today's conversation challenge?",
            'Was there a viewpoint shared today that you found genuinely difficult to understand?',
            'What question do you wish you had asked?',
        ],
    },
    {
        'title': 'Memories Making',
        'short_description': 'A craft workshop where students create a physical keepsake to remember their time in Taiwan.',
        'description': desc(
            intro='Memories Making is a hands-on craft workshop at the end of the semester. Using photos, fabric, and simple materials, each student creates a small book or memory box capturing their highlights from the Li-Ze Academy programme.',
            expect=[
                'Printed copies of your favourite photos from the programme',
                'Craft materials: fabric swatches, stamps, coloured paper, pens',
                'Guided templates to help structure your keepsake',
                'Time to share and talk about your favourite memory',
            ],
        ),
        'date': datetime(2025, 6, 7, 14, 0),
        'location': 'Art Studio, MCUT',
        'capacity': 25,
        'registered_count': 10,
        'reflection_prompts': [
            'Which Li-Ze Academy event had the biggest impact on you, and why?',
            'What is one thing you will carry back home from this programme?',
            "If you could tell next semester's participants one thing, what would it be?",
        ],
    },
    {
        'title': 'Lunch English',
        'short_description': 'A casual weekly lunch where local and international students practise English over food.',
        'description': desc(
            intro='Lunch English runs every Thursday during the semester. It is the most relaxed activity in the programme — just lunch, good conversation, and a weekly conversation card to spark discussion.',
            details='Local students get English practice. International students get local friends. Everyone gets free bubble tea.',
            expect=[
                'Meet at the MCUT cafeteria at 12:00 on Thursdays',
                'Mixed seating of local and international students',
                'One conversation prompt card per table',
                'Absolutely no pressure — come when you can',
            ],
        ),
        'date': datetime(2025, 3, 6, 12, 0),
        'location': 'MCUT Main Cafeteria',
        'capacity': 50,
        'registered_count': 32,
        'reflection_prompts': [
            'What topic came up today that you had never talked about in English before?',
            'Did you learn any new slang or expressions? What were they?',
        ],
    },
    {
        'title': 'Mandarin 101',
        'short_description': 'Learn the basics of Mandarin Chinese — tones, greetings, and survival phrases.',
        'description': desc(
            intro='Mandarin 101 is a short, practical Mandarin mini-course for international students with little or no Chinese language background.',
            details='Classes are taught by MCUT language students and focus entirely on what you actually need: greetings, ordering food, getting around, and saying polite things that Taiwanese people will genuinely appreciate.',
            expect=[
                '4 sessions of 90 minutes each, spread across the semester',
                'Tone practice, Pinyin, and characters for absolute beginners',
                'Real situations: night market, convenience store, taxi, restaurant',
                'Optional homework challenges to try your Mandarin outside the classroom',
            ],
        ),
        'date': datetime(2025, 3, 10, 17, 0),
        'location': 'Language Lab, MCUT Building B',
        'capacity': 20,
        'registered_count': 20,
        'reflection_prompts': [
            'Did you try using any Mandarin outside the classroom this week? What happened?',
            'Which tone is hardest for you, and why do you think that is?',
            'How does learning even a little of another language change how you see its speakers?',
        ],
    },
]

PAGES = [
    {
        'slug': 'home',
        'title': 'Home',
        'content_html': '''
            <p>The <strong>Li-Ze Academy</strong> (麗澤書院) is an intercultural programme run by the
            Office of International Affairs at Ming Chi University of Technology (MCUT), Taiwan.</p>
            <p>We bring together international exchange students and local MCUT students through shared
            activities — home visits, cultural nights, language exchanges, and more — to build genuine
            cross-cultural understanding and friendship.</p>
            <p>Whether you are joining us from across the world or from just down the road, Li-Ze Academy
            is your space to connect, reflect, and grow.</p>
        ''',
    },
    {
        'slug': 'about',
        'title': 'About Li-Ze Academy',
        'content_html': '''
            <h4>What is Li-Ze Academy?</h4>
            <p>Li-Ze Academy (麗澤書院) is an intercultural education programme at Ming Chi University of
            Technology (MCUT), Taiwan, run by the Office of International Affairs (OIA).</p>
            <p>The programme is designed around a simple belief: that genuine cultural understanding
            comes from shared experience, not textbooks. Students participate in themed activities
            together — visiting each other\'s homes, sharing meals, exploring the city, practising languages,
            and creating memories — and are encouraged to reflect on what they experience.</p>

            <h4>The Journal System</h4>
            <p>After each activity, enrolled students are invited to write a short reflection in their
            personal Li-Ze Academy journal. Reflections can be written, recorded as audio, or shared
            as a photo. The journal builds into a personal record of your semester in Taiwan that you
            can keep forever.</p>

            <h4>The Points System</h4>
            <p>Each journal entry earns you points. Students who complete reflections for all programme
            activities receive a Li-Ze Academy completion certificate at the end of the semester.</p>

            <h4>Contact</h4>
            <p>For questions about the programme, contact the Office of International Affairs at MCUT.</p>
        ''',
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Seed admin user
        if not User.query.filter_by(email=app.config['ADMIN_EMAIL']).first():
            admin = User(
                email=app.config['ADMIN_EMAIL'],
                name='Chris Jacobs',
                role='staff',
                nationality='International',
            )
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            print(f"Created admin: {app.config['ADMIN_EMAIL']}")

        # Seed events
        for data in EVENTS:
            if not Event.query.filter_by(title=data['title']).first():
                event = Event(
                    title=data['title'],
                    short_description=data['short_description'],
                    full_description_html=data['description'],
                    date=data['date'],
                    location=data['location'],
                    capacity=data['capacity'],
                    registered_count=data['registered_count'],
                    is_published=True,
                )
                event.reflection_prompts = data['reflection_prompts']
                event.gallery_images = []
                db.session.add(event)
                print(f"Created event: {data['title']}")

        # Seed pages
        for data in PAGES:
            if not Page.query.filter_by(slug=data['slug']).first():
                page = Page(
                    slug=data['slug'],
                    title=data['title'],
                    content_html=data['content_html'],
                )
                db.session.add(page)
                print(f"Created page: {data['slug']}")

        db.session.commit()
        print("\nDatabase seeded successfully.")


if __name__ == '__main__':
    seed()
