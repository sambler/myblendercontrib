import bpy


def add(origin):
    operators_registered = 'do_action' in dir(bpy.ops.console)
    print(origin, ': operators registered')
    try:
        wm = bpy.context.window_manager

        console = wm.keyconfigs.user.keymaps.get('Console')
        if console:
            keymaps = console.keymap_items
            if not ('console.do_action' in keymaps):
                keymaps.new('console.do_action', 'RET', 'PRESS', ctrl=1)

        TE = wm.keyconfigs.user.keymaps.get('Text')
        if TE:
            keymaps = TE.keymap_items
            if not ('text.do_comment' in keymaps):
                keymaps.new('text.do_comment', 'SLASH', 'PRESS', ctrl=1)

            cycle_textblocks = 'text.cycle_textblocks'
            if not (cycle_textblocks in keymaps):
                m = keymaps.new(cycle_textblocks, 'WHEELUPMOUSE', 'PRESS', alt=1)
                m.properties.direction = 1

                m = keymaps.new(cycle_textblocks, 'WHEELDOWNMOUSE', 'PRESS', alt=1)
                m.properties.direction = -1

    except:
        print('BCPrompt keymaps maybe already exist, didnt dupe')
