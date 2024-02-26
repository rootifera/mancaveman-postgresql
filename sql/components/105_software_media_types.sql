INSERT INTO software_type (name)
VALUES ('Blu-ray Disc'),
       ('Cartridge'),
       ('CD-ROM'),
       ('Digital Download'),
       ('Diskette'),
       ('DVD'),
       ('Floppy Disk'),
       ('Game Cartridge'),
       ('HD DVD'),
       ('Magnetic Tape'),
       ('Memory Card'),
       ('Memory Stick'),
       ('MiniDisc'),
       ('Optical Disc'),
       ('ROM Chip'),
       ('SD Card'),
       ('Streaming'),
       ('USB Flash Drive')
ON CONFLICT
    DO NOTHING;
