# Addon Info
bl_info = {
	"name": "Real Camera",
	"description": "Physical camera controls",
	"author": "Wolf",
	"version": (3, 1),
	"blender": (2, 80, 0),
	"location": "Camera Properties",
	"wiki_url": "https://3d-wolf.com/products/camera.html",
	"tracker_url": "https://3d-wolf.com/products/camera.html",
	"support": "COMMUNITY",
	"category": "Render"
	}


# Libraries
import bpy
import bgl
import math
import os
from bpy.props import *
from bpy.types import PropertyGroup, Panel, Operator
from mathutils import Vector
from bpy.app.handlers import persistent
from . import addon_updater_ops


# Real Camera panel
class REALCAMERA_PT_Panel(Panel):
	bl_category = "Real Camera"
	bl_label = "Real Camera"
	bl_space_type = 'PROPERTIES'
	bl_region_type = "WINDOW"
	bl_context = "data"

	@classmethod
	def poll(cls, context):
		return context.camera

	def draw_header(self, context):
		settings = context.scene.camera_settings
		layout = self.layout
		layout.prop(settings, 'enabled', text='')

	def draw(self, context):
		settings = context.scene.camera_settings
		cam = context.camera
		layout = self.layout
		layout.enabled = settings.enabled
		# Updater
		addon_updater_ops.check_for_update_background()

		# Exposure triangle
		layout.use_property_split = True
		layout.use_property_decorate = False
		flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=True)
		col = flow.column()
		sub = col.column(align=True)
		sub.prop(cam.dof, "aperture_fstop", text="Aperture")
		sub.prop(settings, 'shutter_speed')

		# Mechanics
		col = flow.column()
		col.prop(settings, 'af')
		if settings.af:
			row = col.row(align=True)
			row.prop(settings, 'af_step', text="Bake")
			row.prop(settings, 'af_bake', text="", icon='PLAY')
		col = flow.column()
		sub = col.column(align=True)
		if not settings.af:
			sub.prop(cam.dof, "focus_distance", text="Focus Point")
		sub.prop(cam, 'lens', text="Focal Length")

		# Updater
		addon_updater_ops.update_notice_box_ui(self, context)


# Auto Exposure panel
class AUTOEXP_PT_Panel(Panel):
	bl_space_type = "PROPERTIES"
	bl_context = "render"
	bl_region_type = "WINDOW"
	bl_category = "Real Camera"
	bl_label = "Auto Exposure"
	COMPAT_ENGINES = {'BLENDER_EEVEE', 'CYCLES'}

	@classmethod
	def poll(cls, context):
		return (context.engine in cls.COMPAT_ENGINES)

	def draw_header(self, context):
		settings = context.scene.camera_settings
		layout = self.layout
		layout.prop(settings, 'enable_ae', text='')

	def draw(self, context):
		settings = context.scene.camera_settings
		layout = self.layout
		layout.enabled = settings.enable_ae
		# Updater
		addon_updater_ops.check_for_update_background()

		# Modes
		col = layout.column(align=True)
		row = col.row(align=True)
		row.alignment = "CENTER"
		row.label(text="Metering Mode")
		row = col.row(align=True)
		row.scale_x = 1.5
		row.scale_y = 1.5
		row.alignment = "CENTER"
		row.prop(settings, 'ae_mode', text="", expand=True)
		col.label(text="")

		# Settings
		layout.use_property_split = True
		layout.use_property_decorate = False
		flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=True)
		col = flow.column()
		col.prop(settings, 'ec', slider=True)
		if settings.ae_mode=="Center Weighted":
			col.prop(settings, 'center_grid')
		if settings.ae_mode=="Full Window":
			col.prop(settings, 'full_grid')

		# Updater
		addon_updater_ops.update_notice_box_ui(self, context)


# Enable camera
def toggle_update(self, context):
	settings = context.scene.camera_settings
	if settings.enabled:
		name = context.active_object.name
		# set limits
		bpy.data.cameras[name].show_limits = True
		# enable DOF
		context.object.data.dof.use_dof = True
		# set camera size
		bpy.context.object.data.display_size = 0.2
		# initial values Issue
		update_aperture(self, context)
		update_shutter_speed(self, context)
	else:
		# disable DOF
		context.object.data.dof.use_dof = False
		# reset limits
		name = context.active_object.name
		bpy.data.cameras[name].show_limits = False
		# reset autofocus
		bpy.context.scene.camera_settings.af = False


# Update Aperture
def update_aperture(self, context):
	context.object.data.cycles.aperture_fstop = context.scene.camera_settings.aperture
# Update Shutter Speed
def update_shutter_speed(self, context):
	fps = context.scene.render.fps
	shutter = context.scene.camera_settings.shutter_speed
	motion = fps*shutter
	context.scene.render.motion_blur_shutter = motion


