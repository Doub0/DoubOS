extends StaticBody2D

var player

var player_in_area = false

@onready var ui = $CanvasLayer

var is_open = false

@onready var stem_pos = $stem_pos.global_position.y

@export var building_name: String

var build_mode = false
var build_placeable

# Called when the node enters the scene tree for the first time.
func _ready():
	close()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if player_in_area == true:
		if Input.is_action_just_pressed("e"):
			if is_open:
				close()
			else:
				open()
		if (player.position.y - stem_pos) < 0:
#			print("ABOVE")
			z_index = 2
		if (player.position.y - stem_pos) > 0:
			z_index = 0
#			print("BELLOW")
	else:
		pass
	if build_mode:
		var mouse_tile = Tilemanager.tilemap.local_to_map(get_global_mouse_position())
		var local_pos = Tilemanager.tilemap.map_to_local(mouse_tile)
		var world_pos = Tilemanager.tilemap.to_global(local_pos)
		build_placeable.global_position = local_pos
		if Input.is_action_just_pressed("left click"):
			var temp_root = self.get_parent()
			temp_root.add_child(build_placeable)

func _on_player_detection_body_entered(body):
	player = body
	player_in_area = true

func open():
	is_open = true
	ui.show()
	
func close():
	is_open = false
	ui.hide()

func _on_player_detection_body_exited(body):
	player_in_area = false

		


func _on_build_button_pressed():
	pass # Replace with function body.


func _on_farmer_bed_pressed():
	building_name = "Farmer Bed"
	parse_preview(building_name)

func _on_6x6_house_pressed():
	building_name = "6x6 House"
	

func parse_preview(name: String):
	var tilemap_node
	tilemap_node = self.get_parent()
	tilemap_node = tilemap_node.get_node("placement_mechanic")
	print("placement mechanic:",tilemap_node)
	var building_placable = Sprite2D.new()
#	var building_placable_instance = building_placable.instantiate()
	
	
	var build_script = load("res://build_placable.gd")
	
	Tilemanager.tilemap = $build_grid
	
	build_mode = true
	
	build_placeable = building_placable
	
	if building_name == "6x6 House":
		#building_placable_instance.sprite
		pass
	elif building_name == "Farmer Bed":
		building_placable.region_enabled = true
		building_placable.texture = preload("res://assets/Item Assets/placeables/garden_bed_tier_1.png")
		building_placable.region_rect = Rect2(0,0,102,59)
		building_placable.scale = Vector2(3,5)
		tilemap_node.add_child(building_placable)
