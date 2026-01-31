extends Sprite2D

var i_type

func _ready():
	pass
func _process(delta):
	var mouse_tile = Tilemanager.tilemap.local_to_map(get_global_mouse_position())
	var local_pos = Tilemanager.tilemap.map_to_local(mouse_tile)
	var world_pos = Tilemanager.tilemap.to_global(local_pos)
	global_position = local_pos
	
#	print("HAIIIII")
#	print("Type",i_type) U can activate later
func variant(type:String):
	print("Type",i_type)
	i_type = type
	region_enabled = true
	if type == "Redbaneberry":
		region_rect = Rect2(0,0,32,32)
		texture = preload("res://pixil-frame-0 - 2024-01-16T110111.777.png")
	elif type == "Chive":
		region_rect = Rect2(32,0,32,32)
		texture = preload("res://pixilart-sprite (10).png")
	if type == "Construction Table":
		region_enabled = false
		texture = preload("res://assets/Item Assets/placeables/construction_table.png")
	elif type == "Farm Bed":
		region_enabled = true
		region_rect = Rect2(0,0,109,59)
		texture = preload("res://assets/Item Assets/placeables/garden_bed_tier_1.png")
		
#func _on_area_2d_body_entered(body):
#	$area2D/CollisionShape2D.modulate[]
	

func _on_area_2d_area_entered(area):
	$ColorRect.self_modulate = Color(255,0,0)


func _on_area_2d_area_exited(area):
	$ColorRect.self_modulate = Color(0,255,0)