# Update Autofocus
def update_af(self, context):
	af = context.scene.camera_settings.af
	if af:
		name = context.active_object.name
		obj = bpy.data.objects[name]
		# ray Cast
		ray = context.scene.ray_cast(context.scene.view_layers[0], obj.location, obj.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0)))
		distance = (ray[1]-obj.location).magnitude
		bpy.context.object.data.dof.focus_distance = distance
	else:
		# reset baked af
		context.scene.camera_settings.af_bake = False
		update_af_bake(self, context)


# Autofocus Bake
def update_af_bake(self, context):
	scene = bpy.context.scene
	bake = scene.camera_settings.af_bake
	start = scene.frame_start
	end = scene.frame_end
	frames = end-start+1
	steps = scene.camera_settings.af_step
	n = int(float(frames/steps))
	current_frame = scene.frame_current
	name = context.active_object.name
	cam = bpy.data.cameras[name]
	if bake:
		scene.frame_current = start
		# every step frames, place a keyframe
		for i in range(n+1):
			update_af(self, context)
			cam.dof.keyframe_insert('focus_distance')
			scene.frame_set(scene.frame_current+steps)
		# current Frame
		scene.frame_current = current_frame
	else:
		# delete dof keyframes
		try:
			fcurves = cam.animation_data.action.fcurves
		except AttributeError:
			a=0
		else:
			for c in fcurves:
				if c.data_path.startswith("dof.focus_distance"):
					fcurves.remove(c)


# Read filmic values from files
def read_filmic_values(path):
	nums = []
	with open(path) as filmic_file:
		for line in filmic_file:
			nums.append(float(line))
	return nums


# Global values
handle = ()
path = os.path.join(os.path.dirname(__file__), "looks/")
filmic_vhc = read_filmic_values(path + "Very High Contrast")
filmic_hc = read_filmic_values(path + "High Contrast")
filmic_mhc = read_filmic_values(path + "Medium High Contrast")
filmic_bc = read_filmic_values(path + "Medium Contrast")
filmic_mlc = read_filmic_values(path + "Medium Low Contrast")
filmic_lc = read_filmic_values(path + "Low Contrast")
filmic_vlc = read_filmic_values(path + "Very Low Contrast")
old_engine = ""


# Enable Auto Exposure
def update_ae(self, context):
	ae = context.scene.camera_settings.enable_ae
	if ae:
		engine = context.scene.render.engine
		global handle
		if engine=="BLENDER_EEVEE":
			handle = bpy.types.SpaceView3D.draw_handler_add(ae_calc, (), 'WINDOW', 'PRE_VIEW')
		if engine=="CYCLES":
			handle = bpy.types.SpaceView3D.draw_handler_add(ae_calc, (), 'WINDOW', 'POST_PIXEL')
	else:
		bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
	global old_engine
	old_engine = bpy.context.scene.render.engine


# Auto Exposure algorithms
def ae_calc():
	shading = bpy.context.area.spaces.active.shading.type
	if shading=="RENDERED":
		settings = bpy.context.scene.camera_settings
		# width and height of the viewport
		viewport = bgl.Buffer(bgl.GL_INT, 4)
		bgl.glGetIntegerv(bgl.GL_VIEWPORT, viewport)
		width = viewport[2]
		height = viewport[3]
		bgl.glDisable(bgl.GL_DEPTH_TEST)
		buf = bgl.Buffer(bgl.GL_FLOAT, 3)

		# Center Spot
		if settings.ae_mode=="Center Spot":
			x = width//2
			y = height//2
			bgl.glReadPixels(x, y, 1, 1, bgl.GL_RGB, bgl.GL_FLOAT, buf)
			avg = luminance(buf)

		# Full Window
		if settings.ae_mode=="Full Window":
			grid = settings.full_grid
			values = 0
			step = 1/(grid+1)
			for i in range (grid):
				for j in range (grid):
					x = int(step*(j+1)*width)
					y = int(step*(i+1)*height)
					bgl.glReadPixels(x, y, 1, 1, bgl.GL_RGB, bgl.GL_FLOAT, buf)
					lum = luminance(buf)
					values = values+lum
			avg = values/(grid*grid)

		# Center Weighted
		if settings.ae_mode=="Center Weighted":
			circles = settings.center_grid
			if width>=height:
				max = width
			else:
				max = height
			half = max//2
			step = max//(circles*2+2)
			values = 0
			weights = 0
			for i in range (circles):
				x = half-(i+1)*step
				y = x
				n_steps = i*2+2
				weight = (circles-1-i)/circles
				for n in range (n_steps):
					x = x+step
					bgl.glReadPixels(x, y, 1, 1, bgl.GL_RGB, bgl.GL_FLOAT, buf)
					lum = luminance(buf)
					values = values+lum*weight
					weights = weights+weight
				for n in range (n_steps):
					y = y+step
					bgl.glReadPixels(x, y, 1, 1, bgl.GL_RGB, bgl.GL_FLOAT, buf)
					lum = luminance(buf)
					values = values+lum*weight
					weights = weights+weight
				for n in range (n_steps):
					x = x-step
					bgl.glReadPixels(x, y, 1, 1, bgl.GL_RGB, bgl.GL_FLOAT, buf)
					lum = luminance(buf)
					values = values+lum*weight
					weights = weights+weight
				for n in range (n_steps):
					y = y-step
					bgl.glReadPixels(x, y, 1, 1, bgl.GL_RGB, bgl.GL_FLOAT, buf)
					lum = luminance(buf)
					values = values+lum*weight
					weights = weights+weight

			avg = values/weights

		ec = bpy.context.scene.camera_settings.ec
		if ec!=0:
			middle = 0.18*math.pow(2, ec)
			log = (math.log2(middle/0.18)+10)/16.5
			s = s_calc(log)
			avg_min = s-0.01
			avg_max = s+0.01
		else:
			avg_min = 0.49
			avg_max = 0.51
			middle = 0.18
		if not (avg>avg_min and avg<avg_max):
			# Measure scene referred value and change the exposure value
			s_curve = s_calculation(avg)
			log = math.pow(2, (16.5*s_curve-12.47393))
			past = bpy.context.scene.view_settings.exposure
			scene = log/(math.pow(2, past))
			future = -math.log2(scene/middle)
			exposure = past-((past-future)/5)
			bpy.context.scene.view_settings.exposure = exposure


