<a name="sound_drivers"></a>
<img src="https://github.com/batFINGER/sound-bake-drivers/wiki/images/anim.gif"  width="100%" height="150" padding="10" align="center"/>
<h1 padding="10">Sound Drivers v3.1.0</h1>
**Blender Addon Drive animation with sound**
---

[Install](#install)&nbsp;&nbsp;
[Add Sound](#add_sound)&nbsp;&nbsp;
[Bake](#bake)&nbsp;&nbsp;
[Normalize](#normalize)&nbsp;&nbsp;
[NLA Stack](#nla_stack)&nbsp;&nbsp;
[Visualize](#visualize)&nbsp;&nbsp;
[Midi](#midi)&nbsp;&nbsp;


---
**Install the Addon<a name="install"></a>**

---

Open the zip file from github in your favourite archive program.  Move the `sound_drivers` folder into your blender  "scripts/addons/folder"

<a href="https://github.com/batFINGER/sound-bake-drivers/wiki/images/install_addon.png"><img src="https://github.com/batFINGER/sound-bake-drivers/wiki/images/install_addon.png" height="200" ></a>

[back to top](#sound_drivers)


---
**Add a Speaker and Sound<a name="add_sound"></a>**

---

Speaker Objects have been used as they are a convient way to store a sound in a blend file.  To get started add a speaker to the scene, go to the Properties window data panel and select a sound.  Speaker vismode options will become available as sounds are baked.


[back to top](#sound_drivers)

---
**Bake to multiple frequencies<a name="bake"></a>**

---

Only need to select the start and end frequencies to bake across a range.  By default bakes to 16 channels from 1 to 40,000 Hz (the audible spectrum) using a log base.  
<a href="https://github.com/batFINGER/sound-bake-drivers/wiki/images/bake.png"><img src="https://github.com/batFINGER/sound-bake-drivers/wiki/images/bake.png" height="200" ></a>

[back to top](#sound_drivers)



---
**Normalize Actions<a name="normalize"></a>**

---

Automatically makes the range of the action [0, 1] after baking using fcurve modifiers.  Setting normalize type to `CHANNEL` will normalize each channel from its min, max to [0, 1], or whatever range you choose.  Reverse ranges will invert the fcurves

<a href="https://github.com/batFINGER/sound-bake-drivers/wiki/images/normalize.png"><img src="https://github.com/batFINGER/sound-bake-drivers/wiki/images/normalize.png" height="200" ></a>

[back to top](#sound_drivers)


---
**UI Visualise with BGL<a name="visualize"></a>**

---

Display a visualiser using properties in the UI or with a BGL overlay on the UI. 

<a href="https://github.com/batFINGER/sound-bake-drivers/wiki/images/visualiser_new.png"><img src="https://github.com/batFINGER/sound-bake-drivers/wiki/images/visualiser_new.png" height="200" ></a>

<span text-size="-1" margin="0" padding="0">
_Image: Visualisers in the 3d view, graph editor and timeline"_
</span>

[back to top](#sound_drivers)


---
**NLA Stack<a name="nla_stack"></a>**

---

Bake or copy actions and add to the outcome using the NLA editor. Actions are automatically added to the NLA stack on baking. The action in the action slot ( assigned action to speaker) is the active action.  Other actions are saved (stacked) and actively take place in the animation. For example an action can be copied, then normalized to [radians(-180), radians(180)] to use this channel as a driver target for rotation properties.
<a href="https://github.com/batFINGER/sound-bake-drivers/wiki/images/nla.png"><img src="https://github.com/batFINGER/sound-bake-drivers/wiki/images/nla.png" height="200" ></a>

[back to top](#sound_drivers)

---
**Make Visualisers Quickly<a name="visualize"></a>**

---

Create and drive an object or set of objects with channel 0 of a sound bake, and the automatically produce a grid of objects, each driven by the corresponding channel.


<a href="https://github.com/batFINGER/sound-bake-drivers/wiki/images/visquick.png"><img src="https://github.com/batFINGER/sound-bake-drivers/wiki/images/visquick.png" height="200" ></a>

<span text-size="-1" margin="0" padding="0">
_Default Cylinder, array modifier with count driven by channel 0 of AA bake._
</span>

[back to top](#sound_drivers)

---
**MIDI file support<a name="midi"></a>**

---

<a href="https://github.com/batFINGER/sound-bake-drivers/wiki/images/install_addon.png"><img src="https://github.com/batFINGER/sound-bake-drivers/wiki/images/midi_icon.png" align="left" height="40" ></a> Bake a corresponding  midi file to fcurves.  Not sure what instrument is making that sound, well with an associated midi bake we can tell.


<a href="https://github.com/batFINGER/sound-bake-drivers/wiki/images/midi2.png"><img src="https://github.com/batFINGER/sound-bake-drivers/wiki/images/midi2.png" height="200" ></a> 

[back to top](#sound_drivers)


# mocap-madness
Extended tools for bvh mocap files.
Still very much in testing.
Multiple file import
One rig with multiple actions.
Rig only
Action only
Rescale action to rig
Use CMU names if applicable
Change rest pose.
Pose matching : make cycle animations or branch to others.

