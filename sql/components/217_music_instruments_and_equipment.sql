INSERT INTO hardware_category (name)
VALUES ('Music Instruments and Equipment')
ON CONFLICT
    DO NOTHING;

-- Music Instruments and Equipment
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Acoustic Guitar', 17),
       ('Audio Interface', 17),
       ('Bass Guitar', 17),
       ('Cello', 17),
       ('Clarinet', 17),
       ('Condenser Microphone', 17),
       ('Digital Audio Workstation (DAW)', 17),
       ('Digital Mixer', 17),
       ('Digital Piano', 17),
       ('DJ Mixer', 17),
       ('Drum Kit', 17),
       ('Drum Machine', 17),
       ('Dynamic Microphone', 17),
       ('Electric Guitar', 17),
       ('Effects Pedals', 17),
       ('Flute', 17),
       ('French Horn', 17),
       ('Harmonica', 17),
       ('Headphones', 17),
       ('Keyboard', 17),
       ('Microphone Preamp', 17),
       ('MIDI Controller', 17),
       ('MIDI Keyboard', 17),
       ('Mixing Console', 17),
       ('Monitor Speakers', 17),
       ('Music Stand', 17),
       ('Oboe', 17),
       ('Percussion Instruments', 17),
       ('Pop Filter', 17),
       ('Ribbon Microphone', 17),
       ('Saxophone', 17),
       ('Sequencer', 17),
       ('Sound Mixer', 17),
       ('Speaker', 17),
       ('Studio Rack', 17),
       ('Synthesizer', 17),
       ('Trombone', 17),
       ('Trumpet', 17),
       ('Turntable', 17),
       ('Ukulele', 17),
       ('USB Microphone', 17),
       ('Violin', 17),
       ('Vocal Booth', 17),
       ('Xylophone', 17)
ON CONFLICT
    DO NOTHING;
