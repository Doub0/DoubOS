extends Node2D

@onready var cutscene_cam = $cutscene_cam
var camera

var player

signal cutscene_finished

# Called when the node enters the scene tree for the first time.
func _ready():
	cutscene_cam.enabled = true
	player.camera.enabled = false
#	player..enabled = false
	$zea.visible = true
	$AnimatedSprite2D.visible = true
	$second_dialogue_zea.visible = true
	$second_dialogue_zea.start()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
	
func _on_second_dialogue_zea_dialogue_finished():
	print("test")
	player.camera.enabled = true
	cutscene_cam.enabled = false
	player.position = Vector2(-5100,-3031)
	emit_signal("cutscene_finished")

func _on_area_2d_body_entered(body):
	player.position = Vector2(-1000, -1000)
	camera.enabled = false
	cutscene_cam.enabled = true
	$second_dialogue_zea.visible = true
	$second_dialogue_zea.start()
