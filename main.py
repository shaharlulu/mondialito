import json
import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

import models
from database import engine, SessionLocal

# קוד ה-HTML של פאנל הניהול מוטמע ישירות בתוך השרת כדי למנוע בעיות קבצים!
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>פאנל ניהול | מונדיאל</title>
    <style>
        body { font-family: -apple-system, sans-serif; background: #050609; color: white; padding: 20px; }
        h1 { color: #5b6ef5; text-align: center; }
        .match-card { background: #131829; border: 1px solid #222c42; padding: 15px; margin-bottom: 10px; border-radius: 12px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; }
        .match-teams { font-weight: bold; font-size: 16px; min-width: 200px; }
        input[type="number"] { width: 60px; padding: 10px; border-radius: 8px; border: 1px solid #2d3a54; background: #1a2035; color: white; text-align: center; font-weight: bold; font-size: 16px; }
        select { padding: 10px; border-radius: 8px; border: 1px solid #2d3a54; background: #1a2035; color: white; font-size: 14px; }
        button { padding: 10px 20px; background: linear-gradient(135deg, #00d97e, #00b866); border: none; border-radius: 8px; color: white; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:hover { opacity: 0.8; }
        .msg { color: #00d97e; font-size: 14px; font-weight: bold; min-width: 60px; text-align: center;}
    </style>
</head>
<body>
    <h1>פאנל ניהול תוצאות 🏆</h1>
    <p style="text-align: center; color: #6b7a99;">מכאן תוכל לעדכן את תוצאות האמת. כל עדכון יחשב אוטומטית את הנקודות בטבלה של כולם.</p>
    <div id="matches" style="max-width: 800px; margin: 0 auto; margin-top: 30px;"></div>

    <script>
        async function loadMatches() {
            const res = await fetch('/api/matches');
            const matches = await res.json();
            const div = document.getElementById('matches');
            div.innerHTML = '';
            matches.forEach(m => {
                div.innerHTML += `
                    <div class="match-card">
                        <div class="match-teams">${m.hn} 🆚 ${m.an}</div>
                        <div>
                            <input type="number" id="h${m.id}" value="${m.hs !== null ? m.hs : ''}" placeholder="בית">
                            -
                            <input type="number" id="a${m.id}" value="${m.as !== null ? m.as : ''}" placeholder="חוץ">
                        </div>
                        <select id="st${m.id}">
                            <option value="scheduled" ${m.st === 'scheduled' ? 'selected' : ''}>טרם התחיל</option>
                            <option value="live" ${m.st === 'live' ? 'selected' : ''}>מחצית ראשונה</option>
                            <option value="halftime" ${m.st === 'halftime' ? 'selected' : ''}>מחצית / הפסקה</option>
                            <option value="finished" ${m.st === 'finished' ? 'selected' : ''}>סיום משחק (לחלוקת נקודות)</option>
                        </select>
                        <button onclick="saveMatch(${m.id})">עדכן תוצאה</button>
                        <div id="msg${m.id}" class="msg"></div>
                    </div>
                `;
            });
        }

        async function saveMatch(id) {
            const h = document.getElementById('h'+id).value;
            const a = document.getElementById('a'+id).value;
            const st = document.getElementById('st'+id).value;
            
            const body = {
                match_id: id,
                home_score: h === "" ? 0 : parseInt(h),
                away_score: a === "" ? 0 : parseInt(a),
                status: st
            };

            await fetch('/api/admin/update_score', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });

            const msgEl = document.getElementById('msg'+id);
            msgEl.innerText = "✓ עודכן";
            setTimeout(() => msgEl.innerText = "", 3000);
        }

        loadMatches();
    </script>
</body>
</html>
"""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def seed_db():
    db = SessionLocal()
    try:
        if not db.query(models.Player).first():
            file_to_load = 'players_full.json' if os.path.exists('players_full.json') else 'players_groups_ab.json'
            with open(file_to_load, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for team, players in data.items():
                for p in players:
                    db.add(models.Player(
                        name=p['name'],
                        team=team,
                        position=p.get('position', 'unknown').lower(),
                        price=p.get('price', 50),
                        image=p.get('image', None)
                    ))
            db.commit()
            print(f"--- שחקנים הוטענו בהצלחה מהקובץ: {file_to_load} ---")

        if not db.query(models.Match).first():
            seed_matches = [
                (1, "Mexico", "South Korea", "MX", "KR", "scheduled", None, None, "2026-06-11T22:00:00"),
                (2, "South Africa", "Czech Republic", "ZA", "CZ", "scheduled", None, None, "2026-06-12T19:00:00"),
                (3, "Canada", "Switzerland", "CA", "CH", "scheduled", None, None, "2026-06-13T22:00:00"),
                (4, "Qatar", "Bosnia", "QA", "BA", "scheduled", None, None, "2026-06-14T19:00:00"),
                (5, "Mexico", "Czech Republic", "MX", "CZ", "scheduled", None, None, "2026-06-17T22:00:00")
            ]
            for m in seed_matches:
                match_obj = models.Match(
                    match_num=m[0], home_team=m[1], away_team=m[2],
                    home_code=m[3], away_code=m[4], status=m[5],
                    home_score=m[6], away_score=m[7]
                )
                if hasattr(match_obj, 'kickoff'):
                    match_obj.kickoff = m[8]
                db.add(match_obj)
            db.commit()
            print("--- משחקים הוטענו ---")
    except Exception as e:
        print(f"שגיאת seed: {e}")
    finally:
        db.close()

# --- Schemas ---
class RegisterSchema(BaseModel):
    username: str
    display_name: str
    password: str
class LoginSchema(BaseModel):
    username: str
    password: str
class PredictionSchema(BaseModel):
    user_id: int
    match_id: int
    h: int
    a: int
class BonusSchema(BaseModel):
    user_id: int
    champ: Optional[str] = None
    scorer: Optional[str] = None
class SquadSchema(BaseModel):
    user_id: int
    squad_data: dict
    cap: Optional[str] = None
    vc: Optional[str] = None
class ScoreUpdateSchema(BaseModel):
    match_id: int
    home_score: int
    away_score: int
    status: str

# --- Routes ---
@app.get("/")
async def read_root(): 
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="index.html not found")

@app.get("/admin")
async def read_admin():
    return HTMLResponse(content=ADMIN_HTML)

@app.post("/api/register")
def register(body: RegisterSchema, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == body.username).first():
        raise HTTPException(status_code=400, detail="שם המשתמש כבר תפוס")
    user = models.User(username=body.username, pw=body.password)
    if hasattr(user, 'display_name'): user.display_name = body.display_name
    elif hasattr(user, 'display'): user.display = body.display_name
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True, "user": {"id": user.id, "username": user.username, "display_name": body.display_name}}

@app.post("/api/login")
def login(body: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == body.username).first()
    if not user or getattr(user, 'pw', '') != body.password:
        raise HTTPException(status_code=401, detail="שגיאה בפרטים")
    return {"ok": True, "user": {"id": user.id, "username": user.username, "display_name": getattr(user, 'display_name', getattr(user, 'display', user.username))}}

@app.get("/api/players")
def get_players(db: Session = Depends(get_db)):
    players = db.query(models.Player).order_by(models.Player.price.desc()).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "team": p.team, "nat": p.team,
            "position": getattr(p, 'position', 'mid'), "pos": getattr(p, 'position', 'mid').upper(),
            "price": round(getattr(p, 'price', 50) / 10, 1),
            "club": p.team,
            "rating": 80,
            "image": getattr(p, 'image', None)
        }
        for p in players
    ]

@app.get("/api/matches")
def get_matches(db: Session = Depends(get_db)):
    rows = db.query(models.Match).order_by(models.Match.match_num).all()
    return [
        {
            "id": r.match_num, "match_num": r.match_num,
            "hn": r.home_team, "home_team": r.home_team,
            "an": r.away_team, "away_team": r.away_team,
            "hc": r.home_code, "home_code": r.home_code,
            "ac": r.away_code, "away_code": r.away_code,
            "hs": r.home_score, "home_score": r.home_score,
            "as": r.away_score, "away_score": r.away_score,
            "st": getattr(r, 'status', 'scheduled'), "status": getattr(r, 'status', 'scheduled'),
            "stage": getattr(r, 'stage', 'group'),
            "ko": getattr(r, 'kickoff', None), "kickoff": getattr(r, 'kickoff', None),
        }
        for r in rows
    ]

@app.post("/api/predictions")
def save_prediction(body: PredictionSchema, db: Session = Depends(get_db)):
    match = db.query(models.Match).filter(models.Match.match_num == body.match_id).first()
    if not match: raise HTTPException(status_code=404, detail="Match not found")
    
    if hasattr(match, 'kickoff') and match.kickoff:
        try:
            kickoff_dt = datetime.fromisoformat(match.kickoff)
            if datetime.now() >= kickoff_dt:
                raise HTTPException(status_code=400, detail="המשחק כבר התחיל! לא ניתן לערוך ניחוש.")
        except Exception:
            pass

    existing = db.query(models.Prediction).filter(models.Prediction.user_id==body.user_id, models.Prediction.match_id==body.match_id).first()
    if existing: existing.h, existing.a = body.h, body.a
    else: db.add(models.Prediction(user_id=body.user_id, match_id=body.match_id, h=body.h, a=body.a))
    db.commit()
    return {"ok": True}

@app.get("/api/predictions")
def get_predictions(user_id: int, db: Session = Depends(get_db)):
    rows = db.query(models.Prediction).filter(models.Prediction.user_id == user_id).all()
    return {"predictions": {str(r.match_id): {"h": r.h, "a": r.a} for r in rows}}

@app.post("/api/bonus")
def save_bonus(body: BonusSchema, db: Session = Depends(get_db)):
    tournament_start = datetime(2026, 6, 11, 22, 0)
    if datetime.now() >= tournament_start:
         raise HTTPException(status_code=400, detail="המונדיאל התחיל, לא ניתן לשנות בונוסים.")

    existing = db.query(models.Bonus).filter(models.Bonus.user_id == body.user_id).first()
    if existing: existing.champ, existing.scorer = body.champ, body.scorer
    else: db.add(models.Bonus(user_id=body.user_id, champ=body.champ, scorer=body.scorer))
    db.commit()
    return {"ok": True}

@app.get("/api/bonus")
def get_bonus(user_id: int, db: Session = Depends(get_db)):
    row = db.query(models.Bonus).filter(models.Bonus.user_id == user_id).first()
    if not row: return {"bonus": None}
    return {"bonus": {"champ": row.champ, "scorer": row.scorer}}

@app.post("/api/squad")
def save_squad(body: SquadSchema, db: Session = Depends(get_db)):
    tournament_start = datetime(2026, 6, 11, 22, 0)
    if datetime.now() >= tournament_start:
         raise HTTPException(status_code=400, detail="המונדיאל התחיל, לא ניתן לשנות הרכבים.")

    existing = db.query(models.FantasySquad).filter(models.FantasySquad.user_id == body.user_id).first()
    if existing: existing.squad_data, existing.cap, existing.vc = body.squad_data, body.cap, body.vc
    else: db.add(models.FantasySquad(user_id=body.user_id, squad_data=body.squad_data, cap=body.cap, vc=body.vc))
    db.commit()
    return {"ok": True}

@app.get("/api/squad")
def get_squad(user_id: int, db: Session = Depends(get_db)):
    row = db.query(models.FantasySquad).filter(models.FantasySquad.user_id == user_id).first()
    if not row: return {"squad": None}
    return {"squad": {"squad_data": row.squad_data, "cap": row.cap, "vc": row.vc}}

def _calc_pts(user_id: int, db: Session) -> dict:
    preds = db.query(models.Prediction).filter(models.Prediction.user_id == user_id).all()
    total = exact = correct = 0
    for pred in preds:
        match = db.query(models.Match).filter(models.Match.match_num == pred.match_id).first()
        if not match or getattr(match, 'status', 'scheduled') != "finished" or match.home_score is None: continue
        ph, pa, ah, aa = pred.h, pred.a, match.home_score, match.away_score
        if ph == ah and pa == aa: total += 5; exact += 1
        else:
            def _dir(h, a): return "h" if h > a else ("a" if a > h else "d")
            if _dir(ph, pa) == _dir(ah, aa): total += 3; correct += 1
    return {"points": total, "exact": exact, "correct": correct}

@app.get("/api/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    rows = []
    for u in users:
        if hasattr(u, 'is_active') and not u.is_active: continue
        bet = _calc_pts(u.id, db)
        rows.append({
            "id": u.id, "display_name": getattr(u, 'display_name', getattr(u, 'display', u.username)),
            "betting_pts": bet["points"], "exact": bet["exact"], "correct": bet["correct"],
            "fantasy_pts": 0, "overall": round(bet["points"] * 0.6, 2)
        })
    def _rank(lst, key):
        lst = sorted(lst, key=lambda x: x[key], reverse=True)
        prev_val = prev_rank = None
        for i, r in enumerate(lst):
            rank = prev_rank if r[key] == prev_val else i + 1
            r["rank"] = rank
            prev_val, prev_rank = r[key], rank
        return lst
    return {
        "betting": _rank([{"id": r["id"], "display_name": r["display_name"], "points": r["betting_pts"], "exact": r["exact"], "correct": r["correct"]} for r in rows], "points"),
        "fantasy": _rank([{"id": r["id"], "display_name": r["display_name"], "points": r["fantasy_pts"]} for r in rows], "points"),
        "overall": _rank([{"id": r["id"], "display_name": r["display_name"], "betting_pts": r["betting_pts"], "fantasy_pts": r["fantasy_pts"], "overall_score": r["overall"]} for r in rows], "overall_score"),
    }

@app.post("/api/admin/update_score")
def update_score(body: ScoreUpdateSchema, db: Session = Depends(get_db)):
    match = db.query(models.Match).filter(models.Match.match_num == body.match_id).first()
    if not match: raise HTTPException(status_code=404, detail="משחק לא נמצא")
    match.home_score, match.away_score, match.status = body.home_score, body.away_score, body.status
    db.commit()
    return {"ok": True}

if __name__ == "__main__":
    seed_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)