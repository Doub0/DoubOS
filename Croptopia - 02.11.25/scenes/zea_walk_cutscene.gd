extends Node2D

var player
var quest_is_finished = false
var is_pathfollowing = false
var is_pathfollowing2 = false
var cutscene_is_over = false

@onready var questTrans = $quest_transition
@onready var quest_camera = $first_cutscene_follow2/PathFollow2D/questcam
@onready var quest_camera2 = $second_cutscene_follow2/PathFollow2D/questcam

signal cutscene_over
# Called when the node enters the scene tree for the first time.
func _ready():
	cutscene_start()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	var pathfollower = $first_cutscene_follow2/PathFollow2D
	var pathfollower2 = $second_cutscene_follow2/PathFollow2D
	pathfollower.visible = false
	pathfollower2.visible = false
	if is_pathfollowing:
		print("POWER")
#			emit_signal("start_music")
#			background_music.stop()
#			zea_backgroundsong.play()
		pathfollower2.visible = false
		pathfollower.visible = true
		quest_camera.enabled = true
		quest_camera2.enabled = false
		$first_cutscene_follow2/PathFollow2D/AnimatedSprite2D.play("walk_left")
		$first_cutscene_follow2/PathFollow2D/AnimatedSprite2D2.play("walk_w")
		#
		#$Node2D/world2/world2openingcutscene/Path2D/PathFollow2D/Camera2D.enabled = false
		pathfollower.progress_ratio += 0.007
		if pathfollower.progress_ratio >= 1:
			questTrans.play("quest_fade")
			print("PLEP")
			is_pathfollowing = false
			is_pathfollowing2 = true
	if is_pathfollowing2:
		$quest_transition/ColorRect.position = quest_camera2.global_position - Vector2(200,150)
		print("SEP")
		pathfollower.visible = false
		pathfollower2.visible = true
		quest_camera.enabled = false
		quest_camera2.enabled = true
		$second_cutscene_follow2/PathFollow2D/AnimatedSprite2D.play("walk_left")
		$second_cutscene_follow2/PathFollow2D/AnimatedSprite2D2.play("walk_w")
		pathfollower2.progress_ratio += 0.001
		if pathfollower2.progress_ratio >= 1:
			print("SAC")
			quest_camera.enabled = false
			quest_camera2.enabled = false
			is_pathfollowing = false
			is_pathfollowing2 = false
			emit_signal("cutscene_over")

func cutscene_start():
	questTrans.play("quest_fade")
	is_pathfollowing = true
	
	
