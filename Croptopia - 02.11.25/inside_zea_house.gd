extends Node2D

signal already_happened

var player
var player_in_area

@onready var transition = $cutscene/Transition
signal left_her_house
signal memory_of_zea

@onready var inside_zea_cam = $base/Camera2D
@onready var unknown_dialogue = $cutscene/unknown_dialogue
@onready var man = $cutscene/man
@onready var house_player = $cutscene/cutscene_player
#ne tree for the first time.

func cutscene():
	inside_zea_cam.enabled = true
	player.camera.enabled = false
	unknown_dialogue.visible = true
	unknown_dialogue.start()
	man.visible = true
	house_player.visible = true
func _on_unknown_dialogue_dialogue_finished():
	transition.play("fade_out")
	$cutscene/unknown_dialogue.visible = false
	$cutscene/man.visible = false
	house_player.visible = false
	GlobalCache.null_it_out()
func _on_area_2d_body_entered(body):
	if body.has_method("player"):
		emit_signal("left_her_house")


func _on_enter_house_body_entered(body):
	pass # Replace with function body.

func exit():
	pass
#	inside_zea_cam.enabled = false
#	camera.enabled = true
#	unknown_dialogue.visible = false
#	man.visible = false
#	player.position = Vector2(-5069,-2873)
#	zea_house_happened = "true"
func _process(delta):
#	print(get_viewport().get_camera_2d().get_parent())
	pass
