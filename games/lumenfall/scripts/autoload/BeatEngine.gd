extends Node
## Procedural BPM-synced beat bed (no external audio file required).

const MIX_RATE := 44100.0

var _player: AudioStreamPlayer
var _playback: AudioStreamGeneratorPlayback
var _bpm: float = 174.0
var _offset_ms: float = 0.0
var _enabled: bool = true
var _phase: float = 0.0
var _song_ms: float = 0.0
var _running: bool = false


func _ready() -> void:
	_player = AudioStreamPlayer.new()
	_player.bus = &"Master"
	var gen := AudioStreamGenerator.new()
	gen.mix_rate = int(MIX_RATE)
	gen.buffer_length = 0.15
	_player.stream = gen
	add_child(_player)


func configure(bpm: float, offset_ms: float = 0.0) -> void:
	_bpm = maxf(bpm, 60.0)
	_offset_ms = offset_ms


func set_enabled(on: bool) -> void:
	_enabled = on


func start() -> void:
	_song_ms = 0.0
	_phase = 0.0
	_running = true
	if not _enabled:
		return
	_player.play()
	_playback = _player.get_stream_playback()


func stop() -> void:
	_running = false
	_player.stop()
	_playback = null


func sync_ms(ms: float) -> void:
	_song_ms = ms


func _process(delta: float) -> void:
	if not _running or not _enabled or _playback == null:
		return
	var beat_hz := _bpm / 60.0
	var frames_to_fill: int = _playback.get_frames_available()
	if frames_to_fill <= 0:
		return
	var beat_period := 1.0 / beat_hz
	for i in frames_to_fill:
		var t_sec := _phase + float(i) / MIX_RATE
		var sample := _sample_at(t_sec, beat_period)
		_playback.push_frame(Vector2(sample, sample))
	_phase += float(frames_to_fill) / MIX_RATE


func _sample_at(t_sec: float, beat_period: float) -> float:
	var beat_pos := fmod(t_sec, beat_period) / beat_period
	var kick := 0.0
	if beat_pos < 0.02:
		kick = sin(beat_pos / 0.02 * PI) * 0.35
	var snare := 0.0
	if absf(beat_pos - 0.5) < 0.015:
		snare = sin((beat_pos - 0.5) / 0.015 * PI) * 0.18
	var hihat := sin(t_sec * 8000.0) * 0.015 if int(t_sec / (beat_period * 0.25)) % 2 == 0 else 0.0
	var fever_boost := 0.08 if GameState.fever_active else 0.0
	return clampf(kick + snare + hihat + fever_boost, -1.0, 1.0)
