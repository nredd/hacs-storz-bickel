var Z=function(x,r,b,f){var g=arguments.length,w=g<3?r:f===null?f=Object.getOwnPropertyDescriptor(r,b):f,z;if(typeof Reflect==="object"&&typeof Reflect.decorate==="function")w=Reflect.decorate(x,r,b,f);else for(var Q=x.length-1;Q>=0;Q--)if(z=x[Q])w=(g<3?z(w):g>3?z(r,b,w):z(r,b))||w;return g>3&&w&&Object.defineProperty(r,b,w),w};var m=globalThis,h=m.ShadowRoot&&(m.ShadyCSS===void 0||m.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,x1=Symbol(),W1=new WeakMap;class l{constructor(x,r,b){if(this._$cssResult$=!0,b!==x1)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=x,this.t=r}get styleSheet(){let x=this.o,r=this.t;if(h&&x===void 0){let b=r!==void 0&&r.length===1;b&&(x=W1.get(r)),x===void 0&&((this.o=x=new CSSStyleSheet).replaceSync(this.cssText),b&&W1.set(r,x))}return x}toString(){return this.cssText}}var P1=(x)=>new l(typeof x=="string"?x:x+"",void 0,x1),O=(x,...r)=>{let b=x.length===1?x[0]:r.reduce((f,g,w)=>f+((z)=>{if(z._$cssResult$===!0)return z.cssText;if(typeof z=="number")return z;throw Error("Value passed to 'css' function must be a 'css' function result: "+z+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(g)+x[w+1],x[0]);return new l(b,x,x1)},U1=(x,r)=>{if(h)x.adoptedStyleSheets=r.map((b)=>b instanceof CSSStyleSheet?b:b.styleSheet);else for(let b of r){let f=document.createElement("style"),g=m.litNonce;g!==void 0&&f.setAttribute("nonce",g),f.textContent=b.cssText,x.appendChild(f)}},r1=h?(x)=>x:(x)=>x instanceof CSSStyleSheet?((r)=>{let b="";for(let f of r.cssRules)b+=f.cssText;return P1(b)})(x):x;var{is:g0,defineProperty:w0,getOwnPropertyDescriptor:z0,getOwnPropertyNames:Q0,getOwnPropertySymbols:J0,getPrototypeOf:K0}=Object,u=globalThis,O1=u.trustedTypes,$0=O1?O1.emptyScript:"",k0=u.reactiveElementPolyfillSupport,N=(x,r)=>x,c={toAttribute(x,r){switch(r){case Boolean:x=x?$0:null;break;case Object:case Array:x=x==null?x:JSON.stringify(x)}return x},fromAttribute(x,r){let b=x;switch(r){case Boolean:b=x!==null;break;case Number:b=x===null?null:Number(x);break;case Object:case Array:try{b=JSON.parse(x)}catch(f){b=null}}return b}},a=(x,r)=>!g0(x,r),C1={attribute:!0,type:String,converter:c,reflect:!1,useDefault:!1,hasChanged:a};Symbol.metadata??=Symbol("metadata"),u.litPropertyMetadata??=new WeakMap;class o extends HTMLElement{static addInitializer(x){this._$Ei(),(this.l??=[]).push(x)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(x,r=C1){if(r.state&&(r.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(x)&&((r=Object.create(r)).wrapped=!0),this.elementProperties.set(x,r),!r.noAccessor){let b=Symbol(),f=this.getPropertyDescriptor(x,b,r);f!==void 0&&w0(this.prototype,x,f)}}static getPropertyDescriptor(x,r,b){let{get:f,set:g}=z0(this.prototype,x)??{get(){return this[r]},set(w){this[r]=w}};return{get:f,set(w){let z=f?.call(this);g?.call(this,w),this.requestUpdate(x,z,b)},configurable:!0,enumerable:!0}}static getPropertyOptions(x){return this.elementProperties.get(x)??C1}static _$Ei(){if(this.hasOwnProperty(N("elementProperties")))return;let x=K0(this);x.finalize(),x.l!==void 0&&(this.l=[...x.l]),this.elementProperties=new Map(x.elementProperties)}static finalize(){if(this.hasOwnProperty(N("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(N("properties"))){let r=this.properties,b=[...Q0(r),...J0(r)];for(let f of b)this.createProperty(f,r[f])}let x=this[Symbol.metadata];if(x!==null){let r=litPropertyMetadata.get(x);if(r!==void 0)for(let[b,f]of r)this.elementProperties.set(b,f)}this._$Eh=new Map;for(let[r,b]of this.elementProperties){let f=this._$Eu(r,b);f!==void 0&&this._$Eh.set(f,r)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(x){let r=[];if(Array.isArray(x)){let b=new Set(x.flat(1/0).reverse());for(let f of b)r.unshift(r1(f))}else x!==void 0&&r.push(r1(x));return r}static _$Eu(x,r){let b=r.attribute;return b===!1?void 0:typeof b=="string"?b:typeof x=="string"?x.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise((x)=>this.enableUpdating=x),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach((x)=>x(this))}addController(x){(this._$EO??=new Set).add(x),this.renderRoot!==void 0&&this.isConnected&&x.hostConnected?.()}removeController(x){this._$EO?.delete(x)}_$E_(){let x=new Map,r=this.constructor.elementProperties;for(let b of r.keys())this.hasOwnProperty(b)&&(x.set(b,this[b]),delete this[b]);x.size>0&&(this._$Ep=x)}createRenderRoot(){let x=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return U1(x,this.constructor.elementStyles),x}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach((x)=>x.hostConnected?.())}enableUpdating(x){}disconnectedCallback(){this._$EO?.forEach((x)=>x.hostDisconnected?.())}attributeChangedCallback(x,r,b){this._$AK(x,b)}_$ET(x,r){let b=this.constructor.elementProperties.get(x),f=this.constructor._$Eu(x,b);if(f!==void 0&&b.reflect===!0){let g=(b.converter?.toAttribute!==void 0?b.converter:c).toAttribute(r,b.type);this._$Em=x,g==null?this.removeAttribute(f):this.setAttribute(f,g),this._$Em=null}}_$AK(x,r){let b=this.constructor,f=b._$Eh.get(x);if(f!==void 0&&this._$Em!==f){let g=b.getPropertyOptions(f),w=typeof g.converter=="function"?{fromAttribute:g.converter}:g.converter?.fromAttribute!==void 0?g.converter:c;this._$Em=f;let z=w.fromAttribute(r,g.type);this[f]=z??this._$Ej?.get(f)??z,this._$Em=null}}requestUpdate(x,r,b,f=!1,g){if(x!==void 0){let w=this.constructor;if(f===!1&&(g=this[x]),b??=w.getPropertyOptions(x),!((b.hasChanged??a)(g,r)||b.useDefault&&b.reflect&&g===this._$Ej?.get(x)&&!this.hasAttribute(w._$Eu(x,b))))return;this.C(x,r,b)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(x,r,{useDefault:b,reflect:f,wrapped:g},w){b&&!(this._$Ej??=new Map).has(x)&&(this._$Ej.set(x,w??r??this[x]),g!==!0||w!==void 0)||(this._$AL.has(x)||(this.hasUpdated||b||(r=void 0),this._$AL.set(x,r)),f===!0&&this._$Em!==x&&(this._$Eq??=new Set).add(x))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(r){Promise.reject(r)}let x=this.scheduleUpdate();return x!=null&&await x,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[f,g]of this._$Ep)this[f]=g;this._$Ep=void 0}let b=this.constructor.elementProperties;if(b.size>0)for(let[f,g]of b){let{wrapped:w}=g,z=this[f];w!==!0||this._$AL.has(f)||z===void 0||this.C(f,void 0,g,z)}}let x=!1,r=this._$AL;try{x=this.shouldUpdate(r),x?(this.willUpdate(r),this._$EO?.forEach((b)=>b.hostUpdate?.()),this.update(r)):this._$EM()}catch(b){throw x=!1,this._$EM(),b}x&&this._$AE(r)}willUpdate(x){}_$AE(x){this._$EO?.forEach((r)=>r.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(x)),this.updated(x)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(x){return!0}update(x){this._$Eq&&=this._$Eq.forEach((r)=>this._$ET(r,this[r])),this._$EM()}updated(x){}firstUpdated(x){}}o.elementStyles=[],o.shadowRootOptions={mode:"open"},o[N("elementProperties")]=new Map,o[N("finalized")]=new Map,k0?.({ReactiveElement:o}),(u.reactiveElementVersions??=[]).push("2.1.2");var b1=globalThis,V1=(x)=>x,n=b1.trustedTypes,H1=n?n.createPolicy("lit-html",{createHTML:(x)=>x}):void 0;var G=`lit$${Math.random().toFixed(9).slice(2)}$`,j1="?"+G,Z0=`<${j1}>`,d=document,I=()=>d.createComment(""),L=(x)=>x===null||typeof x!="object"&&typeof x!="function",f1=Array.isArray,q0=(x)=>f1(x)||typeof x?.[Symbol.iterator]=="function";var _=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,o1=/-->/g,G1=/>/g,D=RegExp(`>|[ 	
\f\r](?:([^\\s"'>=/]+)([ 	
\f\r]*=[ 	
\f\r]*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),D1=/'/g,p1=/"/g,M1=/^(?:script|style|textarea|title)$/i,g1=(x)=>(r,...b)=>({_$litType$:x,strings:r,values:b}),k=g1(1),N1=g1(2),T0=g1(3),j=Symbol.for("lit-noChange"),J=Symbol.for("lit-nothing"),d1=new WeakMap,p=d.createTreeWalker(d,129);function c1(x,r){if(!f1(x)||!x.hasOwnProperty("raw"))throw Error("invalid template strings array");return H1!==void 0?H1.createHTML(r):r}var Y0=(x,r)=>{let b=x.length-1,f=[],g,w=r===2?"<svg>":r===3?"<math>":"",z=_;for(let Q=0;Q<b;Q++){let $=x[Q],B,K,Y=-1,X=0;for(;X<$.length&&(z.lastIndex=X,K=z.exec($),K!==null);)X=z.lastIndex,z===_?K[1]==="!--"?z=o1:K[1]!==void 0?z=G1:K[2]!==void 0?(M1.test(K[2])&&(g=RegExp("</"+K[2],"g")),z=D):K[3]!==void 0&&(z=D):z===D?K[0]===">"?(z=g??_,Y=-1):K[1]===void 0?Y=-2:(Y=z.lastIndex-K[2].length,B=K[1],z=K[3]===void 0?D:K[3]==='"'?p1:D1):z===p1||z===D1?z=D:z===o1||z===G1?z=_:(z=D,g=void 0);let P=z===D&&x[Q+1].startsWith("/>")?" ":"";w+=z===_?$+Z0:Y>=0?(f.push(B),$.slice(0,Y)+"$lit$"+$.slice(Y)+G+P):$+G+(Y===-2?Q:P)}return[c1(x,w+(x[b]||"<?>")+(r===2?"</svg>":r===3?"</math>":"")),f]};class R{constructor({strings:x,_$litType$:r},b){let f;this.parts=[];let g=0,w=0,z=x.length-1,Q=this.parts,[$,B]=Y0(x,r);if(this.el=R.createElement($,b),p.currentNode=this.el.content,r===2||r===3){let K=this.el.content.firstChild;K.replaceWith(...K.childNodes)}for(;(f=p.nextNode())!==null&&Q.length<z;){if(f.nodeType===1){if(f.hasAttributes())for(let K of f.getAttributeNames())if(K.endsWith("$lit$")){let Y=B[w++],X=f.getAttribute(K).split(G),P=/([.?@])?(.*)/.exec(Y);Q.push({type:1,index:g,name:P[2],strings:X,ctor:P[1]==="."?I1:P[1]==="?"?L1:P[1]==="@"?R1:A}),f.removeAttribute(K)}else K.startsWith(G)&&(Q.push({type:6,index:g}),f.removeAttribute(K));if(M1.test(f.tagName)){let K=f.textContent.split(G),Y=K.length-1;if(Y>0){f.textContent=n?n.emptyScript:"";for(let X=0;X<Y;X++)f.append(K[X],I()),p.nextNode(),Q.push({type:2,index:++g});f.append(K[Y],I())}}}else if(f.nodeType===8)if(f.data===j1)Q.push({type:2,index:g});else{let K=-1;for(;(K=f.data.indexOf(G,K+1))!==-1;)Q.push({type:7,index:g}),K+=G.length-1}g++}}static createElement(x,r){let b=d.createElement("template");return b.innerHTML=x,b}}function M(x,r,b=x,f){if(r===j)return r;let g=f!==void 0?b._$Co?.[f]:b._$Cl,w=L(r)?void 0:r._$litDirective$;return g?.constructor!==w&&(g?._$AO?.(!1),w===void 0?g=void 0:(g=new w(x),g._$AT(x,b,f)),f!==void 0?(b._$Co??=[])[f]=g:b._$Cl=g),g!==void 0&&(r=M(x,g._$AS(x,r.values),g,f)),r}class _1{constructor(x,r){this._$AV=[],this._$AN=void 0,this._$AD=x,this._$AM=r}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(x){let{el:{content:r},parts:b}=this._$AD,f=(x?.creationScope??d).importNode(r,!0);p.currentNode=f;let g=p.nextNode(),w=0,z=0,Q=b[0];for(;Q!==void 0;){if(w===Q.index){let $;Q.type===2?$=new T(g,g.nextSibling,this,x):Q.type===1?$=new Q.ctor(g,Q.name,Q.strings,this,x):Q.type===6&&($=new T1(g,this,x)),this._$AV.push($),Q=b[++z]}w!==Q?.index&&(g=p.nextNode(),w++)}return p.currentNode=d,f}p(x){let r=0;for(let b of this._$AV)b!==void 0&&(b.strings!==void 0?(b._$AI(x,b,r),r+=b.strings.length-2):b._$AI(x[r])),r++}}class T{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(x,r,b,f){this.type=2,this._$AH=J,this._$AN=void 0,this._$AA=x,this._$AB=r,this._$AM=b,this.options=f,this._$Cv=f?.isConnected??!0}get parentNode(){let x=this._$AA.parentNode,r=this._$AM;return r!==void 0&&x?.nodeType===11&&(x=r.parentNode),x}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(x,r=this){x=M(this,x,r),L(x)?x===J||x==null||x===""?(this._$AH!==J&&this._$AR(),this._$AH=J):x!==this._$AH&&x!==j&&this._(x):x._$litType$!==void 0?this.$(x):x.nodeType!==void 0?this.T(x):q0(x)?this.k(x):this._(x)}O(x){return this._$AA.parentNode.insertBefore(x,this._$AB)}T(x){this._$AH!==x&&(this._$AR(),this._$AH=this.O(x))}_(x){this._$AH!==J&&L(this._$AH)?this._$AA.nextSibling.data=x:this.T(d.createTextNode(x)),this._$AH=x}$(x){let{values:r,_$litType$:b}=x,f=typeof b=="number"?this._$AC(x):(b.el===void 0&&(b.el=R.createElement(c1(b.h,b.h[0]),this.options)),b);if(this._$AH?._$AD===f)this._$AH.p(r);else{let g=new _1(f,this),w=g.u(this.options);g.p(r),this.T(w),this._$AH=g}}_$AC(x){let r=d1.get(x.strings);return r===void 0&&d1.set(x.strings,r=new R(x)),r}k(x){f1(this._$AH)||(this._$AH=[],this._$AR());let r=this._$AH,b,f=0;for(let g of x)f===r.length?r.push(b=new T(this.O(I()),this.O(I()),this,this.options)):b=r[f],b._$AI(g),f++;f<r.length&&(this._$AR(b&&b._$AB.nextSibling,f),r.length=f)}_$AR(x=this._$AA.nextSibling,r){for(this._$AP?.(!1,!0,r);x!==this._$AB;){let b=V1(x).nextSibling;V1(x).remove(),x=b}}setConnected(x){this._$AM===void 0&&(this._$Cv=x,this._$AP?.(x))}}class A{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(x,r,b,f,g){this.type=1,this._$AH=J,this._$AN=void 0,this.element=x,this.name=r,this._$AM=f,this.options=g,b.length>2||b[0]!==""||b[1]!==""?(this._$AH=Array(b.length-1).fill(new String),this.strings=b):this._$AH=J}_$AI(x,r=this,b,f){let g=this.strings,w=!1;if(g===void 0)x=M(this,x,r,0),w=!L(x)||x!==this._$AH&&x!==j,w&&(this._$AH=x);else{let z=x,Q,$;for(x=g[0],Q=0;Q<g.length-1;Q++)$=M(this,z[b+Q],r,Q),$===j&&($=this._$AH[Q]),w||=!L($)||$!==this._$AH[Q],$===J?x=J:x!==J&&(x+=($??"")+g[Q+1]),this._$AH[Q]=$}w&&!f&&this.j(x)}j(x){x===J?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,x??"")}}class I1 extends A{constructor(){super(...arguments),this.type=3}j(x){this.element[this.name]=x===J?void 0:x}}class L1 extends A{constructor(){super(...arguments),this.type=4}j(x){this.element.toggleAttribute(this.name,!!x&&x!==J)}}class R1 extends A{constructor(x,r,b,f,g){super(x,r,b,f,g),this.type=5}_$AI(x,r=this){if((x=M(this,x,r,0)??J)===j)return;let b=this._$AH,f=x===J&&b!==J||x.capture!==b.capture||x.once!==b.once||x.passive!==b.passive,g=x!==J&&(b===J||f);f&&this.element.removeEventListener(this.name,this,b),g&&this.element.addEventListener(this.name,this,x),this._$AH=x}handleEvent(x){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,x):this._$AH.handleEvent(x)}}class T1{constructor(x,r,b){this.element=x,this.type=6,this._$AN=void 0,this._$AM=r,this.options=b}get _$AU(){return this._$AM._$AU}_$AI(x){M(this,x)}}var X0=b1.litHtmlPolyfillSupport;X0?.(R,T),(b1.litHtmlVersions??=[]).push("3.3.3");var A1=(x,r,b)=>{let f=b?.renderBefore??r,g=f._$litPart$;if(g===void 0){let w=b?.renderBefore??null;f._$litPart$=g=new T(r.insertBefore(I(),w),w,void 0,b??{})}return g._$AI(x),g};var w1=globalThis;class F extends o{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let x=super.createRenderRoot();return this.renderOptions.renderBefore??=x.firstChild,x}update(x){let r=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(x),this._$Do=A1(r,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return j}}F._$litElement$=!0,F.finalized=!0,w1.litElementHydrateSupport?.({LitElement:F});var F0=w1.litElementPolyfillSupport;F0?.({LitElement:F});(w1.litElementVersions??=[]).push("4.2.2");var B0={attribute:!0,type:String,converter:c,reflect:!1,hasChanged:a},W0=(x=B0,r,b)=>{let{kind:f,metadata:g}=b,w=globalThis.litPropertyMetadata.get(g);if(w===void 0&&globalThis.litPropertyMetadata.set(g,w=new Map),f==="setter"&&((x=Object.create(x)).wrapped=!0),w.set(b.name,x),f==="accessor"){let{name:z}=b;return{set(Q){let $=r.get.call(this);r.set.call(this,Q),this.requestUpdate(z,$,x,!0,Q)},init(Q){return Q!==void 0&&this.C(z,void 0,x,Q),Q}}}if(f==="setter"){let{name:z}=b;return function(Q){let $=this[z];r.call(this,Q),this.requestUpdate(z,$,x,!0,Q)}}throw Error("Unsupported decorator location: "+f)};function q(x){return(r,b)=>typeof b=="object"?W0(x,r,b):((f,g,w)=>{let z=g.hasOwnProperty(w);return g.constructor.createProperty(w,f),z?Object.getOwnPropertyDescriptor(g,w):void 0})(x,r,b)}function C(x){return q({...x,state:!0,attribute:!1})}var E1="0.1.0",E="storz-bickel-card",i="storz-bickel-card-editor",z1="sb-temp-dial",Q1="sb-seven-segment",J1="sb-history-chart",K1="sb-sessions-chart",y1="storz_bickel",S1=[175,185,195];var v1=(x)=>x.strings===void 0;var m1={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},$1=(x)=>(...r)=>({_$litDirective$:x,values:r});class k1{constructor(x){}get _$AU(){return this._$AM._$AU}_$AT(x,r,b){this._$Ct=x,this._$AM=r,this._$Ci=b}_$AS(x,r){return this.update(x,r)}update(x,r){return this.render(...r)}}var y=(x,r)=>{let b=x._$AN;if(b===void 0)return!1;for(let f of b)f._$AO?.(r,!1),y(f,r);return!0},e=(x)=>{let r,b;do{if((r=x._$AM)===void 0)break;b=r._$AN,b.delete(x),x=r}while(b?.size===0)},h1=(x)=>{for(let r;r=x._$AM;x=r){let b=r._$AN;if(b===void 0)r._$AN=b=new Set;else if(b.has(x))break;b.add(x),O0(r)}};function P0(x){this._$AN!==void 0?(e(this),this._$AM=x,h1(this)):this._$AM=x}function U0(x,r=!1,b=0){let f=this._$AH,g=this._$AN;if(g!==void 0&&g.size!==0)if(r)if(Array.isArray(f))for(let w=b;w<f.length;w++)y(f[w],!1),e(f[w]);else f!=null&&(y(f,!1),e(f));else y(this,x)}var O0=(x)=>{x.type==m1.CHILD&&(x._$AP??=U0,x._$AQ??=P0)};class Z1 extends k1{constructor(){super(...arguments),this._$AN=void 0}_$AT(x,r,b){super._$AT(x,r,b),h1(this),this.isConnected=x._$AU}_$AO(x,r=!0){x!==this.isConnected&&(this.isConnected=x,x?this.reconnected?.():this.disconnected?.()),r&&(y(this,x),e(this))}setValue(x){if(v1(this._$Ct))this._$Ct._$AI(x,this);else{let r=[...this._$Ct._$AH];r[this._$Ci]=x,this._$Ct._$AI(r,this,0)}}disconnected(){}reconnected(){}}var q1=new WeakMap,l1=$1(class extends Z1{render(x){return J}update(x,[r]){let b=r!==this.G;return b&&this.rt(void 0),(b||this.lt!==this.ct)&&(this.G=r,this.ht=x.options?.host,this.rt(this.ct=x.element)),J}rt(x){if(this.G!==void 0)if(this.isConnected||(x=void 0),typeof this.G=="function"){let r=this.ht??globalThis,b=q1.get(r);b===void 0&&(b=new WeakMap,q1.set(r,b)),b.get(this.G)!==void 0&&this.G.call(this.ht,void 0),b.set(this.G,x),x!==void 0&&this.G.call(this.ht,x)}else this.G.value=x}get lt(){return typeof this.G=="function"?q1.get(this.ht??globalThis)?.get(this.G):this.G?.value}disconnected(){this.lt===this.ct&&this.rt(void 0)}reconnected(){this.rt(this.ct)}});var S=300,V=-150,C0=12.5,V0=75;function Y1(x,r,b){return Math.min(b,Math.max(r,x))}class u1 extends F{constructor(){super(...arguments);this.min=40;this.max=230;this.unit="°C";this.active=!1;this.heating=!1;this.disabled=!1;this.dragging=!1}containerRef;fraction(x){if(this.max<=this.min)return 0;return Y1((x-this.min)/(this.max-this.min),0,1)}get mode(){if(!this.active||this.disabled)return"off";if(this.current!==void 0&&this.target!==void 0&&this.current>=this.target-1)return"ready";return"heating"}ticks(){let x=[];for(let r=V;r<=V+S+0.001;r+=C0){if(!(Math.abs((r-V)%V0)<0.01)){x.push({angle:r,major:!1,label:"",labelOffset:0});continue}let f=this.min+(r-V)/S*(this.max-this.min),g=`${Math.round(f)}${this.unit}`,w=r*Math.PI/180,z=g.length*3.1,Q=5,$=134+z*Math.abs(Math.sin(w))+Q*Math.abs(Math.cos(w));x.push({angle:r,major:!0,label:g,labelOffset:$})}return x}angleFromPointer(x,r){let b=this.containerRef?.getBoundingClientRect();if(!b)return V;let f=b.left+b.width/2,g=b.top+b.height/2,z=Math.atan2(r-g,x-f)*180/Math.PI;if(z<V)z+=360;return Y1(z,V,V+S)}emitDrag(x){this.dispatchEvent(new CustomEvent("dial-drag",{detail:{value:x},bubbles:!0,composed:!0}))}handlePointerDown=(x)=>{if(this.disabled)return;this.dragging=!0,x.target.setPointerCapture(x.pointerId),this.handlePointerMove(x)};handlePointerMove=(x)=>{if(!this.dragging)return;let r=this.angleFromPointer(x.clientX,x.clientY),b=this.min+(r-V)/S*(this.max-this.min);this.emitDrag(Y1(Math.round(b),this.min,this.max))};handlePointerUp=(x)=>{this.dragging=!1,x.target.releasePointerCapture?.(x.pointerId)};render(){let x=this.disabled?void 0:this.target,r=x===void 0?V:V+this.fraction(x)*S;return k`
      <div
        class="dial ${this.mode} ${this.disabled?"disabled":""} ${this.dragging?"dragging":""}"
        ${l1((b)=>{this.containerRef=b})}
        @pointerdown=${this.handlePointerDown}
        @pointermove=${this.handlePointerMove}
        @pointerup=${this.handlePointerUp}
        @pointercancel=${this.handlePointerUp}
      >
        ${this.ticks().map((b)=>k`
            <div class="tick" style="transform:translate(-50%,-50%) rotate(${b.angle}deg)">
              <div class="dash ${b.major?"major":"minor"}"></div>
              ${b.major?k`
                    <div
                      class="tick-label"
                      style="top:-${b.labelOffset}px;transform:translate(-50%,-50%) rotate(${-b.angle}deg)"
                    >
                      <span>${b.label}</span>
                    </div>
                  `:J}
            </div>
          `)}
        <div class="knob-wrapper">
          <div class="knob-face" style="transform:rotate(${r}deg)">
            <div class="indicator"></div>
          </div>
          <div class="knob-overlay"></div>
          <div class="readout">
            <span class="current"
              >${this.current===void 0||this.disabled?"—":Math.round(this.current)}</span
            >
          </div>
        </div>
      </div>
    `}static styles=O`
    :host {
      display: block;
      --sb-dial-accent: var(--sb-color-heating, #ff6a3d);
    }

    .dial {
      position: relative;
      width: 280px;
      max-width: 100%;
      aspect-ratio: 1;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: grab;
      touch-action: none;
      user-select: none;
    }

    .dial.disabled {
      cursor: not-allowed;
      opacity: 0.5;
    }

    .dial.dragging {
      cursor: grabbing;
    }

    .tick {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 0;
      height: 0;
    }

    .dash {
      position: absolute;
      left: -0.5px;
      top: -124px;
      width: 1px;
      height: 7px;
      border-radius: 0.5px;
      background: rgba(127, 127, 127, 0.3);
    }

    .dash.major {
      left: -1px;
      top: -128px;
      width: 2px;
      height: 13px;
      background: var(--secondary-text-color, rgba(127, 127, 127, 0.6));
    }

    .tick-label {
      position: absolute;
      left: 0;
      display: flex;
    }

    .tick-label span {
      font-family: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 10px;
      color: var(--secondary-text-color);
      white-space: nowrap;
    }

    .knob-wrapper {
      width: 190px;
      height: 190px;
      border-radius: 50%;
      position: relative;
      background: var(--card-background-color, #0e0c09);
      box-shadow:
        0 16px 34px rgba(0, 0, 0, 0.55),
        0 3px 6px rgba(0, 0, 0, 0.4);
    }

    .knob-face {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: radial-gradient(circle at 50% 30%, #433c31 0%, #211d17 58%, #16130e 100%);
      position: absolute;
      inset: 0;
      transition: transform 0.6s ease;
    }

    .dial.off .knob-face {
      background: radial-gradient(circle at 50% 30%, #3a3a3a 0%, #1e1e1e 58%, #141414 100%);
    }

    .indicator {
      position: absolute;
      top: 16px;
      left: 50%;
      width: 5px;
      height: 36px;
      background: var(--sb-dial-accent);
      border-radius: 3px;
      transform: translateX(-50%);
      box-shadow: 0 0 10px rgba(255, 106, 61, 0.85);
    }

    .dial.off .indicator {
      background: var(--disabled-text-color, #9e9e9e);
      box-shadow: none;
    }

    .dial.heating .knob-face {
      animation: sb-breathe 3s ease-in-out infinite;
    }

    @keyframes sb-breathe {
      0%,
      100% {
        filter: drop-shadow(0 0 2px var(--sb-dial-accent));
      }
      50% {
        filter: drop-shadow(0 0 10px var(--sb-dial-accent));
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .dial.heating .knob-face {
        animation: none;
      }
      .knob-face {
        transition: none;
      }
    }

    .knob-overlay {
      position: absolute;
      inset: 0;
      border-radius: 50%;
      pointer-events: none;
      box-shadow:
        inset 0 0 0 1px rgba(255, 255, 255, 0.05),
        inset 0 3px 5px rgba(255, 255, 255, 0.05),
        inset 0 -12px 24px rgba(0, 0, 0, 0.5);
    }

    .readout {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      pointer-events: none;
    }

    .current {
      font-size: clamp(1.8rem, 14cqw, 2.6rem);
      font-weight: 300;
      font-variant-numeric: tabular-nums;
      color: var(--primary-text-color);
    }
  `}Z([q({type:Number})],u1.prototype,"current",void 0),Z([q({type:Number})],u1.prototype,"target",void 0),Z([q({type:Number})],u1.prototype,"min",void 0),Z([q({type:Number})],u1.prototype,"max",void 0),Z([q()],u1.prototype,"unit",void 0),Z([q({type:Boolean})],u1.prototype,"active",void 0),Z([q({type:Boolean})],u1.prototype,"heating",void 0),Z([q({type:Boolean})],u1.prototype,"disabled",void 0),Z([C()],u1.prototype,"dragging",void 0);if(!customElements.get(z1))customElements.define(z1,u1);var a1=["preset_1","preset_2","preset_3"],H0=[{name:"device",required:!0,selector:{device:{integration:"storz_bickel"}}},{name:"name",selector:{text:{}}},...a1.map((x)=>({name:x,selector:{number:{mode:"box",step:1}}}))],o0={device:"Device",name:"Name (optional)",preset_1:"Preset 1",preset_2:"Preset 2",preset_3:"Preset 3"};class X1 extends F{setConfig(x){this.config=x}get formData(){let x=this.config?.presets??[];return{device:this.config?.device??"",name:this.config?.name,preset_1:x[0],preset_2:x[1],preset_3:x[2]}}handleValueChanged(x){if(x.stopPropagation(),!this.config)return;let r=x.detail.value,b=a1.map((g)=>r[g]).filter((g)=>typeof g==="number"&&Number.isFinite(g)),f={type:this.config.type,device:typeof r.device==="string"?r.device:""};if(typeof r.name==="string"&&r.name!=="")f.name=r.name;if(b.length>0)f.presets=b;this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:f},bubbles:!0,composed:!0}))}render(){if(!this.config)return J;return k`
      <ha-form
        .hass=${this.hass}
        .data=${this.formData}
        .schema=${H0}
        .computeLabel=${(x)=>o0[x.name]??x.name}
        @value-changed=${this.handleValueChanged}
      ></ha-form>
    `}}Z([q({attribute:!1})],X1.prototype,"hass",void 0),Z([C()],X1.prototype,"config",void 0);function n1(x,r){let b=Object.values(x.entities).filter((g)=>g.device_id===r&&g.platform===y1),f=(g,w)=>b.find((z)=>z.entity_id.startsWith(`${g}.`)&&z.translation_key===w)?.entity_id;return{climate:f("climate","heater"),temperature:f("sensor","temperature"),pump:f("switch","pump"),vibration:f("switch","vibration"),autoShutoffEnabled:f("switch","auto_shutoff_enabled"),battery:f("sensor","battery"),connection:f("binary_sensor","connection"),ledBrightness:f("number","led_brightness"),autoShutoffMinutes:f("number","auto_shutoff_minutes"),boostTemperature:f("number","boost_temperature"),currentSessionStart:f("sensor","current_session_start"),sessionHistory:f("sensor","session_history"),totalSessions:f("sensor","total_sessions"),favoriteTemperature:f("sensor","favorite_temperature"),totalRuntime:f("sensor","total_runtime"),bleFirmwareVersion:f("sensor","ble_firmware_version"),pumpFailsafeSeconds:f("number","pump_failsafe_seconds"),pumpCooldownSeconds:f("number","pump_cooldown_seconds"),tempStep:f("number","temp_step")}}var F1=560,v=110,G0=30000;function D0(x){if(x<=0)return 10;let r=10**Math.floor(Math.log10(x)),b=x/r;return(b<=1?1:b<=2?2:b<=5?5:10)*r}class s1 extends F{constructor(){super(...arguments);this.windowMinutes=30;this.unit="°";this.points=[]}refreshTimer;connectedCallback(){super.connectedCallback(),this.refresh(),this.refreshTimer=setInterval(()=>this.refresh(),G0)}disconnectedCallback(){super.disconnectedCallback(),clearInterval(this.refreshTimer)}updated(x){if(x.has("entityId")||x.has("windowMinutes"))this.refresh()}async refresh(){if(!this.hass||!this.entityId){this.points=[];return}let x=new Date,b=`history/period/${new Date(x.getTime()-this.windowMinutes*60000).toISOString()}?filter_entity_id=${this.entityId}&end_time=${x.toISOString()}&minimal_response`;try{let g=(await this.hass.callApi("GET",b))[0]??[];this.points=g.map((w)=>({t:new Date(w.last_changed).getTime(),v:Number(w.state)})).filter((w)=>Number.isFinite(w.v))}catch{this.points=[]}}render(){let x=this.points[this.points.length-1],r=this.points.map((w)=>w.v),b=r.length?Math.min(...r):0,f=D0(r.length?Math.max(...r):0),g=[0,0.25,0.5,0.75,1].map((w)=>Math.round(f*w));return k`
      <div class="header">
        <span class="title">Temperature · live</span>
        ${x!==void 0?k`<span class="current">${Math.round(x.v)}${this.unit}</span>`:J}
      </div>
      <div class="chart-row">
        <div class="y-axis">
          ${g.slice().reverse().map((w)=>k`<span>${w}</span>`)}
        </div>
        <div class="plot">
          ${this.renderSvg(b,f)}
        </div>
      </div>
    `}renderSvg(x,r){if(this.points.length<2)return k`<div class="empty">No data yet</div>`;let b=this.points[0],f=this.points[this.points.length-1];if(!b||!f)return J;let g=Math.max(1,f.t-b.t),w=Math.max(1,r-x),z=(K)=>({x:(K.t-b.t)/g*F1,y:v-(K.v-x)/w*v}),$=this.points.map(z).map((K,Y)=>`${Y===0?"M":"L"} ${K.x} ${K.y}`).join(" "),B=`${$} L ${F1} ${v} L 0 ${v} Z`;return N1`
      <svg viewBox="0 0 ${F1} ${v}" preserveAspectRatio="none" role="img" aria-label="Temperature history">
        <defs>
          <linearGradient id="sb-history-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--sb-color-heating, #ff9800)" stop-opacity="0.35" />
            <stop offset="100%" stop-color="var(--sb-color-heating, #ff9800)" stop-opacity="0" />
          </linearGradient>
        </defs>
        <path d=${B} fill="url(#sb-history-fill)" />
        <path
          d=${$}
          fill="none"
          stroke="var(--sb-color-heating, #ff9800)"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    `}static styles=O`
    :host {
      display: block;
    }

    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 14px;
    }

    .title {
      font-size: 11px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--secondary-text-color);
    }

    .current {
      font-family: "JetBrains Mono", ui-monospace, monospace;
      font-size: 15px;
      font-weight: 600;
      color: var(--sb-color-heating, #ff9800);
    }

    .chart-row {
      display: flex;
      gap: 8px;
    }

    .y-axis {
      width: 32px;
      height: 110px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      font-size: 9px;
      color: var(--secondary-text-color);
      text-align: right;
    }

    .plot {
      position: relative;
      flex: 1;
      height: 110px;
    }

    svg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      display: block;
    }

    .empty {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: var(--disabled-text-color, #9e9e9e);
      font-size: 12px;
    }
  `}Z([q({attribute:!1})],s1.prototype,"hass",void 0),Z([q()],s1.prototype,"entityId",void 0),Z([q({type:Number})],s1.prototype,"windowMinutes",void 0),Z([q()],s1.prototype,"unit",void 0),Z([C()],s1.prototype,"points",void 0);if(!customElements.get(J1))customElements.define(J1,s1);class i1 extends F{constructor(){super(...arguments);this.showTarget=!0;this.unit="F"}emitUnit(x){if(x===this.unit)return;this.dispatchEvent(new CustomEvent("unit-change",{detail:{unit:x},bubbles:!0,composed:!0}))}render(){let x=this.current===void 0?"---":String(Math.round(this.current)),r=this.target===void 0?"---":String(Math.round(this.target));return k`
      <div class="readout-panel">
        <div class="digits">
          <div class="ghost">888</div>
          <div class="lit current">${x}<span class="deg">°</span></div>
        </div>
        ${this.showTarget?k`
              <div class="digits target-digits">
                <div class="ghost small">888</div>
                <div class="lit small target">${r}<span class="deg">°</span></div>
              </div>
            `:J}
      </div>
      <div class="unit-toggle">
        <button
          class=${this.unit==="F"?"active":""}
          aria-pressed=${this.unit==="F"}
          @click=${()=>this.emitUnit("F")}
        >
          °F
        </button>
        <button
          class=${this.unit==="C"?"active":""}
          aria-pressed=${this.unit==="C"}
          @click=${()=>this.emitUnit("C")}
        >
          °C
        </button>
      </div>
    `}static styles=O`
    :host {
      display: flex;
      align-items: center;
      gap: 10px;
      --sb-seg-accent: var(--sb-color-heating, #ff9800);
    }

    .readout-panel {
      background: var(--card-background-color, #0d0b08);
      border-radius: 8px;
      padding: 12px 20px;
      box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.5);
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      line-height: 1;
    }

    .digits {
      position: relative;
      font-family: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-variant-numeric: tabular-nums;
      font-size: 40px;
      font-weight: 600;
      letter-spacing: 0.02em;
    }

    .target-digits {
      font-size: 22px;
      margin-top: 2px;
    }

    .ghost {
      color: var(--sb-seg-accent);
      opacity: 0.08;
    }

    .lit {
      position: absolute;
      inset: 0;
      text-align: right;
      color: var(--sb-seg-accent);
      text-shadow: 0 0 18px rgba(255, 152, 0, 0.6);
    }

    .lit.target {
      color: var(--secondary-text-color, #a39a8c);
      text-shadow: none;
    }

    .deg {
      font-size: 0.6em;
      vertical-align: text-top;
    }

    .unit-toggle {
      display: flex;
      flex-direction: column;
      border: 1px solid var(--divider-color, rgba(255, 255, 255, 0.1));
      border-radius: 8px;
      overflow: hidden;
    }

    .unit-toggle button {
      border: none;
      padding: 8px 12px;
      font-size: 12px;
      font-family: "JetBrains Mono", ui-monospace, monospace;
      cursor: pointer;
      background: var(--secondary-background-color, #242019);
      color: var(--secondary-text-color, #a39a8c);
    }

    .unit-toggle button.active {
      background: var(--sb-seg-accent);
      color: var(--primary-background-color, #1a1207);
    }
  `}Z([q({type:Number})],i1.prototype,"current",void 0),Z([q({type:Number})],i1.prototype,"target",void 0),Z([q({type:Boolean})],i1.prototype,"showTarget",void 0),Z([q()],i1.prototype,"unit",void 0);if(!customElements.get(Q1))customElements.define(Q1,i1);function p0(){return new Date().toISOString().slice(0,10)}function d0(x){return new Date(`${x}T00:00:00`).toLocaleDateString(void 0,{weekday:"short"}).slice(0,2)}class e1 extends F{constructor(){super(...arguments);this.dailyCounts={}}render(){let x=Object.entries(this.dailyCounts).sort(([g],[w])=>g.localeCompare(w)),r=x.reduce((g,[,w])=>g+w,0),b=Math.max(1,...x.map(([,g])=>g)),f=p0();return k`
      <div class="header">
        <span class="title">Sessions · ${r} total · ${x.length}d</span>
      </div>
      ${x.length===0?k`<div class="empty">No sessions yet</div>`:k`
            <div class="bars">
              ${x.map(([g,w])=>{let z=w===0?3:Math.max(6,w/b*100);return k`
                  <div class="bar-col" title="${g}: ${w} session${w===1?"":"s"}">
                    <div
                      class="bar ${g===f?"today":""} ${w===0?"zero":""}"
                      style="height:${z}%"
                    ></div>
                  </div>
                `})}
            </div>
            <div class="x-axis">
              ${x.map(([g])=>k`<span>${d0(g)}</span>`)}
            </div>
          `}
    `}static styles=O`
    :host {
      display: block;
    }

    .header {
      margin-bottom: 14px;
    }

    .title {
      font-size: 11px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--secondary-text-color);
    }

    .bars {
      display: flex;
      align-items: flex-end;
      gap: 4px;
      height: 100px;
    }

    .bar-col {
      flex: 1;
      display: flex;
      align-items: flex-end;
      height: 100%;
    }

    .bar {
      width: 100%;
      border-radius: 2px;
      background: #c85a35;
      transition: height 0.3s ease;
    }

    .bar.zero {
      background: var(--secondary-background-color, #242019);
    }

    .bar.today {
      background: var(--sb-color-heating, #ff9800);
      box-shadow: 0 0 8px rgba(255, 152, 0, 0.6);
    }

    .x-axis {
      display: flex;
      gap: 4px;
      margin-top: 6px;
    }

    .x-axis span {
      flex: 1;
      text-align: center;
      font-size: 9px;
      color: var(--secondary-text-color);
    }

    .empty {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100px;
      color: var(--disabled-text-color, #9e9e9e);
      font-size: 12px;
    }
  `}Z([q({attribute:!1})],e1.prototype,"dailyCounts",void 0);if(!customElements.get(K1))customElements.define(K1,e1);var t1=O`
  :host {
    --sb-heat: var(--sb-color-heating, #ff9800);
    --sb-ready: var(--sb-color-ready, #4caf50);
  }

  ha-card {
    padding: 16px;
  }

  .body {
    container-type: inline-size;
    display: flex;
    flex-direction: column;
    gap: 16px;
    transition: opacity 0.3s ease;
  }

  .body.disconnected .grid {
    opacity: 0.45;
    pointer-events: none;
  }

  /* ---- header ---------------------------------------------------------- */

  .header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 10px;
  }

  .titles {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }

  .kicker {
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--secondary-text-color);
  }

  .name {
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--primary-text-color);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: none;
  }

  .connection-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
    color: var(--secondary-text-color);
  }

  .connection-chip::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: currentColor;
  }

  .connection-chip.on {
    color: var(--sb-ready);
    background: color-mix(in srgb, var(--sb-ready) 16%, transparent);
  }

  .connection-chip.off {
    color: var(--error-color, #f44336);
    background: color-mix(in srgb, var(--error-color, #f44336) 16%, transparent);
    animation: sb-blink 1.6s ease-in-out infinite;
  }

  @keyframes sb-blink {
    50% {
      opacity: 0.5;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .connection-chip.off {
      animation: none;
    }
  }

  .battery {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 10px;
    border-radius: 12px;
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
    color: var(--secondary-text-color);
    font-size: 0.85rem;
    font-variant-numeric: tabular-nums;
  }

  /* ---- layout ------------------------------------------------------------ */

  .grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 20px;
    align-items: start;
  }

  @container (max-width: 640px) {
    .grid {
      grid-template-columns: 1fr;
    }
  }

  .left-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 18px;
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.06));
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
    border-radius: 10px;
    padding: 24px;
  }

  .right-col {
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-width: 0;
  }

  .panel {
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.06));
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
    border-radius: 10px;
    padding: 18px 20px;
  }

  .panel-title {
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--secondary-text-color);
    margin-bottom: 10px;
  }

  /* ---- readout + status label -------------------------------------------- */

  .status-label {
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--secondary-text-color);
  }

  /* ---- stepper ------------------------------------------------------------ */

  .stepper {
    display: flex;
    align-items: center;
    gap: 16px;
    background: var(--card-background-color, rgba(0, 0, 0, 0.2));
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
    border-radius: 100px;
    padding: 6px;
  }

  .step {
    width: 44px;
    height: 44px;
    flex: none;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
    border-radius: 50%;
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
    color: var(--primary-text-color);
    font-size: 1.2rem;
    line-height: 1;
    cursor: pointer;
    transition: transform 0.1s ease;
  }

  .step:active {
    transform: scale(0.92);
  }

  .step:disabled {
    cursor: not-allowed;
    opacity: 0.4;
  }

  .stepper-value {
    min-width: 96px;
    text-align: center;
  }

  .stepper-value span {
    font-size: 1rem;
    font-weight: 600;
    color: var(--primary-text-color);
    font-variant-numeric: tabular-nums;
  }

  .step-caption {
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    color: var(--secondary-text-color);
  }

  /* ---- preset chips ---------------------------------------------------- */

  .presets {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .preset {
    padding: 7px 16px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 18px;
    background: transparent;
    color: var(--primary-text-color);
    font-size: 0.9rem;
    font-variant-numeric: tabular-nums;
    cursor: pointer;
    transition:
      background 0.2s ease,
      color 0.2s ease,
      border-color 0.2s ease,
      transform 0.1s ease;
  }

  .preset:active {
    transform: scale(0.95);
  }

  .preset.active {
    border-color: transparent;
    background: var(--sb-heat);
    color: #fff;
  }

  /* ---- HEAT / AIR toggle row --------------------------------------------- */

  .toggle-row {
    display: flex;
    gap: 12px;
    width: 100%;
  }

  .heat-btn,
  .air-btn {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 100px;
    background: transparent;
    color: var(--primary-text-color);
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    cursor: pointer;
    transition:
      background 0.25s ease,
      color 0.25s ease,
      box-shadow 0.25s ease,
      transform 0.1s ease;
  }

  .heat-btn:active,
  .air-btn:active {
    transform: scale(0.97);
  }

  .heat-btn.on {
    border-color: transparent;
    background: var(--sb-heat);
    color: #1a1207;
    box-shadow: 0 0 14px color-mix(in srgb, var(--sb-heat) 60%, transparent);
  }

  .air-btn.on {
    border-color: transparent;
    background: var(--primary-color, #03a9f4);
    color: #fff;
  }

  /* ---- session panel ----------------------------------------------------- */

  .session-panel {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .session-timer {
    font-size: 1.8rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    color: var(--primary-text-color);
  }

  .sessions-today {
    text-align: center;
  }

  .sessions-today-count {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--primary-text-color);
  }

  .sessions-today-label {
    font-size: 0.7rem;
    color: var(--secondary-text-color);
  }

  /* ---- device info + settings --------------------------------------------- */

  .info-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 8px 0;
    font-size: 0.9rem;
    color: var(--primary-text-color);
    border-top: 1px solid var(--divider-color, rgba(127, 127, 127, 0.1));
  }

  .info-row:first-of-type {
    border-top: none;
  }

  .info-row select {
    background: var(--card-background-color, rgba(0, 0, 0, 0.2));
    color: var(--primary-text-color);
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 0.85rem;
    font-variant-numeric: tabular-nums;
  }

  details.settings {
    border-top: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
    padding-top: 4px;
  }

  summary {
    padding: 8px 0;
    font-size: 0.9rem;
    color: var(--secondary-text-color);
    cursor: pointer;
    list-style: none;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  summary::before {
    content: "▸";
    transition: transform 0.2s ease;
  }

  details[open] summary::before {
    transform: rotate(90deg);
  }

  .row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    font-size: 0.9rem;
    color: var(--primary-text-color);
  }

  .row label {
    flex: 1;
  }

  .row .value {
    min-width: 3.5em;
    text-align: right;
    color: var(--secondary-text-color);
    font-variant-numeric: tabular-nums;
  }

  input[type="range"] {
    flex: 2;
    accent-color: var(--sb-heat);
  }

  input[type="checkbox"] {
    width: 20px;
    height: 20px;
    accent-color: var(--sb-heat);
  }
`;function W(x){let r=typeof x==="string"?Number(x):x;return typeof r==="number"&&Number.isFinite(r)?r:void 0}function t(x){return{currentTemperature:W(x.attributes.current_temperature),targetTemperature:W(x.attributes.temperature),minTemp:W(x.attributes.min_temp)??40,maxTemp:W(x.attributes.max_temp)??230,targetTempStep:W(x.attributes.target_temp_step)??1,hvacAction:typeof x.attributes.hvac_action==="string"?x.attributes.hvac_action:void 0}}function x0(x,r,b){if(r===b)return x;return r==="C"?x*9/5+32:(x-32)*5/9}function r0(x,r,b){if(r===b)return x;return r==="C"?x*1.8:x/1.8}function j0(x){return x.includes("F")?"F":"C"}function M0(){return new Date().toISOString().slice(0,10)}function N0(x){let r=Math.max(0,Math.floor(x)),b=Math.floor(r/3600),f=Math.floor(r%3600/60),g=r%60,w=(z)=>String(z).padStart(2,"0");return b>0?`${b}:${w(f)}:${w(g)}`:`${f}:${w(g)}`}class b0 extends F{constructor(){super(...arguments);this.chartWindowMinutes=30}debounceMs=500;debounceTimer;liveTickTimer;static styles=t1;connectedCallback(){super.connectedCallback(),this.liveTickTimer=setInterval(()=>this.requestUpdate(),1000)}disconnectedCallback(){super.disconnectedCallback(),clearInterval(this.liveTickTimer),clearTimeout(this.debounceTimer)}static getConfigElement(){return document.createElement(i)}static getStubConfig(x){return{device:(x?Object.values(x.entities).find((b)=>b.platform==="storz_bickel"&&b.device_id):void 0)?.device_id??"",presets:[...S1]}}setConfig(x){if(!x.device)throw Error("storz-bickel-card: 'device' is required (a Storz & Bickel device)");this.config=x}getCardSize(){return 10}getGridOptions(){return{columns:12,rows:14,min_columns:8,min_rows:10}}get entityIds(){if(!this.hass||!this.config)return{};return n1(this.hass,this.config.device)}entityState(x){return x?this.hass?.states[x]:void 0}callService(x,r,b){this.hass?.callService(x,r,b)}setTargetTemperature(x,r){this.callService("climate","set_temperature",{entity_id:x,temperature:r})}debounceTarget(x,r){this.pendingTarget=x,clearTimeout(this.debounceTimer),this.debounceTimer=setTimeout(()=>{this.pendingTarget=void 0,this.setTargetTemperature(r,x)},this.debounceMs)}handleDialStep(x,r){let b=t(r),f=this.pendingTarget??b.targetTemperature??b.minTemp,g=Math.min(b.maxTemp,Math.max(b.minTemp,f+x*b.targetTempStep));this.debounceTarget(g,r.entity_id)}handleDialDrag(x,r,b){let f=t(r),g=this.displayUnitOverride??b,w=x0(x,g,b),z=Math.min(f.maxTemp,Math.max(f.minTemp,w));this.debounceTarget(z,r.entity_id)}handlePreset(x,r){let b=t(r),f=Math.min(b.maxTemp,Math.max(b.minTemp,x));clearTimeout(this.debounceTimer),this.pendingTarget=f,this.setTargetTemperature(r.entity_id,f)}toggleHeat(x){this.callService("climate","set_hvac_mode",{entity_id:x.entity_id,hvac_mode:x.state==="heat"?"off":"heat"})}toggleSwitch(x){this.callService("switch",x.state==="on"?"turn_off":"turn_on",{entity_id:x.entity_id})}setNumber(x,r){this.callService("number","set_value",{entity_id:x,value:r})}render(){if(!this.hass||!this.config)return J;let x=this.entityIds,r=this.entityState(x.climate);if(!r)return k`<ha-card><div class="body">Device entities not found.</div></ha-card>`;let b=t(r),f=this.entityState(x.connection),g=f?f.state==="on":!0,w=r.state==="heat",z=b.hvacAction==="heating",Q=this.pendingTarget??b.targetTemperature,$=this.entityState(x.battery),B=this.entityState(x.pump),K=j0(this.hass.config.unit_system.temperature),Y=this.displayUnitOverride??K,X=(H)=>x0(H,K,Y),P=this.hass.devices[this.config.device],U=this.config.name??P?.name_by_user??P?.name??"Storz & Bickel",B1=this.config.presets??[],f0=!w?"IDLE":z?"HEATING":b.currentTemperature!==void 0&&Q!==void 0&&b.currentTemperature>=Q-1?"HOLDING":"HEATING";return k`
      <ha-card>
        <div class="body ${g?"":"disconnected"}">
          <div class="header">
            <div class="titles">
              <span class="kicker">${P?.name??"Storz & Bickel"}</span>
              <span class="name">${U}</span>
            </div>
            <div class="header-right">
              ${$&&W($.state)!==void 0?k`<span class="battery">🔋 ${Math.round(W($.state)??0)}%</span>`:J}
              <span class="connection-chip ${g?"on":"off"}"
                >${g?"ONLINE":"OFFLINE"}</span
              >
            </div>
          </div>

          <div class="grid">
            <div class="left-col">
              <sb-seven-segment
                .current=${b.currentTemperature===void 0?void 0:X(b.currentTemperature)}
                .target=${Q===void 0?void 0:X(Q)}
                .showTarget=${w}
                .unit=${Y}
                @unit-change=${(H)=>{this.displayUnitOverride=H.detail.unit}}
              ></sb-seven-segment>
              <div class="status-label">${f0}</div>
              <sb-temp-dial
                .current=${b.currentTemperature===void 0?void 0:X(b.currentTemperature)}
                .target=${Q===void 0?void 0:X(Q)}
                .min=${X(b.minTemp)}
                .max=${X(b.maxTemp)}
                .unit=${`°${Y}`}
                ?active=${w}
                ?heating=${z}
                ?disabled=${!g}
                @dial-drag=${(H)=>this.handleDialDrag(H.detail.value,r,K)}
              ></sb-temp-dial>
              <div class="stepper">
                <button
                  class="step minus"
                  aria-label="Decrease target temperature"
                  ?disabled=${!g}
                  @click=${()=>this.handleDialStep(-1,r)}
                >
                  −
                </button>
                <div class="stepper-value">
                  <span
                    >${Q===void 0?"—":Math.round(X(Q))}°${Y}</span
                  >
                  <div class="step-caption">
                    ${Math.round(r0(b.targetTempStep,K,Y)*10)/10}°
                    STEP
                  </div>
                </div>
                <button
                  class="step plus"
                  aria-label="Increase target temperature"
                  ?disabled=${!g}
                  @click=${()=>this.handleDialStep(1,r)}
                >
                  +
                </button>
              </div>
              ${B1.length>0?k`
                    <div class="presets">
                      ${B1.map((H)=>k`
                          <button
                            class="preset ${Q!==void 0&&Math.round(Q)===Math.round(H)?"active":""}"
                            @click=${()=>this.handlePreset(H,r)}
                          >
                            ${Math.round(X(H))}°${Y}
                          </button>
                        `)}
                    </div>
                  `:J}
              <div class="toggle-row">
                <button class="heat-btn ${w?"on":""}" @click=${()=>this.toggleHeat(r)}>
                  HEAT
                </button>
                ${B?k`
                      <button
                        class="air-btn ${B.state==="on"?"on":""}"
                        @click=${()=>this.toggleSwitch(B)}
                      >
                        AIR
                      </button>
                    `:J}
              </div>
            </div>

            <div class="right-col">
              ${this.renderSessionPanel(x)}
              <div class="panel">
                <sb-history-chart
                  .hass=${this.hass}
                  .entityId=${x.temperature}
                  .windowMinutes=${this.chartWindowMinutes}
                  .unit=${`°${Y}`}
                ></sb-history-chart>
              </div>
              <div class="panel">${this.renderSessionsChart(x)}</div>
              <div class="panel">${this.renderDeviceInfo(x,K,Y)}</div>
              ${this.renderSettings(x)}
            </div>
          </div>
        </div>
      </ha-card>
    `}renderSessionPanel(x){let r=this.entityState(x.currentSessionStart),b=this.entityState(x.sessionHistory),f=r&&r.state!=="unknown"?r.state:void 0,g=f?(Date.now()-new Date(f).getTime())/1000:void 0,z=(b?.attributes.daily_counts??{})[M0()]??0;return k`
      <div class="panel session-panel">
        <div>
          <div class="panel-title">Session</div>
          <div class="session-timer">
            ${g===void 0?"—:—":N0(g)}
          </div>
        </div>
        <div class="sessions-today">
          <div class="sessions-today-count">${z}</div>
          <div class="sessions-today-label">sessions today</div>
        </div>
      </div>
    `}renderSessionsChart(x){let b=this.entityState(x.sessionHistory)?.attributes.daily_counts??{};return k`<sb-sessions-chart .dailyCounts=${b}></sb-sessions-chart>`}renderDeviceInfo(x,r,b){let f=this.entityState(x.totalRuntime),g=this.entityState(x.bleFirmwareVersion),w=this.config?this.hass?.devices[this.config.device]?.sw_version:void 0,z=this.entityState(x.autoShutoffMinutes),Q=this.entityState(x.pumpFailsafeSeconds),$=this.entityState(x.pumpCooldownSeconds),B=this.entityState(x.tempStep);if(!f&&!w&&!g&&!z&&!Q&&!$&&!B)return J;let K=[5,10,15,20,30,45,60,90,120,180,240,360,480,720].map((U)=>({value:U,label:`${U} min`})),Y=[15,30,45,60,90,120,180,300,450,600].map((U)=>({value:U,label:`${U} sec`})),X=[1,2,3,5,10,15,30,60,120,300].map((U)=>({value:U,label:`${U} sec`})),P=[0.5,1,1.5,2,2.5,3,4,5].map((U)=>({value:U,label:`${Math.round(r0(U,r,b)*10)/10}°${b}`}));return k`
      <div class="panel-title">Device info</div>
      ${f&&W(f.state)!==void 0?k`<div class="info-row">
            <span>Total runtime</span><span>${W(f.state)?.toFixed(1)} h</span>
          </div>`:J}
      ${w?k`<div class="info-row"><span>Firmware</span><span>${w}</span></div>`:J}
      ${g&&g.state!=="unavailable"&&g.state!=="unknown"?k`<div class="info-row">
            <span>Bluetooth firmware</span><span>${g.state}</span>
          </div>`:J}
      ${z?this.renderSelectRow("Auto shutoff",z,K):J}
      ${Q?this.renderSelectRow("Pump failsafe",Q,Y):J}
      ${$?this.renderSelectRow("Pump cooldown",$,X):J}
      ${B?this.renderSelectRow("Temp step",B,P):J}
    `}renderSelectRow(x,r,b){let f=W(r.state);return k`
      <div class="info-row">
        <span>${x}</span>
        <select
          @change=${(g)=>this.setNumber(r.entity_id,Number(g.target.value))}
        >
          ${b.map((g)=>k`
              <option value=${g.value} ?selected=${f===g.value}>
                ${g.label}
              </option>
            `)}
        </select>
      </div>
    `}renderSettings(x){let r=this.entityState(x.ledBrightness),b=this.entityState(x.boostTemperature),f=this.entityState(x.vibration);if(!r&&!b&&!f)return J;return k`
      <details class="settings panel">
        <summary>More settings</summary>
        ${r?this.renderNumberRow("LED brightness",r,"%"):J}
        ${b?this.renderNumberRow("Boost",b,"°"):J}
        ${f?k`
              <div class="row">
                <label for="vibration">Vibration</label>
                <input
                  id="vibration"
                  type="checkbox"
                  .checked=${f.state==="on"}
                  @change=${()=>this.toggleSwitch(f)}
                />
              </div>
            `:J}
      </details>
    `}renderNumberRow(x,r,b){let f=W(r.state),g=W(r.attributes.min)??0,w=W(r.attributes.max)??100,z=W(r.attributes.step)??1,Q=r.entity_id.replaceAll(".","-");return k`
      <div class="row">
        <label for=${Q}>${x}</label>
        <input
          id=${Q}
          type="range"
          min=${g}
          max=${w}
          step=${z}
          .value=${String(f??g)}
          @change=${($)=>this.setNumber(r.entity_id,Number($.target.value))}
        />
        <span class="value">${f??"—"}${b}</span>
      </div>
    `}}Z([q({attribute:!1})],b0.prototype,"hass",void 0),Z([C()],b0.prototype,"config",void 0),Z([C()],b0.prototype,"pendingTarget",void 0),Z([C()],b0.prototype,"displayUnitOverride",void 0),Z([C()],b0.prototype,"chartWindowMinutes",void 0);if(!customElements.get(E))customElements.define(E,b0);if(!customElements.get(i))customElements.define(i,X1);window.customCards=window.customCards??[];if(!window.customCards.some((x)=>x.type===E))window.customCards.push({type:E,name:"Storz & Bickel Card",description:"Controls for Storz & Bickel vaporizers (Volcano, Venty, Veazy, Crafty).",preview:!0,documentationURL:"https://github.com/nredd/hacs-storz-bickel"});console.info(`%c STORZ-BICKEL-CARD %c v${E1} `,"background: #ff9800; color: #fff; font-weight: 600; border-radius: 3px 0 0 3px;","background: #424242; color: #fff; border-radius: 0 3px 3px 0;");export{b0 as StorzBickelCard};
