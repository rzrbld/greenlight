import {installDuoGamepadAdapter} from './gamepad'

// Renderer-only menu navigation. Streaming keeps Greenlight's native gamepad path.
export function installDuoNavigation(quit: () => void) {
    const restoreGamepads = installDuoGamepadAdapter()
    let raf = 0, lastDirection = '', nextRepeat = 0, wasA = false, wasB = false, wasHome = false
    const visible = () => Array.from(document.querySelectorAll<HTMLElement>('button,a[href],input,select,textarea,[role="button"]'))
        .filter(el => !el.hasAttribute('disabled') && el.getBoundingClientRect().width > 0 && el.getBoundingClientRect().height > 0)
    const focus = (direction: string) => {
        const nodes = visible(), current = document.activeElement as HTMLElement
        if (!nodes.length) return
        if (!nodes.includes(current)) { nodes[0].focus(); return }
        const a = current.getBoundingClientRect(), ax = a.x + a.width/2, ay = a.y + a.height/2
        const horizontal = direction === 'left' || direction === 'right', sign = direction === 'left' || direction === 'up' ? -1 : 1
        const candidates = nodes.filter(el => el !== current).map(el => {
            const b = el.getBoundingClientRect(), dx = b.x+b.width/2-ax, dy = b.y+b.height/2-ay
            const along = (horizontal ? dx : dy)*sign, across = Math.abs(horizontal ? dy : dx)
            return {el, along, score: Math.hypot(dx,dy)+across*2}
        }).filter(item => item.along > 2).sort((a,b) => a.score-b.score)
        const target = candidates[0]?.el
        if (target) { target.focus(); target.scrollIntoView({block:'nearest',inline:'nearest'}) }
    }
    const tick = (now: number) => {
        const pad = Array.from(navigator.getGamepads()).find(p => p?.connected)
        if (pad) {
            const down = (i: number) => !!pad.buttons[i]?.pressed
            // Reserve only the handheld Home button; View+Menu belongs to Xbox.
            const home = /Retroid Pocket Duo Lite|Vendor: 2f24 Product: 0001/i.test(pad.id) && down(16)
            if (home && !wasHome) quit()
            wasHome = home
            const streaming = window.location.pathname.includes('/stream/')
            if (!streaming) {
                const direction = down(12) || pad.axes[1] < -.6 ? 'up' : down(13) || pad.axes[1] > .6 ? 'down' : down(14) || pad.axes[0] < -.6 ? 'left' : down(15) || pad.axes[0] > .6 ? 'right' : ''
                if (direction && (direction !== lastDirection || now >= nextRepeat)) {
                    focus(direction); nextRepeat = now + (direction !== lastDirection ? 350 : 120)
                }
                lastDirection = direction
                if (down(0) && !wasA) {
                    const el = document.activeElement as HTMLElement
                    if (visible().includes(el)) el.click(); else visible()[0]?.focus()
                }
                if (down(1) && !wasB && window.history.length > 1) window.history.back()
            }
            wasA = down(0); wasB = down(1)
        }
        raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => { cancelAnimationFrame(raf); restoreGamepads() }
}
