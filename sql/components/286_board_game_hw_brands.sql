INSERT INTO hardware_brand (name)
VALUES ('Asmodee'),
       ('Buffalo Games'),
       ('Days of Wonder'),
       ('Eagle-Gryphon Games'),
       ('Fantasy Flight Games'),
       ('Gamewright'),
       ('Hasbro'),
       ('Iello'),
       ('Jumbo'),
       ('Kosmos'),
       ('Lego Games'),
       ('Mattel'),
       ('North Star Games'),
       ('Pandasaurs Games'),
       ('Queen Games'),
       ('Ravensburger'),
       ('Space Cowboys'),
       ('Theory 11'),
       ('University Games'),
       ('Victory Point Games'),
       ('Winning Moves Games'),
       ('XYZ Game Labs'),
       ('Yellow Mountain Imports'),
       ('Z-Man Games')
ON CONFLICT
    DO NOTHING;