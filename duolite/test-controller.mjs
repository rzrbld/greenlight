import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'
import ts from 'typescript'

// Exercise the real navigation loop in menus and streams without a browser.
const source = ts.transpileModule(fs.readFileSync(new URL('./controller.ts', import.meta.url), 'utf8'), {
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022},
}).outputText
for (const pathname of ['/home', '/stream/console']) {
    let next, quits = 0, restored = false, cancelled = false
    const pad = {id: 'Retroid Pocket Duo Lite Gamepad', connected: true,
        buttons: Array.from({length: 17}, () => ({pressed: false})), axes: [0, 0, 0, 0]}
    const context = {
        exports: {},
        require: name => {
            assert.equal(name, './gamepad')
            return {installDuoGamepadAdapter: () => () => {restored = true}}
        },
        navigator: {getGamepads: () => [pad]},
        window: {location: {pathname}, history: {length: 1}},
        document: {querySelectorAll: () => [], activeElement: null},
        requestAnimationFrame: callback => {next = callback; return 1},
        cancelAnimationFrame: () => {cancelled = true},
    }
    vm.runInNewContext(source, context)
    const cleanup = context.exports.installDuoNavigation(() => {quits++})
    pad.buttons[8].pressed = pad.buttons[9].pressed = true
    for (const time of [100, 1600, 4000]) next(time)
    assert.equal(quits, 0, 'Select + Start must remain available to Xbox')
    pad.buttons[8].pressed = pad.buttons[9].pressed = false
    pad.buttons[16].pressed = true
    next(4100); next(4200)
    assert.equal(quits, 1, 'Home quits once per press')
    pad.buttons[16].pressed = false; next(4300)
    pad.id = 'Xbox Wireless Controller'; pad.buttons[16].pressed = true; next(4400)
    assert.equal(quits, 1, 'External Guide stays available to Xbox')
    cleanup()
    assert.ok(restored && cancelled, 'Navigation cleanup restores the gamepad adapter')
}
console.log('PASS: Home quits in menus/streams; Select+Start and external Guide do not quit')
