extends StaticBody2D

var player
var player_in_area = false

var propaganda_inspect

var canvaslayer
var portrait_thumbnail

var articles = ["Lunar Propaganda", "New Hampshire President", "Anti Lunar Propaganda"]

var chosen_article

var pic_button

var is_reading = false
# Called when the node enters the scene tree for the first time.
func _ready():
	chosen_article = choose(articles)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if player_in_area:
		if Input.is_action_just_pressed("e"):
			if !has_node("@CanvasLayer@2"):
				read(chosen_article)
				open()
			if has_node("@CanvasLayer@2"):
				open()
					
		if Input.is_action_just_pressed("escape"):
	#		if has_node("@CanvasLayer@2"):
			close()

func open():
	canvaslayer.visible = true
func close():
	canvaslayer.visible = false
func _on_area_2d_body_entered(body):
	if body.has_method("player"):
		player = body
		player_in_area = true

func read(choice_article):
	var canvas = CanvasLayer.new()
	canvaslayer = canvas
	var paper = Panel.new()
	add_child(canvas)
	print(canvas.get_path())
	var format = preload("res://scenes/formats/paper_format.tres")
	var black_border = preload("res://scenes/formats/black_border.tres")
		
		
	var shadow = Panel.new()
	shadow.add_theme_stylebox_override("panel",black_border)
	shadow.modulate.a = 0.5
	shadow.size = get_viewport().size
#	shadow.scale = Vector2(1.25,1.25)
#	shadow.position = Vector2(150,0)
	canvas.add_child(shadow)
	
	canvas.add_child(paper)
	
	paper.add_theme_stylebox_override("panel",format)
	paper.position = Vector2(200,50)
	paper.size = Vector2(800,550)
	
	if choice_article == "Lunar Propaganda":
		var newspaper_name = Sprite2D.new()
		var black = Color(0,0,0)
		var logo = preload("res://assets/hampshire_times_logo.png")
		newspaper_name.texture = logo
		newspaper_name.scale = Vector2(5,5)
		newspaper_name.position = Vector2(400,75)
		
		var header = Label.new()
		header.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		header.text = str("The Revolution of Liberty!")
		header.position = newspaper_name.position + Vector2(-200,100)
	#	header.scale = Vector2(1.5,1.5)
		header.add_theme_color_override("font_color",black)
		
		var pixel_font = preload("res://fonts/yoster.ttf")
		header.add_theme_font_override("font",pixel_font)
		var beginning = Label.new()
		beginning.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		beginning.text = str("After years of harsh oppression by the Federals, the true representatives \n of New Hampshire  are starting to take shape! Formed December 27th of 2024, \n these men have captured  strategic roads leading into the city of Shelburne; \n This practictly means the city is encircled and may be under siege if resistance \n erupts, however the native population seems to welcome them as liberators, and \n along with the wise Warden Mark Gray wise statement- \n 'We yearn for the people - We yearn for freedom' \n helps bring forward the groups intent.")
		beginning.position = newspaper_name.position + Vector2(-350,150)
		beginning.add_theme_font_override("font",pixel_font)
		beginning.add_theme_color_override("font_color",black)
		
		var mid_section = Label.new()
		mid_section.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		mid_section.text = str("Gray's stance prioritizes domestic produce, \n rather than the import based \n stance of the Federal Government. \n Pictured are a unit of \n the 'Lunar Guardsmen' with their \n leaders 'Mark Gray' and two undisclosed subordinates.")
		mid_section.position = newspaper_name.position + Vector2(-350,350)
		mid_section.add_theme_font_override("font",pixel_font)
		mid_section.add_theme_color_override("font_color",black)
	#	beginning.scale = Vector2(1.5,1.5)
		var portrait_file = preload("res://lunar_propaganda_1.png")
		var portrait = Sprite2D.new()
		portrait.name = "propaganda_thumb"
		portrait.texture = portrait_file
		portrait.position = newspaper_name.position + Vector2(245,358)
		portrait_thumbnail = portrait
		
		var inspect_button = Button.new()
		inspect_button.connect("pressed", Callable(self, "inspect_portrait"))
		inspect_button.size = Vector2(300,175)
		inspect_button.position = newspaper_name.position + Vector2(100,275)
		print(newspaper_name.position + Vector2(100,275))
		inspect_button.flat = true
		
		pic_button = inspect_button
		
		var border = Panel.new()
		
		border.size = Vector2(300,175)
		border.position = newspaper_name.position + Vector2(95,270)
		border.add_theme_stylebox_override("panel",black_border)
		
		portrait.scale = Vector2(1.5,1.5)
			
		paper.add_child(newspaper_name)
		paper.add_child(header)
		paper.add_child(beginning)
		paper.add_child(mid_section)
		paper.add_child(border)
		paper.add_child(portrait)
		paper.add_child(inspect_button)
	elif choice_article == "New Hampshire President":
		var newspaper_name = Sprite2D.new()
		var black = Color(0,0,0)
		var logo = preload("res://assets/hampshire_times_logo.png")
		newspaper_name.texture = logo
		newspaper_name.scale = Vector2(5,5)
		newspaper_name.position = Vector2(400,75)
		
		var header = Label.new()
		header.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		header.text = str("The President calls on the people!")
		header.position = newspaper_name.position + Vector2(-200,100)
	#	header.scale = Vector2(1.5,1.5)
		header.add_theme_color_override("font_color",black)
		
		var pixel_font = preload("res://fonts/yoster.ttf")
		header.add_theme_font_override("font",pixel_font)
		var beginning = Label.new()
		beginning.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		beginning.text = str("President of the Provisional Republic of New Hampshire William Lasher \n requested that due to low manpower reserves, he needs the help of \n the local people. It is unsure if he will enforce a \n manditory conscription, but the people will choose the path of \n American freedom")
		beginning.position = newspaper_name.position + Vector2(-350,150)
		beginning.add_theme_font_override("font",pixel_font)
		beginning.add_theme_color_override("font_color",black)
		
		var mid_section = Label.new()
		mid_section.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		mid_section.text = str("Lasher receives support from \n the Federal Government of \n the United States, and their \n troops fight alongside eachother. \n The only chance of a reunited \n America is in your hands \n as a citizen.")
		mid_section.position = newspaper_name.position + Vector2(-350,350)
		mid_section.add_theme_font_override("font",pixel_font)
		mid_section.add_theme_color_override("font_color",black)
	#	beginning.scale = Vector2(1.5,1.5)
		var portrait_file = preload("res://assets/american_propaganda_1.png")
		var portrait = Sprite2D.new()
		portrait.region_enabled = true
		portrait.region_rect = Rect2(0,0,192,108)
		portrait.name = "propaganda_thumb"
		portrait.texture = portrait_file
		portrait.position = newspaper_name.position + Vector2(245,358)
		portrait_thumbnail = portrait
		
		var inspect_button = Button.new()
		inspect_button.connect("pressed", Callable(self, "inspect_portrait"))
		inspect_button.size = Vector2(300,175)
		inspect_button.position = newspaper_name.position + Vector2(100,275)
		inspect_button.flat = true
		
		pic_button = inspect_button
		
		var border = Panel.new()
		
		border.size = Vector2(300,175)
		border.position = newspaper_name.position + Vector2(95,270)
		border.add_theme_stylebox_override("panel",black_border)
		
		portrait.scale = Vector2(1.5,1.5)
			
		paper.add_child(newspaper_name)
		paper.add_child(header)
		paper.add_child(beginning)
		paper.add_child(mid_section)
		paper.add_child(border)
		paper.add_child(portrait)
		paper.add_child(inspect_button)
		
	elif choice_article == "Anti Lunar Propaganda":
		var anti_lunar_file = preload("res://assets/american_propaganda_1.png")
		var anti_lunar = Sprite2D.new()
		anti_lunar.texture = anti_lunar_file
		anti_lunar.region_enabled = true
		anti_lunar.region_rect = Rect2(192,0,192,108)
		anti_lunar.scale = Vector2(3,3)
		anti_lunar.position = Vector2(350,200)
		
		paper.add_child(anti_lunar)
