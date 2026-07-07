var z=function(o,x,f,b){var a=arguments.length,r=a<3?x:b===null?b=Object.getOwnPropertyDescriptor(x,f):b,w;if(typeof Reflect==="object"&&typeof Reflect.decorate==="function")r=Reflect.decorate(o,x,f,b);else for(var d=o.length-1;d>=0;d--)if(w=o[d])r=(a<3?w(r):a>3?w(x,f,r):w(x,f))||r;return a>3&&r&&Object.defineProperty(x,f,r),r};var T=globalThis,L=T.ShadowRoot&&(T.ShadyCSS===void 0||T.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,n=Symbol(),d0=new WeakMap;class y{constructor(o,x,f){if(this._$cssResult$=!0,f!==n)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=o,this.t=x}get styleSheet(){let o=this.o,x=this.t;if(L&&o===void 0){let f=x!==void 0&&x.length===1;f&&(o=d0.get(x)),o===void 0&&((this.o=o=new CSSStyleSheet).replaceSync(this.cssText),f&&d0.set(x,o))}return o}toString(){return this.cssText}}var p0=(o)=>new y(typeof o=="string"?o:o+"",void 0,n),v=(o,...x)=>{let f=o.length===1?o[0]:x.reduce((b,a,r)=>b+((w)=>{if(w._$cssResult$===!0)return w.cssText;if(typeof w=="number")return w;throw Error("Value passed to 'css' function must be a 'css' function result: "+w+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(a)+o[r+1],o[0]);return new y(f,o,n)},k0=(o,x)=>{if(L)o.adoptedStyleSheets=x.map((f)=>f instanceof CSSStyleSheet?f:f.styleSheet);else for(let f of x){let b=document.createElement("style"),a=T.litNonce;a!==void 0&&b.setAttribute("nonce",a),b.textContent=f.cssText,o.appendChild(b)}},u=L?(o)=>o:(o)=>o instanceof CSSStyleSheet?((x)=>{let f="";for(let b of x.cssRules)f+=b.cssText;return p0(f)})(o):o;var{is:j0,defineProperty:S0,getOwnPropertyDescriptor:T0,getOwnPropertyNames:L0,getOwnPropertySymbols:y0,getPrototypeOf:R0}=Object,R=globalThis,X0=R.trustedTypes,E0=X0?X0.emptyScript:"",m0=R.reactiveElementPolyfillSupport,P=(o,x)=>o,U={toAttribute(o,x){switch(x){case Boolean:o=o?E0:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,x){let f=o;switch(x){case Boolean:f=o!==null;break;case Number:f=o===null?null:Number(o);break;case Object:case Array:try{f=JSON.parse(o)}catch(b){f=null}}return f}},E=(o,x)=>!j0(o,x),Y0={attribute:!0,type:String,converter:U,reflect:!1,useDefault:!1,hasChanged:E};Symbol.metadata??=Symbol("metadata"),R.litPropertyMetadata??=new WeakMap;class B extends HTMLElement{static addInitializer(o){this._$Ei(),(this.l??=[]).push(o)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(o,x=Y0){if(x.state&&(x.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(o)&&((x=Object.create(x)).wrapped=!0),this.elementProperties.set(o,x),!x.noAccessor){let f=Symbol(),b=this.getPropertyDescriptor(o,f,x);b!==void 0&&S0(this.prototype,o,b)}}static getPropertyDescriptor(o,x,f){let{get:b,set:a}=T0(this.prototype,o)??{get(){return this[x]},set(r){this[x]=r}};return{get:b,set(r){let w=b?.call(this);a?.call(this,r),this.requestUpdate(o,w,f)},configurable:!0,enumerable:!0}}static getPropertyOptions(o){return this.elementProperties.get(o)??Y0}static _$Ei(){if(this.hasOwnProperty(P("elementProperties")))return;let o=R0(this);o.finalize(),o.l!==void 0&&(this.l=[...o.l]),this.elementProperties=new Map(o.elementProperties)}static finalize(){if(this.hasOwnProperty(P("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(P("properties"))){let x=this.properties,f=[...L0(x),...y0(x)];for(let b of f)this.createProperty(b,x[b])}let o=this[Symbol.metadata];if(o!==null){let x=litPropertyMetadata.get(o);if(x!==void 0)for(let[f,b]of x)this.elementProperties.set(f,b)}this._$Eh=new Map;for(let[x,f]of this.elementProperties){let b=this._$Eu(x,f);b!==void 0&&this._$Eh.set(b,x)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(o){let x=[];if(Array.isArray(o)){let f=new Set(o.flat(1/0).reverse());for(let b of f)x.unshift(u(b))}else o!==void 0&&x.push(u(o));return x}static _$Eu(o,x){let f=x.attribute;return f===!1?void 0:typeof f=="string"?f:typeof o=="string"?o.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise((o)=>this.enableUpdating=o),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach((o)=>o(this))}addController(o){(this._$EO??=new Set).add(o),this.renderRoot!==void 0&&this.isConnected&&o.hostConnected?.()}removeController(o){this._$EO?.delete(o)}_$E_(){let o=new Map,x=this.constructor.elementProperties;for(let f of x.keys())this.hasOwnProperty(f)&&(o.set(f,this[f]),delete this[f]);o.size>0&&(this._$Ep=o)}createRenderRoot(){let o=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return k0(o,this.constructor.elementStyles),o}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach((o)=>o.hostConnected?.())}enableUpdating(o){}disconnectedCallback(){this._$EO?.forEach((o)=>o.hostDisconnected?.())}attributeChangedCallback(o,x,f){this._$AK(o,f)}_$ET(o,x){let f=this.constructor.elementProperties.get(o),b=this.constructor._$Eu(o,f);if(b!==void 0&&f.reflect===!0){let a=(f.converter?.toAttribute!==void 0?f.converter:U).toAttribute(x,f.type);this._$Em=o,a==null?this.removeAttribute(b):this.setAttribute(b,a),this._$Em=null}}_$AK(o,x){let f=this.constructor,b=f._$Eh.get(o);if(b!==void 0&&this._$Em!==b){let a=f.getPropertyOptions(b),r=typeof a.converter=="function"?{fromAttribute:a.converter}:a.converter?.fromAttribute!==void 0?a.converter:U;this._$Em=b;let w=r.fromAttribute(x,a.type);this[b]=w??this._$Ej?.get(b)??w,this._$Em=null}}requestUpdate(o,x,f,b=!1,a){if(o!==void 0){let r=this.constructor;if(b===!1&&(a=this[o]),f??=r.getPropertyOptions(o),!((f.hasChanged??E)(a,x)||f.useDefault&&f.reflect&&a===this._$Ej?.get(o)&&!this.hasAttribute(r._$Eu(o,f))))return;this.C(o,x,f)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(o,x,{useDefault:f,reflect:b,wrapped:a},r){f&&!(this._$Ej??=new Map).has(o)&&(this._$Ej.set(o,r??x??this[o]),a!==!0||r!==void 0)||(this._$AL.has(o)||(this.hasUpdated||f||(x=void 0),this._$AL.set(o,x)),b===!0&&this._$Em!==o&&(this._$Eq??=new Set).add(o))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(x){Promise.reject(x)}let o=this.scheduleUpdate();return o!=null&&await o,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[b,a]of this._$Ep)this[b]=a;this._$Ep=void 0}let f=this.constructor.elementProperties;if(f.size>0)for(let[b,a]of f){let{wrapped:r}=a,w=this[b];r!==!0||this._$AL.has(b)||w===void 0||this.C(b,void 0,a,w)}}let o=!1,x=this._$AL;try{o=this.shouldUpdate(x),o?(this.willUpdate(x),this._$EO?.forEach((f)=>f.hostUpdate?.()),this.update(x)):this._$EM()}catch(f){throw o=!1,this._$EM(),f}o&&this._$AE(x)}willUpdate(o){}_$AE(o){this._$EO?.forEach((x)=>x.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(o)),this.updated(o)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(o){return!0}update(o){this._$Eq&&=this._$Eq.forEach((x)=>this._$ET(x,this[x])),this._$EM()}updated(o){}firstUpdated(o){}}B.elementStyles=[],B.shadowRootOptions={mode:"open"},B[P("elementProperties")]=new Map,B[P("finalized")]=new Map,m0?.({ReactiveElement:B}),(R.reactiveElementVersions??=[]).push("2.1.2");var s=globalThis,z0=(o)=>o,m=s.trustedTypes,J0=m?m.createPolicy("lit-html",{createHTML:(o)=>o}):void 0;var g=`lit$${Math.random().toFixed(9).slice(2)}$`,Z0="?"+g,h0=`<${Z0}>`,O=document,D=()=>O.createComment(""),c=(o)=>o===null||typeof o!="object"&&typeof o!="function",i=Array.isArray,A0=(o)=>i(o)||typeof o?.[Symbol.iterator]=="function";var H=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,K0=/-->/g,Q0=/>/g,q=RegExp(`>|[ 	
\f\r](?:([^\\s"'>=/]+)([ 	
\f\r]*=[ 	
\f\r]*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),W0=/'/g,$0=/"/g,B0=/^(?:script|style|textarea|title)$/i,e=(o)=>(x,...f)=>({_$litType$:o,strings:x,values:f}),J=e(1),g0=e(2),po=e(3),C=Symbol.for("lit-noChange"),k=Symbol.for("lit-nothing"),F0=new WeakMap,V=O.createTreeWalker(O,129);function q0(o,x){if(!i(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return J0!==void 0?J0.createHTML(x):x}var n0=(o,x)=>{let f=o.length-1,b=[],a,r=x===2?"<svg>":x===3?"<math>":"",w=H;for(let d=0;d<f;d++){let X=o[d],Z,p,Y=-1,W=0;for(;W<X.length&&(w.lastIndex=W,p=w.exec(X),p!==null);)W=w.lastIndex,w===H?p[1]==="!--"?w=K0:p[1]!==void 0?w=Q0:p[2]!==void 0?(B0.test(p[2])&&(a=RegExp("</"+p[2],"g")),w=q):p[3]!==void 0&&(w=q):w===q?p[0]===">"?(w=a??H,Y=-1):p[1]===void 0?Y=-2:(Y=w.lastIndex-p[2].length,Z=p[1],w=p[3]===void 0?q:p[3]==='"'?$0:W0):w===$0||w===W0?w=q:w===K0||w===Q0?w=H:(w=q,a=void 0);let F=w===q&&o[d+1].startsWith("/>")?" ":"";r+=w===H?X+h0:Y>=0?(b.push(Z),X.slice(0,Y)+"$lit$"+X.slice(Y)+g+F):X+g+(Y===-2?d:F)}return[q0(o,r+(o[f]||"<?>")+(x===2?"</svg>":x===3?"</math>":"")),b]};class _{constructor({strings:o,_$litType$:x},f){let b;this.parts=[];let a=0,r=0,w=o.length-1,d=this.parts,[X,Z]=n0(o,x);if(this.el=_.createElement(X,f),V.currentNode=this.el.content,x===2||x===3){let p=this.el.content.firstChild;p.replaceWith(...p.childNodes)}for(;(b=V.nextNode())!==null&&d.length<w;){if(b.nodeType===1){if(b.hasAttributes())for(let p of b.getAttributeNames())if(p.endsWith("$lit$")){let Y=Z[r++],W=b.getAttribute(p).split(g),F=/([.?@])?(.*)/.exec(Y);d.push({type:1,index:a,name:F[2],strings:W,ctor:F[1]==="."?O0:F[1]==="?"?C0:F[1]==="@"?G0:N}),b.removeAttribute(p)}else p.startsWith(g)&&(d.push({type:6,index:a}),b.removeAttribute(p));if(B0.test(b.tagName)){let p=b.textContent.split(g),Y=p.length-1;if(Y>0){b.textContent=m?m.emptyScript:"";for(let W=0;W<Y;W++)b.append(p[W],D()),V.nextNode(),d.push({type:2,index:++a});b.append(p[Y],D())}}}else if(b.nodeType===8)if(b.data===Z0)d.push({type:2,index:a});else{let p=-1;for(;(p=b.data.indexOf(g,p+1))!==-1;)d.push({type:7,index:a}),p+=g.length-1}a++}}static createElement(o,x){let f=O.createElement("template");return f.innerHTML=o,f}}function G(o,x,f=o,b){if(x===C)return x;let a=b!==void 0?f._$Co?.[b]:f._$Cl,r=c(x)?void 0:x._$litDirective$;return a?.constructor!==r&&(a?._$AO?.(!1),r===void 0?a=void 0:(a=new r(o),a._$AT(o,f,b)),b!==void 0?(f._$Co??=[])[b]=a:f._$Cl=a),a!==void 0&&(x=G(o,a._$AS(o,x.values),a,b)),x}class V0{constructor(o,x){this._$AV=[],this._$AN=void 0,this._$AD=o,this._$AM=x}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(o){let{el:{content:x},parts:f}=this._$AD,b=(o?.creationScope??O).importNode(x,!0);V.currentNode=b;let a=V.nextNode(),r=0,w=0,d=f[0];for(;d!==void 0;){if(r===d.index){let X;d.type===2?X=new M(a,a.nextSibling,this,o):d.type===1?X=new d.ctor(a,d.name,d.strings,this,o):d.type===6&&(X=new l0(a,this,o)),this._$AV.push(X),d=f[++w]}r!==d?.index&&(a=V.nextNode(),r++)}return V.currentNode=O,b}p(o){let x=0;for(let f of this._$AV)f!==void 0&&(f.strings!==void 0?(f._$AI(o,f,x),x+=f.strings.length-2):f._$AI(o[x])),x++}}class M{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(o,x,f,b){this.type=2,this._$AH=k,this._$AN=void 0,this._$AA=o,this._$AB=x,this._$AM=f,this.options=b,this._$Cv=b?.isConnected??!0}get parentNode(){let o=this._$AA.parentNode,x=this._$AM;return x!==void 0&&o?.nodeType===11&&(o=x.parentNode),o}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(o,x=this){o=G(this,o,x),c(o)?o===k||o==null||o===""?(this._$AH!==k&&this._$AR(),this._$AH=k):o!==this._$AH&&o!==C&&this._(o):o._$litType$!==void 0?this.$(o):o.nodeType!==void 0?this.T(o):A0(o)?this.k(o):this._(o)}O(o){return this._$AA.parentNode.insertBefore(o,this._$AB)}T(o){this._$AH!==o&&(this._$AR(),this._$AH=this.O(o))}_(o){this._$AH!==k&&c(this._$AH)?this._$AA.nextSibling.data=o:this.T(O.createTextNode(o)),this._$AH=o}$(o){let{values:x,_$litType$:f}=o,b=typeof f=="number"?this._$AC(o):(f.el===void 0&&(f.el=_.createElement(q0(f.h,f.h[0]),this.options)),f);if(this._$AH?._$AD===b)this._$AH.p(x);else{let a=new V0(b,this),r=a.u(this.options);a.p(x),this.T(r),this._$AH=a}}_$AC(o){let x=F0.get(o.strings);return x===void 0&&F0.set(o.strings,x=new _(o)),x}k(o){i(this._$AH)||(this._$AH=[],this._$AR());let x=this._$AH,f,b=0;for(let a of o)b===x.length?x.push(f=new M(this.O(D()),this.O(D()),this,this.options)):f=x[b],f._$AI(a),b++;b<x.length&&(this._$AR(f&&f._$AB.nextSibling,b),x.length=b)}_$AR(o=this._$AA.nextSibling,x){for(this._$AP?.(!1,!0,x);o!==this._$AB;){let f=z0(o).nextSibling;z0(o).remove(),o=f}}setConnected(o){this._$AM===void 0&&(this._$Cv=o,this._$AP?.(o))}}class N{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(o,x,f,b,a){this.type=1,this._$AH=k,this._$AN=void 0,this.element=o,this.name=x,this._$AM=b,this.options=a,f.length>2||f[0]!==""||f[1]!==""?(this._$AH=Array(f.length-1).fill(new String),this.strings=f):this._$AH=k}_$AI(o,x=this,f,b){let a=this.strings,r=!1;if(a===void 0)o=G(this,o,x,0),r=!c(o)||o!==this._$AH&&o!==C,r&&(this._$AH=o);else{let w=o,d,X;for(o=a[0],d=0;d<a.length-1;d++)X=G(this,w[f+d],x,d),X===C&&(X=this._$AH[d]),r||=!c(X)||X!==this._$AH[d],X===k?o=k:o!==k&&(o+=(X??"")+a[d+1]),this._$AH[d]=X}r&&!b&&this.j(o)}j(o){o===k?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,o??"")}}class O0 extends N{constructor(){super(...arguments),this.type=3}j(o){this.element[this.name]=o===k?void 0:o}}class C0 extends N{constructor(){super(...arguments),this.type=4}j(o){this.element.toggleAttribute(this.name,!!o&&o!==k)}}class G0 extends N{constructor(o,x,f,b,a){super(o,x,f,b,a),this.type=5}_$AI(o,x=this){if((o=G(this,o,x,0)??k)===C)return;let f=this._$AH,b=o===k&&f!==k||o.capture!==f.capture||o.once!==f.once||o.passive!==f.passive,a=o!==k&&(f===k||b);b&&this.element.removeEventListener(this.name,this,f),a&&this.element.addEventListener(this.name,this,o),this._$AH=o}handleEvent(o){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,o):this._$AH.handleEvent(o)}}class l0{constructor(o,x,f){this.element=o,this.type=6,this._$AN=void 0,this._$AM=x,this.options=f}get _$AU(){return this._$AM._$AU}_$AI(o){G(this,o)}}var u0=s.litHtmlPolyfillSupport;u0?.(_,M),(s.litHtmlVersions??=[]).push("3.3.3");var v0=(o,x,f)=>{let b=f?.renderBefore??x,a=b._$litPart$;if(a===void 0){let r=f?.renderBefore??null;b._$litPart$=a=new M(x.insertBefore(D(),r),r,void 0,f??{})}return a._$AI(o),a};var t=globalThis;class $ extends B{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let o=super.createRenderRoot();return this.renderOptions.renderBefore??=o.firstChild,o}update(o){let x=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(o),this._$Do=v0(x,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return C}}$._$litElement$=!0,$.finalized=!0,t.litElementHydrateSupport?.({LitElement:$});var s0=t.litElementPolyfillSupport;s0?.({LitElement:$});(t.litElementVersions??=[]).push("4.2.2");var i0={attribute:!0,type:String,converter:U,reflect:!1,hasChanged:E},e0=(o=i0,x,f)=>{let{kind:b,metadata:a}=f,r=globalThis.litPropertyMetadata.get(a);if(r===void 0&&globalThis.litPropertyMetadata.set(a,r=new Map),b==="setter"&&((o=Object.create(o)).wrapped=!0),r.set(f.name,o),b==="accessor"){let{name:w}=f;return{set(d){let X=x.get.call(this);x.set.call(this,d),this.requestUpdate(w,X,o,!0,d)},init(d){return d!==void 0&&this.C(w,void 0,o,d),d}}}if(b==="setter"){let{name:w}=f;return function(d){let X=this[w];x.call(this,d),this.requestUpdate(w,X,o,!0,d)}}throw Error("Unsupported decorator location: "+b)};function K(o){return(x,f)=>typeof f=="object"?e0(o,x,f):((b,a,r)=>{let w=a.hasOwnProperty(r);return a.constructor.createProperty(r,b),w?Object.getOwnPropertyDescriptor(a,r):void 0})(o,x,f)}function I(o){return K({...o,state:!0,attribute:!1})}var P0="0.1.0",j="storz-bickel-card",A="storz-bickel-card-editor",o0="sb-temp-dial",U0="storz_bickel",H0=[175,185,195];var D0=100,b0=85,x0=135,c0=270,S=100;function f0(o,x=b0){let f=o*Math.PI/180;return{x:D0+x*Math.cos(f),y:D0+x*Math.sin(f)}}function t0(o,x,f){return Math.min(f,Math.max(x,o))}class a0 extends ${constructor(){super(...arguments);this.min=40;this.max=230;this.unit="°C";this.active=!1;this.heating=!1;this.disabled=!1}fraction(o){if(this.max<=this.min)return 0;return t0((o-this.min)/(this.max-this.min),0,1)}get mode(){if(!this.active||this.disabled)return"off";if(this.current!==void 0&&this.target!==void 0){if(this.current>=this.target-1)return"ready"}return"heating"}emitStep(o){this.dispatchEvent(new CustomEvent("dial-step",{detail:{direction:o},bubbles:!0,composed:!0}))}render(){let o=f0(x0),x=f0(x0+c0),f=`M ${o.x} ${o.y} A ${b0} ${b0} 0 1 1 ${x.x} ${x.y}`,b=this.current===void 0?0:this.fraction(this.current),a=this.target===void 0||this.disabled?void 0:f0(x0+c0*this.fraction(this.target));return J`
      <div class="dial ${this.mode} ${this.disabled?"disabled":""}">
        <svg viewBox="0 0 200 200" role="img" aria-label="Temperature dial">
          <path class="track" d=${f} pathLength=${S} />
          <path
            class="fill"
            d=${f}
            pathLength=${S}
            stroke-dasharray="${S} ${S}"
            stroke-dashoffset=${S*(1-b)}
          />
          ${a?g0`<circle class="marker" cx=${a.x} cy=${a.y} r="5" />`:k}
        </svg>
        <div class="readout">
          <span class="current"
            >${this.current===void 0||this.disabled?"—":Math.round(this.current)}<span
              class="unit"
              >${this.unit}</span
            ></span
          >
          ${this.active&&!this.disabled&&this.target!==void 0?J`<span class="target">➜ ${Math.round(this.target)}${this.unit}</span>`:k}
        </div>
        <button
          class="step minus"
          aria-label="Decrease target temperature"
          ?disabled=${this.disabled}
          @click=${()=>this.emitStep(-1)}
        >
          −
        </button>
        <button
          class="step plus"
          aria-label="Increase target temperature"
          ?disabled=${this.disabled}
          @click=${()=>this.emitStep(1)}
        >
          +
        </button>
      </div>
    `}static styles=v`
    :host {
      display: block;
      --sb-dial-off: var(--sb-color-off, var(--disabled-text-color, #9e9e9e));
      --sb-dial-heat: var(--sb-color-heating, #ff9800);
      --sb-dial-ready: var(--sb-color-ready, #4caf50);
    }

    .dial {
      position: relative;
      width: min(240px, 100%);
      aspect-ratio: 1;
      margin: 0 auto;
      --dial-color: var(--sb-dial-off);
    }

    .dial.heating {
      --dial-color: var(--sb-dial-heat);
    }

    .dial.ready {
      --dial-color: var(--sb-dial-ready);
    }

    svg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
    }

    path {
      fill: none;
      stroke-width: 6;
      stroke-linecap: round;
    }

    .track {
      stroke: var(--divider-color, rgba(127, 127, 127, 0.3));
    }

    .fill {
      stroke: var(--dial-color);
      transition:
        stroke-dashoffset 0.6s ease,
        stroke 0.6s ease;
    }

    .marker {
      fill: var(--dial-color);
      transition: fill 0.6s ease;
    }

    .dial.heating svg {
      animation: sb-breathe 3s ease-in-out infinite;
    }

    @keyframes sb-breathe {
      0%,
      100% {
        filter: drop-shadow(0 0 2px var(--dial-color));
      }
      50% {
        filter: drop-shadow(0 0 10px var(--dial-color));
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .dial.heating svg {
        animation: none;
      }
      .fill,
      .marker {
        transition: none;
      }
    }

    .readout {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 2px;
      pointer-events: none;
    }

    .current {
      font-size: clamp(2.2rem, 18cqw, 3.2rem);
      font-weight: 300;
      font-variant-numeric: tabular-nums;
      line-height: 1;
      color: var(--primary-text-color);
    }

    .dial.disabled .current {
      color: var(--disabled-text-color, #9e9e9e);
    }

    .unit {
      font-size: 0.4em;
      font-weight: 400;
      color: var(--secondary-text-color);
      vertical-align: super;
    }

    .target {
      font-size: 1rem;
      font-variant-numeric: tabular-nums;
      color: var(--secondary-text-color);
    }

    .step {
      position: absolute;
      bottom: 2%;
      width: 44px;
      height: 44px;
      border: none;
      border-radius: 50%;
      background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
      color: var(--primary-text-color);
      font-size: 1.4rem;
      line-height: 1;
      cursor: pointer;
      transition:
        transform 0.1s ease,
        background 0.2s ease;
    }

    .step:active {
      transform: scale(0.92);
    }

    .step:disabled {
      cursor: not-allowed;
      opacity: 0.4;
    }

    .minus {
      left: 18%;
    }

    .plus {
      right: 18%;
    }
  `}z([K({type:Number})],a0.prototype,"current",void 0),z([K({type:Number})],a0.prototype,"target",void 0),z([K({type:Number})],a0.prototype,"min",void 0),z([K({type:Number})],a0.prototype,"max",void 0),z([K()],a0.prototype,"unit",void 0),z([K({type:Boolean})],a0.prototype,"active",void 0),z([K({type:Boolean})],a0.prototype,"heating",void 0),z([K({type:Boolean})],a0.prototype,"disabled",void 0);var _0=["preset_1","preset_2","preset_3"],oo=[{name:"device",required:!0,selector:{device:{integration:"storz_bickel"}}},{name:"name",selector:{text:{}}},..._0.map((o)=>({name:o,selector:{number:{mode:"box",step:1}}}))],xo={device:"Device",name:"Name (optional)",preset_1:"Preset 1",preset_2:"Preset 2",preset_3:"Preset 3"};class r0 extends ${setConfig(o){this.config=o}get formData(){let o=this.config?.presets??[];return{device:this.config?.device??"",name:this.config?.name,preset_1:o[0],preset_2:o[1],preset_3:o[2]}}handleValueChanged(o){if(o.stopPropagation(),!this.config)return;let x=o.detail.value,f=_0.map((a)=>x[a]).filter((a)=>typeof a==="number"&&Number.isFinite(a)),b={type:this.config.type,device:typeof x.device==="string"?x.device:""};if(typeof x.name==="string"&&x.name!=="")b.name=x.name;if(f.length>0)b.presets=f;this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:b},bubbles:!0,composed:!0}))}render(){if(!this.config)return k;return J`
      <ha-form
        .hass=${this.hass}
        .data=${this.formData}
        .schema=${oo}
        .computeLabel=${(o)=>xo[o.name]??o.name}
        @value-changed=${this.handleValueChanged}
      ></ha-form>
    `}}z([K({attribute:!1})],r0.prototype,"hass",void 0),z([I()],r0.prototype,"config",void 0);function M0(o,x){let f=Object.values(o.entities).filter((a)=>a.device_id===x&&a.platform===U0),b=(a,r)=>f.find((w)=>w.entity_id.startsWith(`${a}.`)&&w.translation_key===r)?.entity_id;return{climate:b("climate","heater"),pump:b("switch","pump"),vibration:b("switch","vibration"),autoShutoffEnabled:b("switch","auto_shutoff_enabled"),battery:b("sensor","battery"),connection:b("binary_sensor","connection"),ledBrightness:b("number","led_brightness"),autoShutoffMinutes:b("number","auto_shutoff_minutes"),boostTemperature:b("number","boost_temperature")}}var N0=v`
  :host {
    --sb-heat: var(--sb-color-heating, #ff9800);
    --sb-ready: var(--sb-color-ready, #4caf50);
  }

  ha-card {
    padding: 16px;
  }

  .body {
    display: flex;
    flex-direction: column;
    gap: 14px;
    transition: opacity 0.3s ease;
  }

  .body.disconnected .controls {
    opacity: 0.45;
    pointer-events: none;
  }

  .controls {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  /* ---- header ---------------------------------------------------------- */

  .header {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .name {
    flex: 1;
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--primary-text-color);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex: none;
  }

  .dot.connected {
    background: var(--sb-ready);
    box-shadow: 0 0 5px var(--sb-ready);
  }

  .dot.disconnected {
    background: var(--error-color, #f44336);
    animation: sb-blink 1.6s ease-in-out infinite;
  }

  @keyframes sb-blink {
    50% {
      opacity: 0.35;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .dot.disconnected {
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

  /* ---- heat pill ------------------------------------------------------- */

  .heat {
    align-self: center;
    min-width: 60%;
    padding: 12px 24px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 28px;
    background: transparent;
    color: var(--primary-text-color);
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    cursor: pointer;
    transition:
      background 0.25s ease,
      color 0.25s ease,
      box-shadow 0.25s ease,
      transform 0.1s ease;
  }

  .heat:active {
    transform: scale(0.97);
  }

  .heat.on {
    border-color: transparent;
    background: var(--sb-heat);
    color: #fff;
    box-shadow: 0 0 14px color-mix(in srgb, var(--sb-heat) 60%, transparent);
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
    animation: sb-fade-in 0.3s ease backwards;
    transition:
      background 0.2s ease,
      color 0.2s ease,
      border-color 0.2s ease,
      transform 0.1s ease;
  }

  .preset:nth-child(2) {
    animation-delay: 0.05s;
  }

  .preset:nth-child(3) {
    animation-delay: 0.1s;
  }

  .preset:nth-child(4) {
    animation-delay: 0.15s;
  }

  .preset:active {
    transform: scale(0.95);
  }

  .preset.active {
    border-color: transparent;
    background: var(--sb-heat);
    color: #fff;
  }

  @keyframes sb-fade-in {
    from {
      opacity: 0;
      transform: translateY(4px);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .preset {
      animation: none;
    }
  }

  /* ---- pump bar -------------------------------------------------------- */

  .pump {
    position: relative;
    overflow: hidden;
    width: 100%;
    padding: 13px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 14px;
    background: transparent;
    color: var(--primary-text-color);
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    cursor: pointer;
    transition:
      background 0.25s ease,
      color 0.25s ease,
      transform 0.1s ease;
  }

  .pump:active {
    transform: scale(0.98);
  }

  .pump.on {
    border-color: transparent;
    background: var(--primary-color, #03a9f4);
    color: #fff;
  }

  .pump.on::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
      105deg,
      transparent 20%,
      rgba(255, 255, 255, 0.25) 50%,
      transparent 80%
    );
    transform: translateX(-100%);
    animation: sb-airflow 1.8s linear infinite;
  }

  @keyframes sb-airflow {
    to {
      transform: translateX(100%);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .pump.on::after {
      animation: none;
    }
  }

  /* ---- status + settings ----------------------------------------------- */

  .status {
    display: flex;
    justify-content: center;
    gap: 6px;
    font-size: 0.85rem;
    color: var(--secondary-text-color);
  }

  details {
    border-top: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
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
`;function Q(o){let x=typeof o==="string"?Number(o):o;return typeof x==="number"&&Number.isFinite(x)?x:void 0}function w0(o){return{currentTemperature:Q(o.attributes.current_temperature),targetTemperature:Q(o.attributes.temperature),minTemp:Q(o.attributes.min_temp)??40,maxTemp:Q(o.attributes.max_temp)??230,targetTempStep:Q(o.attributes.target_temp_step)??1,hvacAction:typeof o.attributes.hvac_action==="string"?o.attributes.hvac_action:void 0}}class I0 extends ${debounceMs=500;debounceTimer;static styles=N0;static getConfigElement(){return document.createElement(A)}static getStubConfig(o){return{device:(o?Object.values(o.entities).find((f)=>f.platform==="storz_bickel"&&f.device_id):void 0)?.device_id??"",presets:[...H0]}}setConfig(o){if(!o.device)throw Error("storz-bickel-card: 'device' is required (a Storz & Bickel device)");this.config=o}getCardSize(){return 5}getGridOptions(){return{columns:12,rows:8,min_columns:6,min_rows:6}}get entityIds(){if(!this.hass||!this.config)return{};return M0(this.hass,this.config.device)}entityState(o){return o?this.hass?.states[o]:void 0}callService(o,x,f){this.hass?.callService(o,x,f)}setTargetTemperature(o,x){this.callService("climate","set_temperature",{entity_id:o,temperature:x})}handleDialStep(o,x){let f=w0(x),b=this.pendingTarget??f.targetTemperature??f.minTemp,a=Math.min(f.maxTemp,Math.max(f.minTemp,b+o*f.targetTempStep));this.pendingTarget=a,clearTimeout(this.debounceTimer),this.debounceTimer=setTimeout(()=>{this.pendingTarget=void 0,this.setTargetTemperature(x.entity_id,a)},this.debounceMs)}handlePreset(o,x){let f=w0(x),b=Math.min(f.maxTemp,Math.max(f.minTemp,o));clearTimeout(this.debounceTimer),this.pendingTarget=b,this.setTargetTemperature(x.entity_id,b)}toggleHeat(o){this.callService("climate","set_hvac_mode",{entity_id:o.entity_id,hvac_mode:o.state==="heat"?"off":"heat"})}toggleSwitch(o){this.callService("switch",o.state==="on"?"turn_off":"turn_on",{entity_id:o.entity_id})}setNumber(o,x){this.callService("number","set_value",{entity_id:o,value:x})}render(){if(!this.hass||!this.config)return k;let o=this.entityIds,x=this.entityState(o.climate);if(!x)return J`<ha-card><div class="body">Device entities not found.</div></ha-card>`;let f=w0(x),b=this.entityState(o.connection),a=b?b.state==="on":!0,r=x.state==="heat",w=f.hvacAction==="heating",d=this.pendingTarget??f.targetTemperature,X=this.entityState(o.battery),Z=this.entityState(o.pump),p=this.hass.config.unit_system.temperature,Y=this.hass.devices[this.config.device],W=this.config.name??Y?.name_by_user??Y?.name??"Storz & Bickel",F=this.config.presets??[];return J`
      <ha-card>
        <div class="body ${a?"":"disconnected"}">
          <div class="header">
            <span class="name">${W}</span>
            ${X&&Q(X.state)!==void 0?J`<span class="battery">🔋 ${Math.round(Q(X.state)??0)}%</span>`:k}
            <span
              class="dot ${a?"connected":"disconnected"}"
              title=${a?"Connected":"Disconnected"}
            ></span>
          </div>
          <div class="controls">
            <sb-temp-dial
              .current=${f.currentTemperature}
              .target=${d}
              .min=${f.minTemp}
              .max=${f.maxTemp}
              .unit=${p}
              ?active=${r}
              ?heating=${w}
              ?disabled=${!a}
              @dial-step=${(l)=>this.handleDialStep(l.detail.direction,x)}
            ></sb-temp-dial>
            <button class="heat ${r?"on":""}" @click=${()=>this.toggleHeat(x)}>
              ⏻ Heat
            </button>
            ${F.length>0?J`
                  <div class="presets">
                    ${F.map((l)=>J`
                        <button
                          class="preset ${d!==void 0&&Math.round(d)===Math.round(l)?"active":""}"
                          @click=${()=>this.handlePreset(l,x)}
                        >
                          ${l}${p}
                        </button>
                      `)}
                  </div>
                `:k}
            ${Z?J`
                  <button
                    class="pump ${Z.state==="on"?"on":""}"
                    @click=${()=>this.toggleSwitch(Z)}
                  >
                    ${Z.state==="on"?"≋ Pump ≋":"Pump"}
                  </button>
                `:k}
            ${this.renderStatus(o)} ${this.renderSettings(o)}
          </div>
        </div>
      </ha-card>
    `}renderStatus(o){let x=this.entityState(o.autoShutoffEnabled),f=this.entityState(o.autoShutoffMinutes);if(!x&&!f)return k;let b=x?x.state==="on":!0,a=f?Q(f.state):void 0;return J`
      <div class="status">
        <span>Auto shutoff:</span>
        <span>
          ${b?a!==void 0?`${a} min`:"on":"off"}
        </span>
      </div>
    `}renderSettings(o){let x=this.entityState(o.ledBrightness),f=this.entityState(o.autoShutoffMinutes),b=this.entityState(o.boostTemperature),a=this.entityState(o.vibration);if(!x&&!f&&!b&&!a)return k;return J`
      <details class="settings">
        <summary>Settings</summary>
        ${x?this.renderNumberRow("LED brightness",x,"%"):k}
        ${f?this.renderNumberRow("Auto shutoff",f," min"):k}
        ${b?this.renderNumberRow("Boost",b,"°"):k}
        ${a?J`
              <div class="row">
                <label for="vibration">Vibration</label>
                <input
                  id="vibration"
                  type="checkbox"
                  .checked=${a.state==="on"}
                  @change=${()=>this.toggleSwitch(a)}
                />
              </div>
            `:k}
      </details>
    `}renderNumberRow(o,x,f){let b=Q(x.state),a=Q(x.attributes.min)??0,r=Q(x.attributes.max)??100,w=Q(x.attributes.step)??1,d=x.entity_id.replaceAll(".","-");return J`
      <div class="row">
        <label for=${d}>${o}</label>
        <input
          id=${d}
          type="range"
          min=${a}
          max=${r}
          step=${w}
          .value=${String(b??a)}
          @change=${(X)=>this.setNumber(x.entity_id,Number(X.target.value))}
        />
        <span class="value">${b??"—"}${f}</span>
      </div>
    `}}z([K({attribute:!1})],I0.prototype,"hass",void 0),z([I()],I0.prototype,"config",void 0),z([I()],I0.prototype,"pendingTarget",void 0);if(!customElements.get(o0))customElements.define(o0,a0);if(!customElements.get(j))customElements.define(j,I0);if(!customElements.get(A))customElements.define(A,r0);window.customCards=window.customCards??[];if(!window.customCards.some((o)=>o.type===j))window.customCards.push({type:j,name:"Storz & Bickel Card",description:"Controls for Storz & Bickel vaporizers (Volcano, Venty, Veazy, Crafty).",preview:!0,documentationURL:"https://github.com/nredd/hacs-storz-bickel"});console.info(`%c STORZ-BICKEL-CARD %c v${P0} `,"background: #ff9800; color: #fff; font-weight: 600; border-radius: 3px 0 0 3px;","background: #424242; color: #fff; border-radius: 0 3px 3px 0;");export{I0 as StorzBickelCard};