# Calculate value after filmic log
def s_calc(log):
	look = bpy.context.scene.view_settings.look
	if look=="None":
		filmic = filmic_bc
	elif look=="Filmic - Very High Contrast":
		filmic = filmic_vhc
	elif look=="Filmic - High Contrast":
		filmic = filmic_hc
	elif look=="Filmic - Medium High Contrast":
		filmic = filmic_mhc
	elif look=="Filmic - Medium Contrast":
		filmic = filmic_bc
	elif look=="Filmic - Medium Low Contrast":
		filmic = filmic_mlc
	elif look=="Filmic - Low Contrast":
		filmic = filmic_lc
	elif look=="Filmic - Very Low Contrast":
		filmic = filmic_vlc
	x = int(log*4096)
	return filmic[x]


# Calculate value after filmic log inverse
def s_calculation(n):
	look = bpy.context.scene.view_settings.look
	if look=="None":
		filmic = filmic_bc
	elif look=="Filmic - Very High Contrast":
		filmic = filmic_vhc
	elif look=="Filmic - High Contrast":
		filmic = filmic_hc
	elif look=="Filmic - Medium High Contrast":
		filmic = filmic_mhc
	elif look=="Filmic - Medium Contrast":
		filmic = filmic_bc
	elif look=="Filmic - Medium Low Contrast":
		filmic = filmic_mlc
	elif look=="Filmic - Low Contrast":
		filmic = filmic_lc
	elif look=="Filmic - Very Low Contrast":
		filmic = filmic_vlc
	begin = 0
	end = len(filmic)
	middle = begin
	# find value in middle (binary search)
	while (end-begin) > 1:
		middle = math.ceil((end+begin)/2)
		if filmic[middle] > n:
			end = middle
		else:
			begin = middle
	return (middle + 1) / len(filmic)


# RGB to Luminance
def luminance(buf):
	lum = 0.2126*buf[0] + 0.7152*buf[1] + 0.0722*buf[2]
	return lum


