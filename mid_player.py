import time
import mido
import fluidsynth  
MIDI_PATH = "twinkle.mid"                 # <- your MIDI file
SOUNDFONT = "GeneralUser-GS.sf2"   # <- your .sf2 file

# Start a FluidSynth software synth with the default audio driver
fs = fluidsynth.Synth()
fs.start()

# Load the SoundFont and set an initial program (bank=0, preset=0) on all 16 channels
sfid = fs.sfload(SOUNDFONT)
for ch in range(16):
    fs.program_select(ch, sfid, 0, 0)

# Stream MIDI with correct timing and translate messages to the synth
mid = mido.MidiFile(MIDI_PATH)

try:
    for msg in mid.play():  # honors tempo & delta times
        if msg.is_meta:
            # Tempo is already handled by mid.play(); ignore other meta for realtime playback
            continue

        t = msg.type
        ch = getattr(msg, "channel", 0)

        if t == "note_on":
            fs.noteon(ch, msg.note, msg.velocity)
        elif t == "note_off":
            fs.noteoff(ch, msg.note)
        elif t == "control_change":
            fs.cc(ch, msg.control, msg.value)
        elif t == "program_change":
            # Change instrument (program) on this channel
            fs.program_select(ch, sfid, 0, msg.program)
        elif t == "pitchwheel":
            # FluidSynth expects 14-bit bend value in [-8192, 8191]
            fs.pitch_bend(ch, msg.pitch)
        elif t == "aftertouch":
            fs.channel_pressure(ch, msg.value)
        elif t == "polytouch":
            fs.poly_pressure(ch, msg.note, msg.value)
        # You can add more mappings if your file uses them (e.g., sysex -> ignore)
finally:
    # Let lingering releases finish, then close cleanly
    time.sleep(0.2)
    fs.delete()