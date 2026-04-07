import sqlite3
import random
import os

random.seed(42) # HGTTG

SONGS = [  # (title, artist, genre, tempo, danceability, energy, valence, loudness, speechiness)
    # Radiohead
    ("Creep", "Radiohead", "Alt-Rock", 92, 0.45, 0.82, 0.22, -7.8, 0.05),
    ("Fake Plastic Trees", "Radiohead", "Alt-Rock", 76, 0.38, 0.55, 0.18, -9.1, 0.03),
    ("High and Dry", "Radiohead", "Alt-Rock", 86, 0.42, 0.60, 0.30, -8.5, 0.04),
    ("Just", "Radiohead", "Alt-Rock", 120, 0.48, 0.88, 0.38, -6.2, 0.05),
    ("My Iron Lung", "Radiohead", "Alt-Rock", 132, 0.44, 0.90, 0.32, -5.8, 0.05),
    ("Karma Police", "Radiohead", "Art-Rock", 76, 0.40, 0.60, 0.28, -9.2, 0.04),
    ("No Surprises", "Radiohead", "Art-Rock", 75, 0.38, 0.45, 0.32, -10.5, 0.03),
    ("Lucky", "Radiohead", "Art-Rock", 68, 0.35, 0.55, 0.20, -10.8, 0.03),
    ("Everything In Its Right Place", "Radiohead", "Art-Rock", 138, 0.48, 0.58, 0.25, -9.8, 0.03),
    ("How to Disappear Completely", "Radiohead", "Art-Rock", 60, 0.25, 0.40, 0.10, -12.2, 0.02),
    ("Idioteque", "Radiohead", "Electronic", 152, 0.55, 0.75, 0.20, -8.5, 0.04),
    ("The National Anthem", "Radiohead", "Art-Rock", 138, 0.52, 0.82, 0.22, -7.2, 0.06),
    ("Pyramid Song", "Radiohead", "Art-Rock", 58, 0.30, 0.48, 0.15, -11.0, 0.03),
    ("Knives Out", "Radiohead", "Art-Rock", 132, 0.45, 0.65, 0.28, -8.8, 0.04),
    ("2 + 2 = 5", "Radiohead", "Art-Rock", 112, 0.42, 0.85, 0.25, -7.0, 0.05),
    ("There There", "Radiohead", "Art-Rock", 96, 0.48, 0.80, 0.30, -7.5, 0.04),
    ("Where I End and You Begin", "Radiohead", "Art-Rock", 136, 0.45, 0.78, 0.22, -7.8, 0.04),
    ("Weird Fishes/Arpeggi", "Radiohead", "Art-Rock", 138, 0.50, 0.72, 0.35, -8.2, 0.03),
    ("All I Need", "Radiohead", "Art-Rock", 72, 0.32, 0.62, 0.18, -10.2, 0.03),
    ("Reckoner", "Radiohead", "Art-Rock", 86, 0.42, 0.55, 0.28, -9.5, 0.03),
    ("House of Cards", "Radiohead", "Art-Rock", 78, 0.38, 0.48, 0.25, -10.8, 0.03),
    ("Lotus Flower", "Radiohead", "Electronic", 94, 0.55, 0.60, 0.22, -9.0, 0.04),
    ("Codex", "Radiohead", "Art-Rock", 58, 0.22, 0.35, 0.12, -12.8, 0.02),
    ("Give Up the Ghost", "Radiohead", "Art-Rock", 66, 0.28, 0.38, 0.18, -11.5, 0.03),
    ("Separator", "Radiohead", "Art-Rock", 94, 0.45, 0.55, 0.30, -9.8, 0.03),
    ("Morning Bell", "Radiohead", "Art-Rock", 88, 0.40, 0.65, 0.22, -9.0, 0.04),
    ("Optimistic", "Radiohead", "Art-Rock", 112, 0.48, 0.78, 0.35, -7.5, 0.04),
    ("In Limbo", "Radiohead", "Art-Rock", 104, 0.42, 0.68, 0.28, -8.5, 0.03),
    ("Dollars and Cents", "Radiohead", "Art-Rock", 96, 0.38, 0.62, 0.20, -9.2, 0.04),
    ("Sit Down Stand Up", "Radiohead", "Art-Rock", 108, 0.44, 0.72, 0.18, -8.0, 0.05),
    ("Sail to the Moon", "Radiohead", "Art-Rock", 64, 0.28, 0.42, 0.22, -11.2, 0.03),
    ("Backdrifts", "Radiohead", "Electronic", 118, 0.50, 0.65, 0.20, -9.0, 0.04),
    ("Go to Sleep", "Radiohead", "Art-Rock", 92, 0.42, 0.70, 0.28, -8.5, 0.04),
    ("A Punchup at a Wedding", "Radiohead", "Art-Rock", 88, 0.45, 0.58, 0.32, -9.5, 0.04),
    ("Myxomatosis", "Radiohead", "Art-Rock", 132, 0.48, 0.85, 0.22, -6.8, 0.06),
    ("Scatterbrain", "Radiohead", "Art-Rock", 96, 0.40, 0.55, 0.25, -10.0, 0.03),
    ("A Wolf at the Door", "Radiohead", "Art-Rock", 108, 0.45, 0.68, 0.18, -8.8, 0.08),
    ("Bloom", "Radiohead", "Art-Rock", 138, 0.48, 0.70, 0.22, -8.2, 0.04),
    ("Feral", "Radiohead", "Electronic", 142, 0.52, 0.72, 0.18, -8.0, 0.03),
    ("Magpie", "Radiohead", "Art-Rock", 92, 0.40, 0.58, 0.25, -9.5, 0.03),
    ("Little by Little", "Radiohead", "Art-Rock", 104, 0.44, 0.65, 0.28, -9.0, 0.04),
    ("Supercollider", "Radiohead", "Electronic", 88, 0.42, 0.52, 0.22, -10.2, 0.03),
    ("The Daily Mail", "Radiohead", "Art-Rock", 112, 0.45, 0.75, 0.20, -8.0, 0.05),
    ("Tinker Tailor Soldier Sailor", "Radiohead", "Art-Rock", 58, 0.25, 0.45, 0.15, -11.5, 0.03),
    ("Ful Stop", "Radiohead", "Art-Rock", 142, 0.50, 0.85, 0.18, -6.5, 0.05),
    ("Daydreaming", "Radiohead", "Art-Rock", 58, 0.22, 0.38, 0.12, -12.0, 0.02),
    ("Decks Dark", "Radiohead", "Art-Rock", 96, 0.42, 0.62, 0.25, -9.2, 0.03),
    ("Desert Island Disk", "Radiohead", "Art-Rock", 72, 0.35, 0.45, 0.30, -10.8, 0.03),
    ("Ful Stop", "Radiohead", "Art-Rock", 138, 0.48, 0.82, 0.20, -7.0, 0.05),
    ("Glass Eyes", "Radiohead", "Art-Rock", 54, 0.20, 0.35, 0.18, -12.5, 0.02),
    ("Identikit", "Radiohead", "Art-Rock", 112, 0.48, 0.72, 0.22, -8.2, 0.04),
    ("The Numbers", "Radiohead", "Art-Rock", 76, 0.35, 0.52, 0.28, -10.5, 0.03),
    ("Present Tense", "Radiohead", "Art-Rock", 92, 0.42, 0.58, 0.32, -9.5, 0.03),
    ("Subterranean Homesick Alien", "Radiohead", "Art-Rock", 96, 0.40, 0.62, 0.35, -9.0, 0.03),
    ("Exit Music (For a Film)", "Radiohead", "Art-Rock", 76, 0.32, 0.58, 0.15, -10.2, 0.03),
    ("Let Down", "Radiohead", "Alt-Rock", 104, 0.48, 0.72, 0.38, -8.0, 0.03),
    ("Climbing Up the Walls", "Radiohead", "Art-Rock", 128, 0.42, 0.80, 0.15, -7.5, 0.05),
    ("Electioneering", "Radiohead", "Alt-Rock", 144, 0.52, 0.90, 0.42, -5.8, 0.05),
    ("Fitter Happier", "Radiohead", "Art-Rock", 72, 0.18, 0.30, 0.08, -13.0, 0.12),
    ("The Tourist", "Radiohead", "Alt-Rock", 76, 0.38, 0.55, 0.28, -9.5, 0.03),

    ("Accompanied a Blazing Solo", "Cities Aviv", "Experimental-Rap", 60, 0.4, 0.4, 0.5, -2, 0.10),
    ("GUM", "Cities Aviv", "Experimental-Rap", 58, 0.38, 0.38, 0.45, -3, 0.12),
    ("Immortal Flame", "Cities Aviv", "Experimental-Rap", 62, 0.42, 0.42, 0.48, -2, 0.09),
    ("Man Plays the Horn", "Cities Aviv", "Experimental-Rap", 65, 0.45, 0.50, 0.55, -1, 0.08),
    ("Ways of the World", "Cities Aviv", "Experimental-Rap", 63, 0.43, 0.45, 0.50, -2, 0.10),
    ("NOT THAT I'M ANYWHERE", "Cities Aviv", "Experimental-Rap", 70, 0.55, 0.55, 0.52, -1, 0.07),
    ("If I Could Hold Your Soul", "Cities Aviv", "Experimental-Rap", 57, 0.36, 0.35, 0.42, -4, 0.14),
    ("ESCORTS", "Cities Aviv", "Experimental-Rap", 72, 0.58, 0.58, 0.54, -1, 0.06),
    ("ETA", "Cities Aviv", "Experimental-Rap", 68, 0.50, 0.52, 0.50, -2, 0.08),
    ("Black Pleasure", "Cities Aviv", "Experimental-Rap", 75, 0.62, 0.60, 0.58, -1, 0.06),
    ("Digital Lows", "Cities Aviv", "Experimental-Rap", 78, 0.65, 0.63, 0.60, -1, 0.05),
    ("Come to Life", "Cities Aviv", "Experimental-Rap", 73, 0.60, 0.58, 0.56, -1, 0.07),

    # Mogwai
    ("Mogwai Fear Satan", "Mogwai", "Post-Rock", 88, 0.30, 0.88, 0.22, -5.8, 0.02),
    ("Like Herod", "Mogwai", "Post-Rock", 76, 0.25, 0.92, 0.15, -4.5, 0.02),
    ("Summer", "Mogwai", "Post-Rock", 82, 0.32, 0.75, 0.30, -7.0, 0.02),
    ("Punk Rock", "Mogwai", "Post-Rock", 94, 0.38, 0.80, 0.28, -6.5, 0.03),
    ("Yes! I Am a Long Way from Home", "Mogwai", "Post-Rock", 86, 0.28, 0.70, 0.25, -7.5, 0.02),
    ("Cody", "Mogwai", "Post-Rock", 72, 0.25, 0.55, 0.30, -9.0, 0.02),
    ("R U Still in 2 It", "Mogwai", "Post-Rock", 78, 0.28, 0.65, 0.22, -8.2, 0.02),
    ("Ratts of the Capital", "Mogwai", "Post-Rock", 92, 0.32, 0.82, 0.20, -6.8, 0.02),
    ("Auto Rock", "Mogwai", "Post-Rock", 96, 0.35, 0.72, 0.35, -7.5, 0.02),
    ("Glasgow Mega-Snake", "Mogwai", "Post-Rock", 108, 0.40, 0.90, 0.25, -5.5, 0.02),
    ("Hunted by a Freak", "Mogwai", "Post-Rock", 104, 0.38, 0.78, 0.30, -6.8, 0.02),
    ("2 Rights Make 1 Wrong", "Mogwai", "Post-Rock", 68, 0.22, 0.50, 0.28, -10.2, 0.02),
    ("Stop Coming to My House", "Mogwai", "Post-Rock", 112, 0.42, 0.88, 0.20, -5.8, 0.02),
    ("Coolverine", "Mogwai", "Post-Rock", 98, 0.35, 0.82, 0.22, -6.5, 0.02),
    ("Mexican Grand Prix", "Mogwai", "Post-Rock", 88, 0.32, 0.75, 0.28, -7.2, 0.02),

    # Godspeed You! Black Emperor
    ("East Hastings", "Godspeed You! Black Emperor", "Post-Rock", 52, 0.18, 0.85, 0.12, -5.2, 0.04),
    ("The Dead Flag Blues", "Godspeed You! Black Emperor", "Post-Rock", 44, 0.15, 0.80, 0.08, -6.0, 0.10),
    ("Storm", "Godspeed You! Black Emperor", "Post-Rock", 48, 0.20, 0.88, 0.10, -4.8, 0.03),
    ("Sleep", "Godspeed You! Black Emperor", "Post-Rock", 40, 0.12, 0.78, 0.12, -6.5, 0.03),
    ("Moya", "Godspeed You! Black Emperor", "Post-Rock", 56, 0.22, 0.82, 0.15, -5.5, 0.02),
    ("BBF3", "Godspeed You! Black Emperor", "Post-Rock", 50, 0.16, 0.86, 0.10, -5.0, 0.02),
    ("Blaise Bailey Finnegan III", "Godspeed You! Black Emperor", "Post-Rock", 46, 0.14, 0.75, 0.08, -6.2, 0.08),
    ("The Cowboy", "Godspeed You! Black Emperor", "Post-Rock", 42, 0.12, 0.70, 0.10, -7.0, 0.03),
    ("Motherfucker=Redeemer", "Godspeed You! Black Emperor", "Post-Rock", 38, 0.10, 0.88, 0.06, -4.5, 0.02),
    ("Albanian", "Godspeed You! Black Emperor", "Post-Rock", 44, 0.14, 0.72, 0.08, -6.8, 0.03),
    ("Rockets Fall on Rocket Falls", "Godspeed You! Black Emperor", "Post-Rock", 48, 0.16, 0.80, 0.10, -5.8, 0.02),
    ("Monheim", "Godspeed You! Black Emperor", "Post-Rock", 52, 0.18, 0.68, 0.12, -7.5, 0.02),

    # Explosions in the Sky
    ("Your Hand in Mine", "Explosions in the Sky", "Post-Rock", 82, 0.38, 0.72, 0.45, -7.2, 0.02),
    ("The Birth and Death of Day", "Explosions in the Sky", "Post-Rock", 86, 0.32, 0.80, 0.35, -6.8, 0.02),
    ("Six Days at the Bottom of the Ocean", "Explosions in the Sky", "Post-Rock", 72, 0.28, 0.68, 0.30, -8.0, 0.02),
    ("First Breath After Coma", "Explosions in the Sky", "Post-Rock", 78, 0.34, 0.74, 0.40, -7.4, 0.02),
    ("The Only Moment We Were Alone", "Explosions in the Sky", "Post-Rock", 80, 0.36, 0.76, 0.42, -7.0, 0.02),
    ("Memorial", "Explosions in the Sky", "Post-Rock", 74, 0.30, 0.70, 0.38, -7.8, 0.02),
    ("catastrophe and the cure", "Explosions in the Sky", "Post-Rock", 88, 0.38, 0.78, 0.40, -6.8, 0.02),
    ("So Long, Lonesome", "Explosions in the Sky", "Post-Rock", 76, 0.32, 0.72, 0.35, -7.5, 0.02),
    ("Trembling Hands", "Explosions in the Sky", "Post-Rock", 84, 0.35, 0.75, 0.38, -7.2, 0.02),
    ("Human Qualities", "Explosions in the Sky", "Post-Rock", 78, 0.30, 0.65, 0.40, -8.0, 0.02),

    # Sigur Ros
    ("Glósóli", "Sigur Rós", "Post-Rock", 64, 0.28, 0.70, 0.35, -8.5, 0.02),
    ("Hoppípolla", "Sigur Rós", "Post-Rock", 76, 0.35, 0.65, 0.50, -9.0, 0.02),
    ("Ára bátur", "Sigur Rós", "Post-Rock", 48, 0.18, 0.55, 0.28, -11.0, 0.02),
    ("Svefn-g-englar", "Sigur Rós", "Post-Rock", 40, 0.15, 0.48, 0.20, -12.0, 0.02),
    ("Untitled #1 (Vaka)", "Sigur Rós", "Post-Rock", 44, 0.16, 0.50, 0.22, -11.5, 0.02),
    ("Njósnavélin", "Sigur Rós", "Post-Rock", 52, 0.20, 0.58, 0.25, -10.5, 0.02),
    ("Starálfur", "Sigur Rós", "Post-Rock", 56, 0.22, 0.52, 0.30, -11.0, 0.02),
    ("Vidrar vel til loftárása", "Sigur Rós", "Post-Rock", 48, 0.18, 0.60, 0.22, -10.2, 0.02),
    ("Olsen Olsen", "Sigur Rós", "Post-Rock", 60, 0.25, 0.55, 0.28, -10.8, 0.02),
    ("Festival", "Sigur Rós", "Post-Rock", 68, 0.30, 0.62, 0.35, -9.5, 0.02),
    ("Sæglópur", "Sigur Rós", "Post-Rock", 72, 0.32, 0.65, 0.30, -9.2, 0.02),
    ("Mílanó", "Sigur Rós", "Post-Rock", 58, 0.22, 0.50, 0.25, -11.2, 0.02),

    # Swans
    ("The Seer", "Swans", "Post-Rock", 38, 0.12, 0.92, 0.10, -4.1, 0.08),
    ("Bring the Sun", "Swans", "Post-Rock", 42, 0.10, 0.98, 0.08, -3.0, 0.05),
    ("A Little God in My Hands", "Swans", "Post-Rock", 92, 0.30, 0.88, 0.15, -5.0, 0.06),
    ("Frankie M", "Swans", "Post-Rock", 56, 0.20, 0.80, 0.12, -6.0, 0.07),
    ("Toussaint L'Ouverture", "Swans", "Post-Rock", 46, 0.14, 0.94, 0.08, -3.8, 0.06),
    ("Lunacy", "Swans", "Post-Rock", 50, 0.16, 0.90, 0.10, -4.2, 0.06),
    ("Screen Shot", "Swans", "Post-Rock", 44, 0.12, 0.88, 0.08, -4.5, 0.05),
    ("She Loves Us", "Swans", "Post-Rock", 52, 0.18, 0.92, 0.10, -3.8, 0.07),
    ("Cloud of Forgetting", "Swans", "Post-Rock", 40, 0.10, 0.85, 0.08, -5.0, 0.05),
    ("Oxygen", "Swans", "Post-Rock", 58, 0.22, 0.82, 0.15, -5.5, 0.06),
    ("The Glowing Man", "Swans", "Post-Rock", 36, 0.08, 0.95, 0.06, -3.2, 0.05),
    ("When Will I Return", "Swans", "Post-Rock", 72, 0.28, 0.65, 0.20, -7.8, 0.06),

    # Boris
    ("Feedbacker", "Boris", "Drone-Metal", 36, 0.08, 0.99, 0.05, -2.8, 0.03),
    ("Flood", "Boris", "Drone-Metal", 40, 0.10, 0.97, 0.06, -3.1, 0.03),
    ("Farewell", "Boris", "Post-Rock", 58, 0.22, 0.85, 0.18, -5.5, 0.04),
    ("Akuma no Uta", "Boris", "Drone-Metal", 62, 0.25, 0.90, 0.20, -4.8, 0.04),
    ("Statement", "Boris", "Drone-Metal", 34, 0.08, 0.99, 0.04, -2.5, 0.02),
    ("Furi", "Boris", "Post-Rock", 72, 0.28, 0.82, 0.25, -6.2, 0.04),
    ("Buzz-In", "Boris", "Drone-Metal", 38, 0.10, 0.96, 0.06, -3.0, 0.03),
    ("lower", "Boris", "Post-Rock", 64, 0.24, 0.78, 0.20, -6.8, 0.03),
    ("Ibitsu", "Boris", "Post-Rock", 68, 0.26, 0.80, 0.22, -6.5, 0.03),
    ("floor shuffle", "Boris", "Drone-Metal", 42, 0.12, 0.94, 0.08, -3.5, 0.02),

    # Slint
    ("Good Morning, Captain", "Slint", "Post-Rock", 78, 0.28, 0.75, 0.12, -8.0, 0.10),
    ("Washer", "Slint", "Post-Rock", 66, 0.25, 0.62, 0.15, -9.8, 0.09),
    ("The Lick", "Slint", "Post-Rock", 88, 0.32, 0.78, 0.18, -7.2, 0.08),
    ("Nosferatu Man", "Slint", "Post-Rock", 92, 0.35, 0.80, 0.20, -7.0, 0.07),
    ("Don, Aman", "Slint", "Post-Rock", 72, 0.28, 0.68, 0.15, -8.5, 0.09),
    ("Breadcrumb Trail", "Slint", "Post-Rock", 82, 0.30, 0.72, 0.18, -8.0, 0.10),
    ("Tweez", "Slint", "Post-Rock", 96, 0.35, 0.82, 0.20, -7.0, 0.07),

    # Bark Psychosis
    ("Absent Friend", "Bark Psychosis", "Post-Rock", 72, 0.28, 0.60, 0.22, -9.5, 0.03),
    ("Nocturoum", "Bark Psychosis", "Post-Rock", 68, 0.25, 0.65, 0.20, -9.0, 0.03),
    ("Blue", "Bark Psychosis", "Post-Rock", 64, 0.22, 0.55, 0.18, -10.2, 0.03),
    ("Pendulum Man", "Bark Psychosis", "Post-Rock", 76, 0.30, 0.68, 0.25, -8.8, 0.03),

    # Tortoise
    ("Djed", "Tortoise", "Post-Rock", 96, 0.48, 0.72, 0.35, -7.5, 0.02),
    ("TNT", "Tortoise", "Post-Rock", 104, 0.52, 0.68, 0.40, -8.0, 0.02),
    ("Seneca", "Tortoise", "Post-Rock", 88, 0.44, 0.65, 0.38, -8.5, 0.02),
    ("The Suspension Bridge at Iguazú Falls", "Tortoise", "Post-Rock", 92, 0.45, 0.70, 0.35, -8.0, 0.02),
    ("Along the Banks of Rivers", "Tortoise", "Post-Rock", 86, 0.42, 0.62, 0.32, -8.8, 0.02),
    ("Salt the Skies", "Tortoise", "Post-Rock", 98, 0.48, 0.72, 0.38, -7.5, 0.02),

    # Thee Silver Mt. Zion
    ("Hang on to Each Other", "Thee Silver Mt. Zion", "Post-Rock", 58, 0.22, 0.65, 0.20, -8.5, 0.05),
    ("13 Angels Standing Guard", "Thee Silver Mt. Zion", "Post-Rock", 48, 0.18, 0.60, 0.15, -9.5, 0.04),
    ("Horses in the Sky", "Thee Silver Mt. Zion", "Post-Rock", 52, 0.20, 0.62, 0.18, -9.0, 0.05),

    # This Will Destroy You
    ("Quiet", "This Will Destroy You", "Post-Rock", 72, 0.28, 0.78, 0.25, -7.0, 0.02),
    ("Glass Realms", "This Will Destroy You", "Post-Rock", 80, 0.32, 0.82, 0.28, -6.5, 0.02),
    ("Threads", "This Will Destroy You", "Post-Rock", 68, 0.25, 0.75, 0.22, -7.5, 0.02),
    ("The Mighty Rio Grande", "This Will Destroy You", "Post-Rock", 76, 0.30, 0.80, 0.25, -7.0, 0.02),
    ("Descending Upon Us Compromise", "This Will Destroy You", "Post-Rock", 64, 0.22, 0.70, 0.20, -8.0, 0.02),

    # Russian Circles
    ("Geneva", "Russian Circles", "Post-Rock", 104, 0.38, 0.88, 0.25, -5.8, 0.02),
    ("Carpe", "Russian Circles", "Post-Rock", 112, 0.42, 0.90, 0.22, -5.5, 0.02),
    ("Harper Lewis", "Russian Circles", "Post-Rock", 96, 0.36, 0.85, 0.28, -6.2, 0.02),
    ("Youngblood", "Russian Circles", "Post-Rock", 108, 0.40, 0.88, 0.25, -5.8, 0.02),
    ("Deficit", "Russian Circles", "Post-Rock", 100, 0.38, 0.86, 0.22, -6.0, 0.02),
    ("Vorel", "Russian Circles", "Post-Rock", 92, 0.35, 0.82, 0.25, -6.5, 0.02),

    # Portishead
    ("Glory Box", "Portishead", "Trip-Hop", 68, 0.40, 0.48, 0.22, -10.8, 0.04),
    ("Sour Times", "Portishead", "Trip-Hop", 98, 0.45, 0.55, 0.18, -10.0, 0.05),
    ("Roads", "Portishead", "Trip-Hop", 72, 0.35, 0.42, 0.15, -11.5, 0.03),
    ("Mysterons", "Portishead", "Trip-Hop", 84, 0.42, 0.50, 0.18, -10.5, 0.04),
    ("Wandering Star", "Portishead", "Trip-Hop", 76, 0.38, 0.48, 0.15, -11.0, 0.04),
    ("Machine Gun", "Portishead", "Trip-Hop", 88, 0.45, 0.60, 0.20, -9.8, 0.05),
    ("The Rip", "Portishead", "Trip-Hop", 64, 0.30, 0.38, 0.18, -12.0, 0.03),
    ("Silence", "Portishead", "Trip-Hop", 78, 0.38, 0.52, 0.20, -10.8, 0.04),

    # Massive Attack
    ("Teardrop", "Massive Attack", "Trip-Hop", 80, 0.48, 0.50, 0.25, -10.2, 0.04),
    ("Unfinished Sympathy", "Massive Attack", "Trip-Hop", 94, 0.55, 0.58, 0.30, -9.0, 0.05),
    ("Inertia Creeps", "Massive Attack", "Trip-Hop", 86, 0.52, 0.62, 0.20, -9.5, 0.06),
    ("Safe from Harm", "Massive Attack", "Trip-Hop", 92, 0.52, 0.60, 0.28, -9.2, 0.05),
    ("Angel", "Massive Attack", "Trip-Hop", 96, 0.50, 0.65, 0.22, -8.8, 0.05),
    ("Risingson", "Massive Attack", "Trip-Hop", 100, 0.52, 0.68, 0.20, -8.5, 0.06),
    ("Dissolved Girl", "Massive Attack", "Trip-Hop", 84, 0.45, 0.55, 0.18, -10.0, 0.04),
    ("Group Four", "Massive Attack", "Trip-Hop", 76, 0.38, 0.48, 0.15, -11.0, 0.03),

    # Mazzy Star
    ("Fade Into You", "Mazzy Star", "Dream-Pop", 68, 0.30, 0.35, 0.28, -11.2, 0.03),
    ("Halah", "Mazzy Star", "Dream-Pop", 72, 0.28, 0.32, 0.22, -11.8, 0.03),
    ("Into Dust", "Mazzy Star", "Dream-Pop", 64, 0.25, 0.28, 0.18, -12.5, 0.02),
    ("Look on Down from the Bridge", "Mazzy Star", "Dream-Pop", 60, 0.22, 0.30, 0.20, -12.2, 0.02),
    ("Flowers in December", "Mazzy Star", "Dream-Pop", 66, 0.26, 0.32, 0.22, -11.8, 0.03),
    ("Rhymes of an Hour", "Mazzy Star", "Dream-Pop", 70, 0.28, 0.35, 0.25, -11.5, 0.03),

    # My Bloody Valentine
    ("Only Shallow", "My Bloody Valentine", "Shoegaze", 160, 0.42, 0.92, 0.38, -5.2, 0.04),
    ("Loomer", "My Bloody Valentine", "Shoegaze", 88, 0.32, 0.80, 0.30, -7.5, 0.02),
    ("Sometimes", "My Bloody Valentine", "Shoegaze", 76, 0.28, 0.65, 0.35, -9.0, 0.02),
    ("When You Sleep", "My Bloody Valentine", "Shoegaze", 140, 0.50, 0.88, 0.45, -5.8, 0.03),
    ("Come in Alone", "My Bloody Valentine", "Shoegaze", 96, 0.38, 0.75, 0.32, -7.8, 0.02),
    ("Blown", "My Bloody Valentine", "Shoegaze", 132, 0.45, 0.85, 0.38, -6.2, 0.03),
    ("To Here Knows When", "My Bloody Valentine", "Shoegaze", 84, 0.30, 0.70, 0.28, -8.5, 0.02),
    ("Sometimes", "My Bloody Valentine", "Shoegaze", 76, 0.28, 0.65, 0.35, -9.2, 0.02),

    # Pixies
    ("Where Is My Mind", "Pixies", "Alt-Rock", 122, 0.44, 0.72, 0.38, -7.8, 0.04),
    ("Here Comes Your Man", "Pixies", "Alt-Rock", 140, 0.60, 0.78, 0.72, -6.2, 0.04),
    ("Gigantic", "Pixies", "Alt-Rock", 98, 0.48, 0.68, 0.48, -7.4, 0.04),
    ("Debaser", "Pixies", "Alt-Rock", 172, 0.55, 0.90, 0.55, -5.5, 0.06),
    ("Gouge Away", "Pixies", "Alt-Rock", 152, 0.52, 0.88, 0.48, -5.8, 0.05),
    ("Monkey Gone to Heaven", "Pixies", "Alt-Rock", 132, 0.50, 0.82, 0.52, -6.5, 0.05),
    ("Hey", "Pixies", "Alt-Rock", 108, 0.45, 0.75, 0.42, -7.2, 0.04),
    ("Caribou", "Pixies", "Alt-Rock", 144, 0.52, 0.85, 0.50, -6.0, 0.05),
    ("Bone Machine", "Pixies", "Alt-Rock", 148, 0.50, 0.88, 0.45, -5.8, 0.06),
]


