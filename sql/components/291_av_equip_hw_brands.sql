INSERT INTO hardware_brand (name)
VALUES ('Bose'),
       ('Canon'),
       ('Denon'),
       ('GoPro'),
       ('JBL'),
       ('Nikon'),
       ('Panasonic'),
       ('Pioneer'),
       ('Samsung'),
       ('Sennheiser'),
       ('Sony'),
       ('Yamaha'),
       ('Bang & Olufsen'),
       ('Blackmagic Design'),
       ('DJI'),
       ('Fujifilm'),
       ('Harman Kardon'),
       ('Kodak'),
       ('Leica'),
       ('Marantz'),
       ('Olympus'),
       ('Rode Microphones'),
       ('Shure'),
       ('Vizio'),
       ('Zeiss')
ON CONFLICT
    DO NOTHING;