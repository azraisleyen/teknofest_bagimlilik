export class QrController extends EventTarget {
 constructor({container,generalNode,announce=()=>{}}){super();this.container=container;this.generalNode=generalNode;this.announce=announce;this.state='BOOTING';this.eventId=null;this.generation=0;this.general();}
 transition(state,detail={}){this.state=state;this.dispatchEvent(new CustomEvent('statechange',{detail:{state,...detail}}));this.announce(state);}
 general(reason=null){this.generation++;this.eventId=null;this.container.replaceChildren(this.generalNode.cloneNode(true));this.transition(reason?'DEGRADED':'GENERAL_READY',{reason});}
 async start(eventId,loader){const generation=++this.generation;this.eventId=eventId;this.container.replaceChildren(this.generalNode.cloneNode(true));this.transition('DYNAMIC_PENDING',{eventId,generation});try{const node=await loader();if(this.eventId!==eventId||this.generation!==generation)return this.transition('DEGRADED',{reason:'STALE_RESPONSE'});this.container.replaceChildren(node);this.transition('DYNAMIC_ACTIVE',{eventId,generation});}catch{if(this.generation===generation)this.general('RENDER_OR_NETWORK_FAILURE');}}
 end(eventId){if(this.eventId===eventId)this.general();}
 shutdown(){this.general();this.transition('SHUTTING_DOWN');}
}
