extends Node2D

var player_in_area = false
var player

var is_inside = false

var interiour
# Called when the node enters the scene tree for the first time.
func _ready():
	pass


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if player_in_area:
			if Input.is_action_just_pressed("e"):
				if !is_inside:
					spawn_house()
				else:
					leave_house()

	
func _on_area_2d_body_entered(body):
	if body.has_method("player"):
		print("PLAYER IN AREA")
		player_in_area = true
		player = body
	


func _on_area_2d_body_exited(body):
	if body.has_method("player"):
		player_in_area = false

func spawn_house():
	print("SPAWN!!")
	if !has_node("inside_zea_house"):
		var zea_inside_file = preload("res://inside_zea_house.tscn")
		var zea_inside_instance = zea_inside_file.instantiate()
		add_child(zea_inside_instance)
		interiour = zea_inside_instance
		interiour.position = interiour.position - Vector2(500,300)
		interiour.scale = Vector2(2,2)
		interiour.player = player
		player.player_can_move(false,false)
		interiour.cutscene()
		interiour.process_mode = PROCESS_MODE_ALWAYS
	if has_node("inside_zea_house"):
		player.player_can_move(false,false)
		interiour.visible = true
		interiour.process_mode = PROCESS_MODE_ALWAYS
	is_inside = true
func leave_house():
	interiour.visible = false
	interiour.process_mode = PROCESS_MODE_DISABLED
	player.player_can_move(true,true)
	
	is_inside = false
