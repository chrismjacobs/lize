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
    return json.dumps({'intro': intro, 'details': details, 'expect': expect or [], 'closing': closing})


def desc_zh(intro, details='', expect=None, closing=''):
    return json.dumps({'intro': intro, 'details': details, 'expect': expect or [], 'closing': closing}, ensure_ascii=False)


EVENTS = [
    {
        'title': 'Welcome to My Home',
        'short_description': 'Visit a local Taiwanese family and experience home life, food, and warm hospitality first-hand.',
        'description': desc(
            intro='One of the most personal activities in the Li-Ze Academy programme, Welcome to My Home connects international students with local Taiwanese families for a genuine home visit experience.',
            details='You will share a meal, explore the home, hear family stories, and discover the everyday rhythms of life in Taiwan — things no classroom can teach you.',
            expect=['A warm welcome at a local family home near MCUT', 'A home-cooked Taiwanese meal together', 'Conversation, games, or activities organised by the family', 'Plenty of photos and memories to take home'],
        ),
        'title_zh': '歡迎來我家',
        'short_description_zh': '拜訪台灣本地家庭，親身體驗家庭生活、美食與溫馨款待。',
        'description_zh': desc_zh(
            intro='「歡迎來我家」是麗澤書院最溫馨的活動之一，讓國際學生有機會走入台灣本地家庭，進行真實的居家體驗。',
            details='你將與家人共享餐點、參觀家中、聆聽家庭故事，深入了解台灣的日常生活節奏——這是課堂上學不到的。',
            expect=['在新北市本地家庭受到熱情歡迎', '一起享用家常台灣料理', '家人安排的交流活動、遊戲或互動', '帶走滿滿的照片與美好回憶'],
        ),
        'date': datetime(2025, 4, 12, 14, 0),
        'location': 'New Taipei City (host family homes)',
        'capacity': 24,
        'registered_count': 18,
        'reflection_prompts': ['What did you notice about how the family organised their home?', 'Was there a moment that surprised you?', 'How did the experience compare to family life in your home country?', 'What is one thing you would like to remember from today?'],
        'reflection_prompts_zh': ['你對這個家庭的居家空間有什麼觀察？', '有沒有哪個瞬間讓你感到驚訝？', '這次體驗與你家鄉的家庭生活有什麼不同？', '你最想留住的是哪件事？'],
    },
    {
        'title': 'NIHAO School Buddy',
        'short_description': 'Visit a local primary school and become a global friend to young Taiwanese students.',
        'description': desc(
            intro='NIHAO School Buddy takes Li-Ze Academy participants to a nearby primary school to interact with young students who are curious about the world beyond Taiwan.',
            details='You will lead simple cultural activities, share a few words in your home language, and experience the joy of cross-cultural connection at its most genuine.',
            expect=['A guided visit to a local New Taipei primary school', 'Small-group interactions with pupils aged 8–12', 'A short activity you co-design (craft, song, or a short talk about your country)', 'Time for questions and gifts of drawings or notes from the children'],
        ),
        'title_zh': '你好！小學夥伴',
        'short_description_zh': '走訪本地小學，成為年輕台灣學生的國際好朋友。',
        'description_zh': desc_zh(
            intro='「你好！小學夥伴」帶領麗澤書院學員前往附近小學，與對外面世界充滿好奇的小朋友互動。',
            details='你將帶領簡單的文化活動、分享幾句母語，體驗最純真的跨文化連結喜悅。',
            expect=['前往新北市本地小學參訪', '與8至12歲小朋友進行小組互動', '共同設計短暫活動（手工藝、歌曲或介紹自己的國家）', '孩子們以畫作或手寫卡片相贈的溫馨時光'],
        ),
        'date': datetime(2025, 3, 22, 9, 0),
        'location': 'Local primary school, New Taipei City',
        'capacity': 20,
        'registered_count': 20,
        'reflection_prompts': ["What questions did the children ask that you didn't expect?", 'How did you feel when language was a barrier?', 'What did their curiosity teach you about your own culture?'],
        'reflection_prompts_zh': ['孩子們問了哪些你沒想到的問題？', '語言不通時，你有什麼感受？', '他們的好奇心讓你對自己的文化有什麼新的認識？'],
    },
    {
        'title': 'Multicultural Roommate',
        'short_description': 'Spend a night living alongside students from different countries in the international dormitory.',
        'description': desc(
            intro='Multicultural Roommate is an overnight dormitory experience where participants from different nationalities are paired as temporary roommates.',
            details='Share your evening routines, your music, your snacks, and your stories. By morning you will have a better understanding of daily life across cultures.',
            expect=['Check-in at the MCUT international dormitory in the evening', 'Structured show-and-tell activity — each student brings one item that represents home', 'Free time to cook, talk, watch a film, or play games together', 'Debrief breakfast the next morning'],
        ),
        'title_zh': '多元文化室友',
        'short_description_zh': '在國際宿舍與來自不同國家的學生共度一晚。',
        'description_zh': desc_zh(
            intro='「多元文化室友」是一場宿舍住宿體驗，來自不同國籍的學員兩兩配對，成為臨時室友。',
            details='分享你的晚間習慣、音樂、零食與故事。到了早晨，你對不同文化的日常生活會有更深的體會。',
            expect=['傍晚在MCUT國際宿舍報到', '每人帶一件代表家鄉的物品進行分享活動', '自由時間可一起煮飯、聊天、看電影或玩遊戲', '隔天早晨共進早餐並分享感想'],
        ),
        'date': datetime(2025, 5, 3, 18, 0),
        'location': 'MCUT International Dormitory',
        'capacity': 30,
        'registered_count': 22,
        'reflection_prompts': ['What habit or routine of your roommate surprised you most?', 'Was there a moment of genuine connection despite cultural differences?', 'What would you do differently if you did this again?'],
        'reflection_prompts_zh': ['你的室友有什麼生活習慣最讓你意外？', '有沒有跨越文化差異的真實連結時刻？', '如果重來一次，你會做什麼不一樣的事？'],
    },
    {
        'title': 'MCUT Toastmasters',
        'short_description': 'Practise public speaking in English in a supportive, international setting.',
        'description': desc(
            intro='The MCUT Toastmasters session is a welcoming English-language speaking club meeting open to all Li-Ze Academy participants.',
            details='Whether you are a confident speaker or terrified of the microphone, Toastmasters provides a structured and encouraging environment to practise.',
            expect=['A prepared short speech (1–2 minutes) on any topic you choose', 'Table Topics — impromptu 1-minute responses to surprise questions', 'Positive, constructive feedback from fellow participants', 'No experience required — first-timers are especially welcome'],
        ),
        'title_zh': '演講俱樂部',
        'short_description_zh': '在友善且多元的環境中練習英語公開演講。',
        'description_zh': desc_zh(
            intro='MCUT演講俱樂部是一個以英語為主的演講練習聚會，歡迎所有麗澤書院學員參加。',
            details='無論你是充滿自信的演說者，還是對麥克風感到害怕，Toastmasters都提供一個有結構、充滿鼓勵的練習環境。',
            expect=['準備一篇1至2分鐘的短講，主題自由', '即席發言——針對臨時問題作1分鐘回應', '來自學員的正向、具體反饋', '零經驗歡迎——初次參加者特別受歡迎'],
        ),
        'date': datetime(2025, 4, 25, 18, 30),
        'location': 'Room A302, MCUT Administration Building',
        'capacity': 25,
        'registered_count': 15,
        'reflection_prompts': ['What was the most difficult part of speaking in front of others?', 'What feedback did you receive that you want to act on?', 'How does public speaking feel different in English vs your home language?'],
        'reflection_prompts_zh': ['在眾人面前演講，你覺得最困難的部分是什麼？', '有什麼反饋是你想要落實的？', '用英語演講和用母語演講，感受有什麼不同？'],
    },
    {
        'title': 'Good Night, MCUT Buddy',
        'short_description': 'An informal evening meet-up pairing international and local students for a city night out.',
        'description': desc(
            intro='Good Night, MCUT Buddy is a relaxed, student-led evening where international students are paired with local MCUT buddies to explore New Taipei City together.',
            details='No formal itinerary — just good company, local food stalls, night markets, and conversations that flow naturally when the pressure is off.',
            expect=['Meeting your MCUT local buddy at the campus main gate at 7pm', 'A self-guided evening out — night market, bubble tea, a walk along the river', 'A small challenge card with optional activities to try together', 'Back to campus by 10:30pm'],
        ),
        'title_zh': '晚安！MCUT夥伴',
        'short_description_zh': '與本地MCUT夥伴一起探索新北市夜晚的輕鬆夜遊。',
        'description_zh': desc_zh(
            intro='「晚安！MCUT夥伴」是一個輕鬆的學生自主夜晚，國際學員與本地MCUT夥伴配對，一起探索新北市。',
            details='沒有固定行程——只有好夥伴、路邊攤、夜市，以及在輕鬆氣氛下自然流淌的對話。',
            expect=['晚上7點在MCUT校門口與本地夥伴會合', '自由探索——夜市、珍珠奶茶、沿河散步', '一張附有選擇性任務的挑戰卡', '晚上10點半前返回校園'],
        ),
        'date': datetime(2025, 3, 29, 19, 0),
        'location': 'MCUT Main Gate → New Taipei City',
        'capacity': 40,
        'registered_count': 35,
        'reflection_prompts': ['What surprised you most about a night out in Taiwan?', 'Did you and your buddy find any common ground? What was it?', 'What would you recommend to a friend visiting Taiwan for the first time?'],
        'reflection_prompts_zh': ['在台灣的夜晚，什麼最讓你驚喜？', '你和夥伴有找到共同話題嗎？是什麼？', '如果朋友第一次來台灣，你最想推薦什麼？'],
    },
    {
        'title': 'Get the Picture',
        'short_description': 'A visual storytelling workshop exploring cultural identity through photography.',
        'description': desc(
            intro='Get the Picture is a half-day photography and storytelling workshop. You will use your phone and a set of prompts to capture images that represent your culture, your identity, and your experience in Taiwan.',
            details='At the end of the session, the group shares and discusses the images together — often the most interesting part.',
            expect=['A short introduction to visual storytelling', 'Two hours of free photography around campus and the neighbourhood', 'A group sharing session — each person presents 3 photos and explains their meaning', "A printed photo zine combining everyone's best shots (given out at the final event)"],
        ),
        'title_zh': '影像說故事',
        'short_description_zh': '透過攝影探索文化認同的視覺敘事工作坊。',
        'description_zh': desc_zh(
            intro='「影像說故事」是一個半日攝影與敘事工作坊。你將用手機和一組提示，拍下代表你的文化、身份認同和台灣體驗的影像。',
            details='活動最後，大家一起分享和討論彼此的照片——這往往是最精彩的部分。',
            expect=['視覺敘事簡介', '兩小時在校園及周邊自由拍攝', '分享會——每人展示3張照片並說明其意義', '集結所有人最佳作品的攝影小冊（於學期末活動發放）'],
        ),
        'date': datetime(2025, 4, 5, 10, 0),
        'location': 'MCUT Campus & surroundings',
        'capacity': 20,
        'registered_count': 14,
        'reflection_prompts': ['Which photo are you most proud of, and why did you take it?', 'Was there a moment you wanted to photograph but chose not to? Why?', 'What does your set of photos say about how you see Taiwan?'],
        'reflection_prompts_zh': ['你最自豪的是哪一張照片？為什麼拍它？', '有沒有一個你想拍但選擇不拍的瞬間？原因是什麼？', '你的照片集呈現了你如何看待台灣？'],
    },
    {
        'title': 'Global Learners',
        'short_description': 'Join a structured cross-cultural dialogue series with students from 10+ countries.',
        'description': desc(
            intro='Global Learners is a series of facilitated conversations where students from different national backgrounds tackle real questions together — education, family, money, identity, and more.',
            details='Sessions are designed to go deeper than small talk and surface the genuine differences (and surprising similarities) in how people around the world see everyday life.',
            expect=['Small mixed-nationality groups of 4–5 students', 'A new discussion theme each session (e.g. "How did you choose your university?")', 'A facilitator to keep things moving and respectful', 'A short written reflection after each session'],
        ),
        'title_zh': '全球學習者',
        'short_description_zh': '加入跨越10個以上國籍的跨文化對話系列活動。',
        'description_zh': desc_zh(
            intro='「全球學習者」是一系列引導式對話，來自不同國籍的學生一起探討真實問題——教育、家庭、金錢、身份認同等。',
            details='每場活動設計為深入小談，挖掘世界各地的人對日常生活的真實差異（以及令人驚喜的相似之處）。',
            expect=['4至5人的混合國籍小組', '每場一個新討論主題（例如：你是如何選擇大學的？）', '引導員協助對話流暢且互相尊重', '每場結束後寫一小段反思'],
        ),
        'date': datetime(2025, 3, 15, 14, 0),
        'location': 'International Lounge, MCUT',
        'capacity': 30,
        'registered_count': 28,
        'reflection_prompts': ["What assumption about another culture did today's conversation challenge?", 'Was there a viewpoint shared today that you found genuinely difficult to understand?', 'What question do you wish you had asked?'],
        'reflection_prompts_zh': ['今天的對話挑戰了你對另一種文化的什麼假設？', '有沒有今天分享的觀點讓你真的很難理解？', '你希望你問過哪個問題？'],
    },
    {
        'title': 'Memories Making',
        'short_description': 'A craft workshop where students create a physical keepsake to remember their time in Taiwan.',
        'description': desc(
            intro='Memories Making is a hands-on craft workshop at the end of the semester. Using photos, fabric, and simple materials, each student creates a small book or memory box capturing their highlights from the Li-Ze Academy programme.',
            expect=['Printed copies of your favourite photos from the programme', 'Craft materials: fabric swatches, stamps, coloured paper, pens', 'Guided templates to help structure your keepsake', 'Time to share and talk about your favourite memory'],
        ),
        'title_zh': '記憶手作',
        'short_description_zh': '在手作工坊中親手製作紀念品，留住你在台灣的美好時光。',
        'description_zh': desc_zh(
            intro='「記憶手作」是學期末的手作工坊。學員利用照片、布料和簡單材料，製作一本小書或記憶盒，記錄麗澤書院的美好片段。',
            expect=['課程精選照片沖印版', '手作材料：布料樣本、印章、彩色紙、筆', '引導你完成紀念品的範本', '分享與談論最喜歡的記憶的時光'],
        ),
        'date': datetime(2025, 6, 7, 14, 0),
        'location': 'Art Studio, MCUT',
        'capacity': 25,
        'registered_count': 10,
        'reflection_prompts': ['Which Li-Ze Academy event had the biggest impact on you, and why?', 'What is one thing you will carry back home from this programme?', "If you could tell next semester's participants one thing, what would it be?"],
        'reflection_prompts_zh': ['麗澤書院的哪個活動對你影響最深？為什麼？', '你最想把什麼帶回家鄉？', '如果你能告訴下學期的學員一件事，你會說什麼？'],
    },
    {
        'title': 'Lunch English',
        'short_description': 'A casual weekly lunch where local and international students practise English over food.',
        'description': desc(
            intro='Lunch English runs every Thursday during the semester. It is the most relaxed activity in the programme — just lunch, good conversation, and a weekly conversation card to spark discussion.',
            details='Local students get English practice. International students get local friends. Everyone gets free bubble tea.',
            expect=['Meet at the MCUT cafeteria at 12:00 on Thursdays', 'Mixed seating of local and international students', 'One conversation prompt card per table', 'Absolutely no pressure — come when you can'],
        ),
        'title_zh': '午餐英語',
        'short_description_zh': '每週輕鬆午餐，本地與國際學生一起練習英語交流。',
        'description_zh': desc_zh(
            intro='「午餐英語」每學期每週四舉行，是課程中最輕鬆的活動——就是午餐、好聊天，加上一張引發討論的話題卡。',
            details='本地學生練英語，國際學生交本地朋友，大家都有免費珍珠奶茶。',
            expect=['週四中午12點在MCUT餐廳集合', '本地與國際學生混坐', '每桌一張對話提示卡', '完全無壓力——有空就來'],
        ),
        'date': datetime(2025, 3, 6, 12, 0),
        'location': 'MCUT Main Cafeteria',
        'capacity': 50,
        'registered_count': 32,
        'reflection_prompts': ['What topic came up today that you had never talked about in English before?', 'Did you learn any new slang or expressions? What were they?'],
        'reflection_prompts_zh': ['今天有什麼話題是你以前從未用英語討論過的？', '你學到了什麼新的說法或俚語？'],
    },
    {
        'title': 'Mandarin 101',
        'short_description': 'Learn the basics of Mandarin Chinese — tones, greetings, and survival phrases.',
        'description': desc(
            intro='Mandarin 101 is a short, practical Mandarin mini-course for international students with little or no Chinese language background.',
            details='Classes are taught by MCUT language students and focus entirely on what you actually need: greetings, ordering food, getting around, and saying polite things that Taiwanese people will genuinely appreciate.',
            expect=['4 sessions of 90 minutes each, spread across the semester', 'Tone practice, Pinyin, and characters for absolute beginners', 'Real situations: night market, convenience store, taxi, restaurant', 'Optional homework challenges to try your Mandarin outside the classroom'],
        ),
        'title_zh': '中文入門',
        'short_description_zh': '學習普通話基礎——聲調、問候語與生活實用短句。',
        'description_zh': desc_zh(
            intro='「中文入門」是專為沒有或幾乎沒有中文基礎的國際學生設計的短期實用中文課程。',
            details='課程由MCUT語言學生教授，完全聚焦在你真正需要的內容：問候、點餐、問路，以及台灣人會真心欣賞的禮貌用語。',
            expect=['共4堂課，每堂90分鐘，分散於學期中', '初學者的聲調練習、拼音與漢字', '真實生活情境：夜市、便利商店、計程車、餐廳', '課外挑戰作業，在教室外練習說中文'],
        ),
        'date': datetime(2025, 3, 10, 17, 0),
        'location': 'Language Lab, MCUT Building B',
        'capacity': 20,
        'registered_count': 20,
        'reflection_prompts': ['Did you try using any Mandarin outside the classroom this week? What happened?', 'Which tone is hardest for you, and why do you think that is?', 'How does learning even a little of another language change how you see its speakers?'],
        'reflection_prompts_zh': ['你這週有在課外試著說中文嗎？結果如何？', '哪個聲調對你最困難？你認為原因是什麼？', '學了一點另一種語言之後，你對這個語言的使用者有什麼不同的感受？'],
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
                event.title_zh = data.get('title_zh')
                event.short_description_zh = data.get('short_description_zh')
                event.full_description_zh = data.get('description_zh')
                event.reflection_prompts_zh = data.get('reflection_prompts_zh', [])
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
