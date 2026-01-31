extends Control

var day_n_night_cycle = preload("res://day_and_night.tscn")
var day_and_night_cycle

var money_count

@onready var money_counter = $money_count/Panel/Sprite2D/count

# Called when the node enters the scene tree for the first time.
func _ready():
	var day_night_cycle_instance
	day_night_cycle_instance = day_n_night_cycle.instantiate()
	$day_and_night.add_child(day_night_cycle_instance)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
	
func invalid_purchase():
	money_counter.text = str("INVALID")
	await get_tree().create_timer(0.5).timeout
	money_counter.text = str(money_count)

