extends Node2D

var player


func _on_area_2d_2_body_entered(body):
	get_tree().change_scene_to_file("res://top_of_mt_crag.tscn")
