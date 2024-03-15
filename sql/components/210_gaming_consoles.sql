INSERT INTO hardware_category (name)
VALUES ('Gaming Consoles')

ON CONFLICT
    DO NOTHING;

-- Gaming Consoles
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Atari 2600', 10),
       ('Atari 5200', 10),
       ('Atari 7800', 10),
       ('Atari Jaguar', 10),
       ('ColecoVision', 10),
       ('Commodore 64 Games System', 10),
       ('Intellivision', 10),
       ('Magnavox Odyssey', 10),
       ('Microsoft Xbox', 10),
       ('Microsoft Xbox 360', 10),
       ('Microsoft Xbox One', 10),
       ('Microsoft Xbox Series X', 10),
       ('Neo Geo', 10),
       ('Neo Geo Pocket', 10),
       ('Nintendo 3DS', 10),
       ('Nintendo 64', 10),
       ('Nintendo DS', 10),
       ('Nintendo Entertainment System (NES)', 10),
       ('Nintendo Game Boy', 10),
       ('Nintendo Game Boy Advance', 10),
       ('Nintendo Game Boy Color', 10),
       ('Nintendo GameCube', 10),
       ('Nintendo Switch', 10),
       ('Nintendo Wii', 10),
       ('Nintendo Wii U', 10),
       ('Nokia N-Gage', 10),
       ('Panasonic 3DO', 10),
       ('Philips CD-i', 10),
       ('PlayStation', 10),
       ('PlayStation 2', 10),
       ('PlayStation 3', 10),
       ('PlayStation 4', 10),
       ('PlayStation 5', 10),
       ('PlayStation Portable (PSP)', 10),
       ('PlayStation Vita', 10),
       ('Sega Dreamcast', 10),
       ('Sega Game Gear', 10),
       ('Sega Genesis', 10),
       ('Sega Master System', 10),
       ('Sega Saturn', 10),
       ('Steam Deck', 10),
       ('Super Nintendo Entertainment System (SNES)', 10),
       ('TurboGrafx-16', 10),
       ('Valve Steam Machine', 10)
ON CONFLICT
    DO NOTHING;
