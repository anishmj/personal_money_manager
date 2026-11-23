(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const e of document.querySelectorAll('link[rel="modulepreload"]'))s(e);new MutationObserver(e=>{for(const o of e)if(o.type==="childList")for(const i of o.addedNodes)i.tagName==="LINK"&&i.rel==="modulepreload"&&s(i)}).observe(document,{childList:!0,subtree:!0});function a(e){const o={};return e.integrity&&(o.integrity=e.integrity),e.referrerPolicy&&(o.referrerPolicy=e.referrerPolicy),e.crossOrigin==="use-credentials"?o.credentials="include":e.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function s(e){if(e.ep)return;e.ep=!0;const o=a(e);fetch(e.href,o)}})();const m=document.getElementById("root"),c=document.createElement("label"),d=document.createElement("span"),r=document.createElement("select"),u=document.createElement("style"),f="streamlit:render";u.textContent=`
  :root { color-scheme: light; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  * { box-sizing: border-box; }
  body { margin: 0; color: #172b4d; }
  label { display: block; margin: 0 0 0.35rem; font-size: 0.875rem; line-height: 1.3; }
  select {
    display: block; width: 100%; min-height: 48px; padding: 0.65rem 2.4rem 0.65rem 0.8rem;
    border: 1px solid #cbd5e1; border-radius: 10px; background: #fff; color: #1e293b;
    font: inherit; font-size: 1rem;
  }
  select:focus { outline: 2px solid #818cf8; outline-offset: 1px; }
  select:disabled { background: #f1f5f9; color: #64748b; }
`;c.append(d,r);m.append(u,c);function p(n){const{args:t,disabled:a}=n.data;d.textContent=t.label,r.setAttribute("aria-label",t.label),r.replaceChildren(),t.options.forEach((e,o)=>{const i=document.createElement("option");i.value=String(o),i.textContent=e,r.appendChild(i)});const s=t.values.findIndex(e=>Object.is(e,t.selected_value));r.value=String(Number.isInteger(s)&&s>=0&&s<t.options.length?s:0),r.disabled=!!a,r.onchange=()=>l("streamlit:setComponentValue",{value:t.values[Number(r.value)],dataType:"json"}),l("streamlit:setFrameHeight",{height:86})}function l(n,t){window.parent.postMessage({isStreamlitMessage:!0,type:n,...t},"*")}window.addEventListener("message",n=>{var t;((t=n.data)==null?void 0:t.type)===f&&p(n)});l("streamlit:componentReady",{apiVersion:1});l("streamlit:setFrameHeight",{height:86});
