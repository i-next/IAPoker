#!/usr/bin/env python3
"""Simple test to verify the Players_Tournament join table is populated"""

from models.database import db
import models.countrycity
import models.players
import models.tournaments
from pony.orm import db_session
import sqlite3
import os

# Use existing database (don't delete to avoid lock issues)
db_path = r'D:\IA\Softwares\IA Poker\database.sqlite'
print("✓ Using existing database")

# Bind and generate
db.bind(provider='sqlite', filename=db_path, create_db=True)
db.generate_mapping(create_tables=True)
print("✓ Database initialized and tables created")

# Create test data
with db_session():
    print("\n--- Creating test data ---")
    
    # Create country/city
    country = models.countrycity.CountryCity(name='France-Paris')
    print(f"✓ Created CountryCity: {country}")
    
    # Create player
    player = models.players.Players(pseudo='test_player_1', countrycity=country)
    print(f"✓ Created Player: {player}")
    
    # Create tournament
    tournament = models.tournaments.Tournament(
        tournament_id=9999,
        date='2026-08-31T12:00:00',
        nb_players=2,
        buy_in_total=10.0,
        dotation=100.0,
        position=1,
        gain=50.0,
        profit=40.0,
        newone=True
    )
    print(f"✓ Created Tournament: {tournament}")
    
    # Add player to tournament
    tournament.players.add(player)
    print(f"✓ Added player to tournament")
    print(f"   Tournament players: {list(tournament.players)}")
    print(f"   Player tournaments: {list(player.tournaments)}")

# Now check directly in SQLite
print("\n--- Direct SQLite verification ---")
conn = sqlite3.connect(db_path)

# List all tables
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print(f"All tables: {[t[0] for t in tables]}")

# Check Players_Tournament table content
print("\nPlayers_Tournament table structure:")
schema = conn.execute("PRAGMA table_info(Players_Tournament)").fetchall()
for col in schema:
    print(f"  {col}")

print("\nPlayers_Tournament table content:")
rows = conn.execute("SELECT * FROM Players_Tournament").fetchall()
if rows:
    print(f"  ✓ FOUND {len(rows)} row(s):")
    for row in rows:
        print(f"    {row}")
else:
    print("  ✗ TABLE IS EMPTY!")

# Show all player and tournament records too
print("\nPlayers table:")
players = conn.execute("SELECT id, pseudo FROM Players").fetchall()
for p in players:
    print(f"  {p}")

print("\nTournament table:")
tournaments = conn.execute("SELECT id, tournament_id, newone FROM Tournament").fetchall()
for t in tournaments:
    print(f"  {t}")

conn.close()
