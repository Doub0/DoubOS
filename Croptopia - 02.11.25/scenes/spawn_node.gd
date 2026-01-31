extends Node2D

signal scene_triggered

var mysterious_cutscene

var player

var x_coords
var y_coords

var x_coords_candidate
var y_coords_candidate

# Called when the node enters the scene tree for the first time.
func _ready():
#	generate_flaura()
	var mysterious_file = preload("res://world_2.tscn")
	var mysterious_instance = mysterious_file.instantiate()
	mysterious_cutscene = mysterious_instance
	mysterious_cutscene.position = $spawn/cutscene_pos.position
	add_child(mysterious_instance)
	mysterious_cutscene.connect("cutscene_over", Callable(self, "cutscene_over"))
	mysterious_cutscene.connect("cutscene_start", Callable(self, "cutscene"))


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass


func _on_player_detection_body_entered(body):
	if body.has_method("player"):
		emit_signal("scene_triggered")

func cutscene():
	pass
func cutscene_over():
	remove_child(mysterious_cutscene)

func generate_flaura():
	var gen_amount = randi_range(0,1000)
	for i in gen_amount:
		Tilemanager.tilemap = $spawn/TileMap2
		
		var shrub_file = preload("res://scenes/shrubs.tscn")
		var shrub_instance = shrub_file.instantiate()
		
		x_coords_candidate = randf_range(-10,900)
		y_coords_candidate = randf_range(400,-900)
		
		x_coords = choose([x_coords_candidate,x_coords_candidate,x_coords_candidate])
		y_coords = pick([y_coords_candidate,y_coords_candidate,y_coords_candidate])
		
		
		var random_vector = Vector2(x_coords,y_coords)
		
		var random_tile = Tilemanager.tilemap.local_to_map(random_vector)
		var local_pos = Tilemanager.tilemap.map_to_local(random_tile)
		var world_pos = Tilemanager.tilemap.to_global(local_pos)
		
		shrub_instance.position = world_pos
		$spawn/objects.add_child(shrub_instance)
	
	
func choose(x_coords):
	x_coords.shuffle()
	return x_coords.front()
func pick(y_coords):
	y_coords.shuffle()
	return y_coords.front()