class CameraSettings(PropertyGroup):
	# Enable
	enabled : bpy.props.BoolProperty(
		name = "Enable Real Camera",
		description = "Enable Real Camera",
		default = False,
		update = toggle_update
		)

	# Exposure Triangle
	aperture : bpy.props.FloatProperty(
		name = "Aperture",
		description = "Aperture of the lens in f-stops. From 0.1 to 64. Gives a depth of field effect",
		min = 0.1,
		max = 64,
		step = 1,
		precision = 2,
		default = 5.6,
		update = update_aperture
		)

	shutter_speed : bpy.props.FloatProperty(
		name = "Shutter Speed",
		description = "Exposure time of the sensor in seconds. From 1/10000 to 10. Gives a motion blur effect",
		min = 0.0001,
		max = 100,
		step = 10,
		precision = 4,
		default = 0.5,
		update = update_shutter_speed
		)

	# Mechanics
	af : bpy.props.BoolProperty(
		name = "Autofocus",
		description = "Enable Autofocus",
		default = False,
		update = update_af
		)

	af_bake : bpy.props.BoolProperty(
		name = "Autofocus Baking",
		description = "Bake Autofocus for the entire animation",
		default = False,
		update = update_af_bake
		)

	af_step : bpy.props.IntProperty(
		name = "Step",
		description = "Every step frames insert a keyframe",
		min = 1,
		max = 10000,
		default = 24
		)

	# Auto Exposure
	enable_ae : bpy.props.BoolProperty(
		name = "Auto Exposure",
		description = "Enable Auto Exposure",
		default = False,
		update = update_ae
		)

	ae_mode : bpy.props.EnumProperty(
		name="Mode",
		items= [
			("Center Spot", "Center Spot", "Sample the pixel in the center of the window", 'PIVOT_BOUNDBOX', 0),
			("Center Weighted", "Center Weighted", "Sample a grid of pixels and gives more weight to the ones near the center", 'CLIPUV_HLT', 1),
			("Full Window", "Full Window", "Sample a grid of pixels among the whole window", 'FACESEL', 2),
			],
		description="Select an auto exposure metering mode",
		default="Center Weighted"
		)

	ec : bpy.props.FloatProperty(
		name = "EV Compensation",
		description = "Exposure Compensation value: add or subtract brightness",
		min = -3,
		max = 3,
		step = 1,
		precision = 2,
		default = 0
		)

	center_grid : bpy.props.IntProperty(
		name = "Circles",
		description = "Number of circles to sample: more circles means more accurate auto exposure, but also means slower viewport",
		min = 2,
		max = 20,
		default = 4
		)

	full_grid : bpy.props.IntProperty(
		name = "Grid",
		description = "Number of rows and columns to sample: more rows and columns means more accurate auto exposure, but also means slower viewport",
		min = 2,
		max = 20,
		default = 7
		)


# Render engine handler
@persistent
def camera_handler(scene):
	subscribe_to = bpy.types.RenderSettings, "engine"
	bpy.types.Scene.realcam_render = object()
	bpy.msgbus.subscribe_rna(
		key=subscribe_to,
		owner=bpy.types.Scene.realcam_render,
		args=(),
		notify=realcam_handler
		)

@persistent
def realcam_handler(*args):
	ae = bpy.context.scene.camera_settings.enable_ae
	if ae:
		engine = bpy.context.scene.render.engine
		global old_engine
		global handle
		if engine!=old_engine:
			if old_engine=="BLENDER_EEVEE":
				bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
			elif old_engine=="CYCLES":
				bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
			if engine=="BLENDER_EEVEE":
				handle = bpy.types.SpaceView3D.draw_handler_add(ae_calc, (), 'WINDOW', 'PRE_VIEW')
			if engine=="CYCLES":
				handle = bpy.types.SpaceView3D.draw_handler_add(ae_calc, (), 'WINDOW', 'POST_PIXEL')
			old_engine = engine

def unsubscribe_to_rna_props():
	bpy.msgbus.clear_by_owner(bpy.types.Scene.realcam_render)


# Preferences Updater
@addon_updater_ops.make_annotations
class RealCameraPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	auto_check_update = bpy.props.BoolProperty(
		name="Auto-check for Update",
		description="If enabled, auto-check for updates using an interval",
		default=True,
		)
	updater_intrval_months = bpy.props.IntProperty(
		name='Months',
		description="Number of months between checking for updates",
		default=0,
		min=0
		)
	updater_intrval_days = bpy.props.IntProperty(
		name='Days',
		description="Number of days between checking for updates",
		default=1,
		min=0,
		max=31
		)
	updater_intrval_hours = bpy.props.IntProperty(
		name='Hours',
		description="Number of hours between checking for updates",
		default=0,
		min=0,
		max=23
		)
	updater_intrval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description="Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59
		)

	def draw(self, context):
		layout = self.layout
		mainrow = layout.row()
		col = mainrow.column()
		addon_updater_ops.update_settings_ui(self, context)


############################################################################
classes = (
	REALCAMERA_PT_Panel,
	AUTOEXP_PT_Panel,
	CameraSettings,
	RealCameraPreferences
	)

register, unregister = bpy.utils.register_classes_factory(classes)

# Register
def register():
	# Updater
	addon_updater_ops.register(bl_info)
	for cls in classes:
		addon_updater_ops.make_annotations(cls)
		bpy.utils.register_class(cls)
	bpy.types.Scene.camera_settings = bpy.props.PointerProperty(type=CameraSettings)
	# Render engine handler
	bpy.app.handlers.load_post.append(camera_handler)
	camera_handler(None)


# Unregister
def unregister():
	# Updater
	addon_updater_ops.unregister()
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.camera_settings
	# Render engine handler
	bpy.app.handlers.load_post.remove(camera_handler)
	unsubscribe_to_rna_props()


if __name__ == "__main__":
	register()
