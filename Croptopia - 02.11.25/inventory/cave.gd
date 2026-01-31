extends Node2D

signal exited_cave

@onready var objects = $objects

# Called when the node enters the scene tree for the first time.
func _ready():
	entered_cave()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass


func _on_area_2d_body_entered(body):
	emit_signal("exited_cave")

func entered_cave():
	generate_objects()
	
func generate_objects():
	var ore_depot_file = preload("res://inventory/ore_depot.tscn")
	var ore_depot_instance = ore_depot_file.instantiate()
	ore_depot_instance.position = Vector2(10,10)
	objects.add_child(ore_depot_instance)
	
	var stalagmite_file = preload("res://stalagmite.tscn")
	var stalagmite_instance = stalagmite_file.instantiate()
	stalagmite_instance.position = Vector2(20,20)
	objects.add_child(ore_depot_instance)
	
	var flint_file = preload("res://flint.tscn")
	var flint_instance = flint_file.instantiate()
	flint_instance.position = Vector2(30,30)
	objects.add_child(flint_instance)
