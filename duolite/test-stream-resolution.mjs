import assert from 'node:assert/strict'
import { configureStreamResolution } from '../packages/desktop/renderer/lib/streamresolution.ts'
function fixture(){
    const sent=[]
    const control={start(){sent.push('start')},send(value){sent.push(JSON.parse(value))}}
    const message={generateMessage(path,data){return {path,data}}}
    return {sent,control,message,player:{getChannelProcessor(name){return name==='control'?control:message}}}
}
for(const [height,width] of [[720,1280],[1080,1920],[1440,2560]]){
    const {player,control,message,sent}=fixture()
    configureStreamResolution(player,height)
    control.start()
    assert.equal(sent[0],'start')
    assert.equal(sent[1].message,'VideoPreference')
    assert.deepEqual(sent[1].resolution,{width,height})
    assert.deepEqual(sent[1].dimensions,{width,height})
    assert.equal(sent[1].maxFPS,60)
    assert.deepEqual(sent[2],{message:'userRequestedResolutionUpdate',resolutionAlias:String(height)})
    const size=message.generateMessage('/streaming/characteristics/dimensionschanged',{extra:true,horizontal:1920,vertical:1080})
    assert.deepEqual(size.data,{extra:true,horizontal:width,vertical:height,preferredWidth:width,preferredHeight:height,safeAreaRight:width,safeAreaBottom:height})
    const data={keep:'untouched'};assert.equal(message.generateMessage('/other/message',data).data,data)
}
for(const height of [0,NaN,10000]){
    const {player,control,message,sent}=fixture();const start=control.start,generate=message.generateMessage
    configureStreamResolution(player,height)
    assert.equal(control.start,start);assert.equal(message.generateMessage,generate);assert.deepEqual(sent,[])
}
console.log('PASS: Xbox explicit resolution requests, matching dimensions, Auto and unrelated-message isolation')
