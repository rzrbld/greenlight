// Measured Chromium Linux mapping for the Duo Lite's 2f24:0001 controller.
// Preserve external controllers and Chromium's already-standard mappings.
export function normalizeDuoPad(pad: Gamepad | null): Gamepad | null {
    if (!pad || pad.mapping === 'standard' || pad.buttons.length !== 18 || pad.axes.length !== 4 ||
        !/Retroid Pocket Duo Lite|Vendor: 2f24 Product: 0001/i.test(pad.id)) return pad
    // Xbox face positions: physical B→A, A→B, Y→X, X→Y.
    // Shoulders/triggers, View/Menu, thumbs, D-pad and Guide stay unchanged.
    // The separate Fn button is left to the OS; it is not another Xbox button.
    const order = [0,1,3,2,4,5,6,7,8,9,11,12,13,14,15,16,10]
    return {
        id:pad.id, index:pad.index, connected:pad.connected, timestamp:pad.timestamp,
        mapping:'standard', axes:pad.axes, buttons:order.map(i => pad.buttons[i]),
        vibrationActuator:pad.vibrationActuator,
        hapticActuators:(pad as any).hapticActuators,
    } as unknown as Gamepad
}

export function installDuoGamepadAdapter() {
    const own = Object.getOwnPropertyDescriptor(navigator,'getGamepads')
    const original = navigator.getGamepads.bind(navigator)
    Object.defineProperty(navigator,'getGamepads',{configurable:true,value:()=>original().map(normalizeDuoPad)})
    return () => {
        if (own) Object.defineProperty(navigator,'getGamepads',own)
        else delete (navigator as any).getGamepads
    }
}