func inspect_portrait():
	if portrait_thumbnail.has_node("propaganda"):
		propaganda_inspect.queue_free()
		pic_button.scale = Vector2(1,1)
		pic_button.position = Vector2(500, 350)
		
	if !portrait_thumbnail.has_node("propaganda"):
		var portrait = Sprite2D.new()
		if chosen_article == "Lunar Propaganda":
			var portrait_file = preload("res://lunar_propaganda_1.png")
			portrait.region_enabled = false
			portrait.texture = portrait_file
		elif chosen_article == "New Hampshire President":
			var portrait_file = preload("res://assets/american_propaganda_1.png")
			portrait.region_enabled = true
			portrait.region_rect = Rect2(0,0,192,108)
			portrait.texture = portrait_file
		elif chosen_article == "Anti Lunar Propaganda":
			var portrait_file = preload("res://assets/american_propaganda_1.png")
			portrait.region_enabled = true
			portrait.region_rect = Rect2(192,0,192,108)
			portrait.texture = portrait_file
		portrait.scale = Vector2(3,3)
		
		pic_button.scale = Vector2(3,3)
		pic_button.position = portrait.position
		portrait.position = Vector2(-150,-100)
		portrait.name = "propaganda"
		propaganda_inspect = portrait
		
		portrait_thumbnail.add_child(portrait)
	
func choose(array):
	array.shuffle()
	return array.front()


func _on_area_2d_body_exited(body):
	if body.has_method("player"):
		player_in_area = false
