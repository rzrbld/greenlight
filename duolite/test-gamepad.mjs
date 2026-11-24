import assert from 'node:assert/strict'
import {normalizeDuoPad} from './gamepad.ts'

const labels=['A','B','X','Y','L','R','L2','R2','Select','Start','L3','R3','Up','Down','Left','Right','Guide']
// Browser indices captured on the actual Duo; trigger slots remain pass-through.
const raw={B:0,A:1,X:2,Y:3,L:4,R:5,L2:6,R2:7,Select:8,Start:9,Guide:10,L3:11,R3:12,Up:13,Down:14,Left:15,Right:16}
const xbox={A:'B',B:'A',X:'Y',Y:'X'}
const make=()=>({id:'Retroid Pocket Duo Lite Gamepad (Vendor: 2f24 Product: 0001)',mapping:'',index:0,connected:true,timestamp:123,axes:[.2,-.4,.6,-.8],buttons:Array.from({length:18},()=>({value:0,pressed:false,touched:false})),vibrationActuator:{marker:'native rumble'}})
for(const [name,index] of Object.entries(raw)) {
    const p=make();p.buttons[index]={value:1,pressed:true,touched:true}
    const mapped=normalizeDuoPad(p)
    assert.equal(mapped.mapping,'standard')
    assert.equal(mapped.buttons.filter(b=>b.pressed).length,1)
    assert.equal(mapped.buttons[labels.indexOf(xbox[name] ?? name)].pressed,true,`${name} → ${xbox[name] ?? name}`)
    assert.equal(mapped.vibrationActuator,p.vibrationActuator)
    assert.equal(mapped.axes,p.axes)
}
const fn=make();fn.buttons[17].pressed=true;assert.equal(normalizeDuoPad(fn).buttons.some(b=>b.pressed),false)
const external=make();external.id='Xbox Wireless Controller';assert.equal(normalizeDuoPad(external),external)
const standard=make();standard.mapping='standard';assert.equal(normalizeDuoPad(standard),standard)
assert.equal(normalizeDuoPad(null),null)
console.log('PASS: measured Duo mapping, Xbox face positions, triggers, D-pad, thumbs, Guide, native rumble and external-controller isolation')
