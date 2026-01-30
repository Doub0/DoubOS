extends Control

@onready var sunset = $sunset_rect/sunset_cycle
@onready var sunrise = $sunrise_rect/sunrise_cycle
@onready var sunset_rect = $sunset_rect
@onready var sunrise_rect = $sunrise_rect

@onready var night_rect = $night_rect
@onready var night = $night_rect/night_cycle
@onready var day = $day_rect/day_cycle
@onready var day_rect = $day_rect

#Day counter code
@onready var day_counter = $CanvasLayer/Panel/Sprite2D/count
@onready var day_label = $CanvasLayer/Panel/Sprite2D/day
var day_count
var day_name
#
var addition = 1

var sunset_time
var sunrise_time

var night_time
var day_time

var phase

var time

var hour
var minutes

var hour_sif1
var hour_sif2

var minute_sif1
var minute_sif2

var week
var weekday_number = 0

var month_array
var month
var month_number = 0

var year = 2027
@onready var year_label = $CanvasLayer/Panel/Sprite2D/year

@onready var month_label = $CanvasLayer/Panel/Sprite2D/month

@onready var clock = $clock
@onready var time_counter = $CanvasLayer/Panel/Sprite2D/clock_time

#OBJECT VARIABLES


# Called when the node enters the scene tree for the first time.
func _ready():
	hour_sif1 = 2
	hour_sif2 = 1
	
	minute_sif1 = 0
	minute_sif2 = 0
	
	hour = str([hour_sif1, hour_sif2])
	minutes = str(minute_sif1, minute_sif2)
	
	
	time = str("")
	day_count = 1
	phase = "day"
	day_time = true
	
	week = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	month_array = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
	month = month_array[month_number]
#	day_counter.text = str(day_name)
	day_name = week[weekday_number]
	day_label.text = str(day_name)
	month_label.text = str(month)
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	day_counter.text = str(day_count)
	if phase == "sunset":
		sunrise_time = false
		sunset_time = true
		night_time = false
		day_time = false
		sunrise_rect.visible = false
		sunset_rect.visible = true
		night_rect.visible = false
		day_rect.visible = false
		sunset.play("day_night_cycle")
		
	if phase == "sunrise":
		sunrise_time = true
		sunset_time = false
		night_time = false
		day_time = false
		sunset_rect.visible = false
		sunrise_rect.visible = true
		night_rect.visible = false
		day_rect.visible = false
		sunrise.play("day_night_cycle_reverse")
		
	if phase == "night":
		sunrise_time = false
		sunset_time = false
		night_time = true
		day_time = false
		sunset_rect.visible = false
		sunrise_rect.visible = false
		night_rect.visible = true
		day_rect.visible = false
		night.play("night_cycle")
		
	if phase == "day":
		sunrise_time = false
		sunset_time = false
		night_time = false
		day_time = true
		sunset_rect.visible = false
		sunrise_rect.visible = false
		night_rect.visible = false
		day_rect.visible = true
		day.play("day_cycle")
		#the day count \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
		#\\\\\\\\\\\\\\\\\\\\\\\
		#SCRIPT FOR OBJECTS

func _on_sunset_cycle_animation_finished(anim_name):
	phase = "night"


func _on_sunrise_cycle_animation_finished(anim_name):
	phase = "day"
#	day_counter.text = str(day_count + 1)
#	day_count = day_count + 1
#	weekday_number = weekday_number + 1


func _on_night_cycle_animation_finished(anim_name):
	phase = "sunrise"


func _on_day_cycle_animation_finished(anim_name):
	phase = "sunset"

func time_concept():
	hour = str(hour_sif2, hour_sif1)
	
	
	time = str(hour,":" ,minutes)
	time_counter.text = str(time)
	
	day_label.text = str(day_name)
	
	month = month_array[month_number]
	
	month_label.text = str(month)
	
	year_label.text = str("Year 
	\n", year)
	
	if hour_sif1 == 9 and minute_sif2 == 5 and minute_sif1 == 9:
		hour_sif1 = 0
		hour_sif2 += 1
		
		minute_sif1 = 0
		minute_sif2 = 0
		
		
	if minute_sif1 == 10:
		minute_sif1 = 0
		minute_sif2 += 1
		minutes = str(minute_sif2,minute_sif1)
		
	if minute_sif2 == 6:
		minute_sif1 = 0
		minute_sif2 = 0
		hour_sif1 += 1
		
	if minute_sif1 == 5:
		minutes = str(minute_sif2,minute_sif1)
		
	
		
	if weekday_number == 6:
		weekday_number = -1
		
	elif hour_sif2 == 2 and hour_sif1 == 4:
		day_count = day_count + 1
		
		hour_sif1 = 0
		hour_sif2 = 0
	
		minute_sif1 = 0
		minute_sif2 = 0
#		day_count = day_count + 1
		day_counter.text = str(day_count)
		
		weekday_number = weekday_number + 1
		day_name = week[weekday_number]
	if month == "JAN" and day_count == 32:
		month_number += 1
		day_count = 1
	elif month == "FEB" and day_count == 29:
		month_number += 1
		day_count = 1
	elif month == "MAR" and day_count == 32:
		month_number += 1
		day_count = 1
	elif month == "APR" and day_count == 31:
		month_number += 1
		day_count = 1
	elif month == "MAY" and day_count == 32:
		month_number += 1
		day_count = 1
	elif month == "JUN" and day_count == 31:
		month_number += 1
		day_count = 1
	elif month == "JUL" and day_count == 32:
		month_number += 1
		day_count = 1
	elif month == "AUG" and day_count == 32:
		month_number += 1
		day_count = 1
	elif month == "SEP" and day_count == 31:
		month_number += 1
		day_count = 1
	elif month == "OCT" and day_count == 32:
		month_number += 1
		day_count = 1
	elif month == "NOV" and day_count == 31:
		month_number += 1
		day_count = 1
	elif month == "DEC" and day_count == 32:
		month_number = 0
		day_count = 1
		year += 1
		
#	if month_number == 11 and minute_sif2 == 5 and minute_sif1 == 9:
#		month_number = -1
#		year += 1

func _on_clock_timeout():
	minute_sif1 += 1
	
	print(minute_sif1)
	
	time_concept()
