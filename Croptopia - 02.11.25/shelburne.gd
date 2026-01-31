extends Node2D

var player

var zea_house_happened

signal mt_crag_over

# Called when the node enters the scene tree for the first time.
func _ready():
#	var player_file = preload("res://scenes/player.tscn")
#	var player_instance = player_file.instantiate()
#	add_child(player_instance)
#	player = player_instance
#	player.position = $zea_house.position
#	disable_cameras(player.camera,2)
	
	var newspaper_file = preload("res://scenes/entities/newspaper.tscn")
	var newspaper_instance = newspaper_file.instantiate()
	add_child(newspaper_instance)
	newspaper_instance.position = $zea_house.position

#	newspaper_instance.process_mode = Node.PROCESS_MODE_DISABLED
	$TileMap.process_mode = Node.PROCESS_MODE_DISABLED
#	$structures.process_mode = Node.PROCESS_MODE_DISABLED
	$crops.process_mode = Node.PROCESS_MODE_DISABLED
	
	$top_of_mt_crag.connect("cutscene_over", Callable(self, "mt_crag_cutscene_over"))
	
#	$inside_zea_house.visible = false
#	$inside_zea_house/unknown_dialogue.visible = false

func _process(delta):
	if Input.is_action_just_pressed("enter"):
		var player_file = preload("res://scenes/player.tscn")
		var player_instance = player_file.instantiate()
		add_child(player_instance)
		player = player_instance
		player.position = $zea_house.position
		disable_cameras(player.camera,2)
func _on_enter_house_body_entered(body):
##	if zea_house_happened == "false":
#	inside_zea_cam.enabled = true
#	camera.enabled = false
#	unknown_dialogue.visible = true
#	unknown_dialogue.start()
#	man.visible = true
#	house_player.visible = true
#	player.position = Vector2(-8721,-381)
	if !zea_house_happened:
		pass
		player.position = Vector2(-8721,-381)

func disable_cameras(variant,num):
	if num == 1:
		variant.enabled = false
	if num == 2:
		variant.enabled = true

func mt_crag_cutscene_over():
	print("BABY")
	emit_signal("mt_crag_over")