# Make names more fun by combining random adjectives and animals
ADJECTIVES = ["Neon", "Spicy", "Cosmic", "Groovy", "Electric", "Chill", "Phonk", "Evan", "DiddyBlud"]
NOUNS = ["Panda", "Falcon", "Tiger", "Otter", "Capybara", "Wolf", "Table", "Mango", "Burger", "Mustard"]
USERS = [f"user_{i:03}" for i in range(1, 201)]

# join database with app directory, in case we run this from a different location
DB_PATH = os.path.join(os.path.dirname(__file__), "music.db")


def seed():
    # create and connect to the SQLite database created
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # create database for sql queries
    c.executescript("""
        DROP TABLE IF EXISTS songs;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS interactions;

        CREATE TABLE songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            genre TEXT NOT NULL,
            tempo REAL,
            danceability REAL,
            energy REAL,
            valence REAL,
            loudness REAL,
            speechiness REAL,
            play_count INTEGER DEFAULT 0
        );

        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            song_id INTEGER NOT NULL,
            play_count INTEGER DEFAULT 1,
            liked INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (song_id) REFERENCES songs(id),
            UNIQUE(user_id, song_id)
        );
    """)

    # insert songs into the table
    for song in SONGS:
        c.execute("""
            INSERT INTO songs (title, artist, genre, tempo, danceability, energy, valence, loudness, speechiness, play_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, song + (random.randint(1000, 500000),))

    for user in USERS:
        c.execute("INSERT INTO users (id) VALUES (?)", (user,))

    # give every user a fake listening history
    song_ids = [row[0] for row in c.execute("SELECT id FROM songs").fetchall()]

    little_god_id = c.execute(
    "SELECT id FROM songs WHERE title = ?", ("A Little God in My Hands",)
    ).fetchone()[0]

    for user in USERS:
        listened = random.sample(song_ids, k=random.randint(50, 200))
        #listened.append(little_god_id)
        for song_id in listened:
            c.execute("""
                INSERT OR IGNORE INTO interactions (user_id, song_id, play_count, liked)
                VALUES (?, ?, ?, ?)
            """, (user, song_id, random.randint(1, 100), random.randint(0, 1)))

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(SONGS)} songs and {len(USERS)} users into {DB_PATH}")


if __name__ == "__main__":
    seed()
