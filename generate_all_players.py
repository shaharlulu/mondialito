import json
import random

# הנבחרות המובילות עם הכוכבים האמיתיים שלהן
top_teams = {
    "Argentina": [
        {"name": "Emiliano Martinez", "position": "gk", "price": 60},
        {"name": "Cristian Romero", "position": "def", "price": 60},
        {"name": "Nicolas Otamendi", "position": "def", "price": 55},
        {"name": "Rodrigo De Paul", "position": "mid", "price": 70},
        {"name": "Alexis Mac Allister", "position": "mid", "price": 75},
        {"name": "Lionel Messi", "position": "fwd", "price": 130}, # 13.0m
        {"name": "Julian Alvarez", "position": "fwd", "price": 95},
        {"name": "Lautaro Martinez", "position": "fwd", "price": 90}
    ],
    "France": [
        {"name": "Mike Maignan", "position": "gk", "price": 60},
        {"name": "William Saliba", "position": "def", "price": 65},
        {"name": "Theo Hernandez", "position": "def", "price": 65},
        {"name": "N'Golo Kante", "position": "mid", "price": 70},
        {"name": "Aurelien Tchouameni", "position": "mid", "price": 70},
        {"name": "Antoine Griezmann", "position": "mid", "price": 95},
        {"name": "Kylian Mbappe", "position": "fwd", "price": 140}, # 14.0m
        {"name": "Ousmane Dembele", "position": "fwd", "price": 85}
    ],
    "England": [
        {"name": "Jordan Pickford", "position": "gk", "price": 60},
        {"name": "Kyle Walker", "position": "def", "price": 60},
        {"name": "John Stones", "position": "def", "price": 60},
        {"name": "Declan Rice", "position": "mid", "price": 70},
        {"name": "Jude Bellingham", "position": "mid", "price": 115}, # 11.5m
        {"name": "Phil Foden", "position": "mid", "price": 100},
        {"name": "Bukayo Saka", "position": "mid", "price": 100},
        {"name": "Harry Kane", "position": "fwd", "price": 120}
    ],
    "Brazil": [
        {"name": "Alisson", "position": "gk", "price": 60},
        {"name": "Marquinhos", "position": "def", "price": 60},
        {"name": "Bruno Guimaraes", "position": "mid", "price": 75},
        {"name": "Lucas Paqueta", "position": "mid", "price": 75},
        {"name": "Vinicius Junior", "position": "fwd", "price": 125}, # 12.5m
        {"name": "Rodrygo", "position": "fwd", "price": 95},
        {"name": "Raphinha", "position": "fwd", "price": 85},
        {"name": "Endrick", "position": "fwd", "price": 80}
    ],
    "Spain": [
        {"name": "Unai Simon", "position": "gk", "price": 55},
        {"name": "Rodri", "position": "mid", "price": 80},
        {"name": "Pedri", "position": "mid", "price": 75},
        {"name": "Lamine Yamal", "position": "mid", "price": 95},
        {"name": "Nico Williams", "position": "mid", "price": 90},
        {"name": "Alvaro Morata", "position": "fwd", "price": 80}
    ],
    "Portugal": [
        {"name": "Diogo Costa", "position": "gk", "price": 60},
        {"name": "Ruben Dias", "position": "def", "price": 65},
        {"name": "Bruno Fernandes", "position": "mid", "price": 105},
        {"name": "Bernardo Silva", "position": "mid", "price": 95},
        {"name": "Rafael Leao", "position": "fwd", "price": 90},
        {"name": "Cristiano Ronaldo", "position": "fwd", "price": 105} # 10.5m
    ]
}

# רשימת שאר הנבחרות שישתתפו במונדיאל (48 סך הכל)
all_countries = [
    "Argentina", "France", "England", "Brazil", "Spain", "Portugal", "Germany", "Italy", 
    "Netherlands", "Belgium", "Croatia", "Uruguay", "USA", "Mexico", "Canada", "Morocco",
    "Senegal", "Japan", "South Korea", "Switzerland", "Denmark", "Colombia", "Ecuador",
    "Peru", "Chile", "Wales", "Poland", "Sweden", "Serbia", "Iran", "Saudi Arabia",
    "Australia", "Cameroon", "Ghana", "Tunisia", "Algeria", "Nigeria", "Mali", "Ivory Coast",
    "Qatar", "UAE", "Uzbekistan", "New Zealand", "Costa Rica", "Panama", "Honduras", "Jamaica", "South Africa"
]

world_cup_squads = {}

# פונקציה להגרלת מחיר חוקי בין 5.0 (50) ל-10.0 (100) לשחקנים משלימים
def get_random_price(position):
    if position == "gk": return random.randint(50, 60)
    if position == "def": return random.randint(50, 65)
    if position == "mid": return random.randint(50, 75)
    if position == "fwd": return random.randint(55, 85)

# בניית הסגלים (26 שחקנים לכל נבחרת)
for country in all_countries:
    squad = []
    
    # אם זו נבחרת גדולה, נכניס קודם את הכוכבים האמיתיים
    if country in top_teams:
        squad.extend(top_teams[country])
        
    # משלימים ל-26 שחקנים בדיוק
    current_count = len(squad)
    for i in range(current_count + 1, 27):
        # מחלקים לעמדות הגיוניות כדי שאפשר יהיה לבנות הרכב (3 שוערים, 8 הגנה, 8 קישור, 7 התקפה)
        pos = "gk" if i <= 3 else "def" if i <= 11 else "mid" if i <= 19 else "fwd"
        squad.append({
            "name": f"{country} Player {i}",
            "position": pos,
            "price": get_random_price(pos)
        })
        
    world_cup_squads[country] = squad

# שמירה לקובץ
with open('players_full.json', 'w', encoding='utf-8') as f:
    json.dump(world_cup_squads, f, ensure_ascii=False, indent=4)

total_players = sum(len(team) for team in world_cup_squads.values())
print(f"✅ קובץ players_full.json נוצר בהצלחה!")
print(f"🌍 סך הכל נבחרות: {len(world_cup_squads)}")
print(f"⚽ סך הכל שחקנים: {total_players}")