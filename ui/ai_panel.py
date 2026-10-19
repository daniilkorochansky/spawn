# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------------------------------------------
#   Spawn — A fast and modern, open-source IDE with a native user interface for SA-MP and open.mp server development.
#   Copyright (C) 2026  Daniil Korochansky
#
#   This file is part of Spawn.
#
#   Spawn is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Spawn is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Spawn.  If not, see <https://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------------------------------------------------

"""Dockable right-side tools panel with Spawn AI as its first tab."""
from __future__ import annotations

import json
import threading
import wx
import wx.aui
import wx.html2

from ai.lm_studio import AIClientError
from ai.service import AIService


HTML_PAGE = r'''<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{color-scheme:dark;--bg:#1e1e1e;--panel:#252526;--panel2:#2d2d30;--border:#3c3c3c;--text:#d4d4d4;--muted:#999;--accent:#0e639c;--accent-hover:#1177bb;--code:#151515;}
*{box-sizing:border-box}html,body{height:100%;margin:0}body{background:var(--bg);color:var(--text);font:13px "Segoe UI","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji",sans-serif;height:100vh;display:flex;flex-direction:column;overflow:hidden}
#status-dot{display:inline-block;width:8px;height:8px;flex:none;border-radius:50%;background:#d4aa00;cursor:help}#status-dot[title]{position:relative}.meta{display:flex;align-items:center;gap:7px;min-width:0}.model-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--muted);font-size:10px}.messages{position:relative;padding:14px 12px;overflow:auto;flex:1;scroll-behavior:auto}.message{margin:0 0 18px;line-height:1.55;overflow-wrap:anywhere;font-family:"Segoe UI","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji",sans-serif}.role{font-size:11px;color:var(--muted);margin-bottom:6px;font-weight:600}.user .body{background:#2a2d2e;border:1px solid var(--border);border-radius:8px;padding:10px 11px}.body p{margin:0 0 9px}.body p:last-child{margin-bottom:0}.body h1,.body h2,.body h3{font-weight:600;margin:14px 0 7px;line-height:1.35}.body h1{font-size:17px}.body h2{font-size:15px}.body h3{font-size:13px}.body ul,.body ol{padding-left:21px}.body li{margin:3px 0}.body code{font:12px Consolas,monospace;background:var(--panel2);padding:1px 4px;border-radius:3px}.code-block{margin:9px 0;max-width:100%;min-width:0;border:1px solid var(--border);border-radius:7px;overflow:hidden;background:var(--code)}.code-head{display:flex;align-items:center;padding:5px 9px;background:var(--panel);border-bottom:1px solid var(--border);font-size:10px;color:var(--muted)}.code-head button{margin-left:auto;background:transparent;border:1px solid var(--border);color:var(--text);padding:3px 7px;font-size:10px}.body pre{display:block;max-width:100%;min-width:0;white-space:pre;overflow-x:auto;overflow-y:hidden;margin:0;padding:11px;background:var(--code);font:12px/1.5 Consolas,monospace}.body blockquote{border-left:3px solid var(--border);padding-left:10px;color:var(--muted)}.body a{color:var(--accent-hover);text-decoration:underline}.body .md-hr{border:0;border-top:1px solid var(--border);margin:14px 0}.body table{border-collapse:collapse;width:100%;margin:10px 0;display:block;overflow-x:auto}.body th,.body td{border:1px solid var(--border);padding:6px 8px;text-align:left}.body th{background:var(--panel2);font-weight:600}.body del{opacity:.8}.body{font-family:"Segoe UI","Segoe UI Symbol","Segoe UI Emoji","Noto Sans",sans-serif;overflow-wrap:anywhere}.body pre code{display:block!important;background:transparent!important;color:inherit;padding:0;border-radius:0;white-space:pre}.thinking{display:inline-flex;align-items:center;gap:5px;color:var(--muted)}.thinking i{width:5px;height:5px;border-radius:50%;background:var(--muted);animation:pulse 1.1s infinite alternate}.thinking i:nth-child(2){animation-delay:.2s}.thinking i:nth-child(3){animation-delay:.4s}@keyframes pulse{to{opacity:.25;transform:translateY(-2px)}}footer{padding:10px;border-top:1px solid var(--border);background:var(--panel)}.composer{background:var(--bg);border:1px solid #4a4a4a;border-radius:8px;padding:8px}.composer:focus-within{border-color:var(--accent)}textarea{width:100%;height:64px;resize:vertical;color:var(--text);background:transparent;border:0;padding:3px;font:13px/1.45 "Segoe UI",sans-serif;outline:none}.actions{display:flex;align-items:center;justify-content:space-between;margin-top:7px;gap:8px}button{border:0;border-radius:5px;background:var(--accent);color:white;padding:7px 13px;cursor:pointer;font:inherit;font-family:"Segoe UI","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji",sans-serif}button:hover:not(:disabled){background:var(--accent-hover)}button:disabled{opacity:.5;cursor:default}.secondary{background:transparent;color:var(--muted);padding:6px}.hint{color:var(--muted);font-size:10px}
#welcome{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;padding:28px;color:var(--text);pointer-events:none}
#welcome-inner{max-width:270px}.copy-toast{position:fixed;left:50%;bottom:94px;transform:translateX(-50%);padding:7px 12px;border-radius:6px;background:var(--panel2);border:1px solid var(--border);color:var(--text);font-size:12px;z-index:999;box-shadow:0 3px 12px #0002;display:none}.copy-toast.visible{display:block}
#welcome-mark{width:42px;height:42px;border-radius:13px;margin:0 auto 14px;display:flex;align-items:center;justify-content:center;background:var(--panel2);border:1px solid var(--border);font-weight:700;font-size:20px}
#welcome h2{font-size:17px;margin:0 0 8px;font-weight:600}
#welcome p{font-size:12px;line-height:1.6;margin:0;color:var(--muted)}
.actions-left,.actions-right{display:flex;align-items:center;gap:5px;min-width:0}
.icon-button{width:30px;height:30px;padding:6px;background:transparent;color:var(--muted);border:1px solid transparent}
.icon-button:hover:not(:disabled){background:var(--panel2);color:var(--text);border-color:var(--border)}
button svg{width:16px;height:16px;display:block;fill:currentColor}
#send{width:34px;height:34px;min-width:34px;min-height:34px;padding:0;border-radius:50%;display:inline-flex;align-items:center;justify-content:center}#send svg{width:16px;height:16px;display:block}#send:not([data-stopping='true']) svg{transform:translate(0.5px,-0.5px)}
body.light{
 --bg:#ffffff;--panel:#f5f5f5;--panel2:#e9e9e9;--border:#d4d4d4;
 --text:#242424;--muted:#666;--accent:#0969a8;--accent-hover:#075987;--code:#f2f2f2;
 color-scheme:light;
}
body.light .user .body{background:#f1f3f5;border-color:#e0e0e0}
body.light .composer{background:#fff;border-color:#d0d0d0}body.light .composer:focus-within{border-color:var(--accent);box-shadow:none}
body.light textarea{color:var(--text)}
body.light .body code{background:#e8e8e8}body.light .body pre code{background:transparent!important;color:inherit;padding:0;border-radius:0}
body.light .code-head{background:#f5f5f5;color:#555}body.light .code-head button{background:var(--accent);color:#fff;border-color:var(--accent)}body.light .code-head button:hover{background:var(--accent-hover);border-color:var(--accent-hover);color:#fff}
body.light .body pre{background:#f7f7f7;color:#242424}
body.light #welcome-mark{background:#f1f1f1}
body.light .icon-button:hover:not(:disabled){background:#e9e9e9;color:#222;border-color:#d0d0d0}

</style></head><body>
<main class="messages" id="messages"><div id="welcome"><div id="welcome-inner"><div id="welcome-mark">S</div><h2>How can I help?</h2><p>Ask a question or explore an idea. Your conversation will appear here.</p></div></div></main>
<div id="copy-toast" class="copy-toast" role="status" aria-live="polite">Copied to clipboard</div>
<footer><div class="composer"><textarea id="prompt" placeholder="Ask anything... (Enter to send, Shift+Enter for newline)" aria-label="Message"></textarea><div class="actions"><div class="actions-left"><button class="icon-button" id="theme" title="Switch to light theme" aria-label="Switch theme"><svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" fill="currentColor"><path d="M8 1.00195C6.61553 1.00195 5.26216 1.4125 4.11101 2.18167C2.95987 2.95084 2.06266 4.04409 1.53285 5.32317C1.00303 6.60225 .86441 8.00972 1.13451 9.36759C1.4046 10.7255 2.07129 11.9727 3.05026 12.9517C4.02922 13.9307 5.27651 14.5974 6.63437 14.8675C7.99224 15.1375 9.3997 14.9989 10.6788 14.4691C11.9579 13.9393 13.0511 13.0421 13.8203 11.8909C14.5895 10.7398 15 9.38642 15 8.00195C15 6.14544 14.2625 4.36496 12.9498 3.05221C11.637 1.73945 9.85652 1.00195 8 1.00195ZM8 14.002V2.00195C9.5913 2.00195 11.1174 2.63409 12.2426 3.75931C13.3679 4.88453 14 6.41065 14 8.00195C14 9.59325 13.3679 11.1194 12.2426 12.2446C11.1174 13.3694 9.5913 14.002 8 14.002Z"/></svg></button><button class="icon-button" id="clear" title="Clear chat" aria-label="Clear chat"><svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" fill="currentColor"><path d="M14.5 6C14.5 5.6 14.344 5.223 14.061 4.939L11.062 1.939C10.496 1.372 9.504 1.372 8.94 1.939L1.439 9.439C1.156 9.722 1 10.099 1 10.5C1 10.901 1.156 11.277 1.439 11.561L3.439 13.561C3.722 13.844 4.099 14 4.5 14H11.5C11.776 14 12 13.776 12 13.5C12 13.224 11.776 13 11.5 13H8.121L14.06 7.061C14.343 6.778 14.499 6.401 14.499 6H14.5ZM4.146 12.854L2.146 10.854C2.051 10.759 2 10.634 2 10.5C2 10.366 2.052 10.241 2.146 10.146L4.293 8L8 11.707L6.707 13H4.5C4.366 13 4.241 12.948 4.146 12.854ZM13.354 6.354L8.708 11L5.001 7.293L9.648 2.646C9.742 2.552 9.867 2.5 10.001 2.5C10.135 2.5 10.26 2.552 10.355 2.646L13.355 5.646C13.45 5.741 13.501 5.866 13.501 6C13.501 6.134 13.448 6.259 13.354 6.354Z"/></svg></button><span id="status-dot" title="Checking connection..." aria-label="Connection status"></span><span class="hint model-name" id="hint">Checking connection...</span></div><div class="actions-right"><button id="send" title="Send message" aria-label="Send message"><svg id="send-icon" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" fill="currentColor"><path d="M1.17683 1.11898C1.32953 0.989634 1.54464 0.963786 1.72363 1.05328L14.7236 7.55328C14.893 7.63797 15 7.8111 15 8.00049C15 8.18987 14.893 8.36301 14.7236 8.4477L1.72363 14.9477C1.54464 15.0372 1.32953 15.0113 1.17683 14.882C1.02414 14.7526 .96328 14.5447 1.02213 14.3534L2.97688 8.00049L1.02213 1.64754C.96328 1.45627 1.02414 1.24833 1.17683 1.11898ZM3.8693 8.50049L2.32155 13.5307L13.382 8.00049L2.32155 2.47027L3.8693 7.50049H9.50001C9.77615 7.50049 10 7.72435 10 8.00049C10 8.27663 9.77615 8.50049 9.50001 8.50049H3.8693Z"/></svg></button></div></div></div></footer>
<script>
const messages=[];let busy=false;let stopping=false;let aiEnabled=true;let streamUpdatePending=false;let latestStreamText='';let streamUpdateTimer=null;
function post(data){if(window.wx&&window.wx.postMessage)window.wx.postMessage(JSON.stringify(data));}
function addMessage(role,text){messages.push({role,content:text});render();}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function markdown(text){
 // Escape raw HTML first: model output is untrusted text.
 let source=String(text==null?'':text).replace(/\r\n?/g,'\n');
 const codeBlocks=[];
 source=source.replace(/```([^\n`]*)\n([\s\S]*?)```/g,(_,lang,code)=>{
   const id=codeBlocks.length;
   codeBlocks.push({lang:(lang||'code').trim(),code:code.replace(/\n$/,'')});
   return '\n@@CODEBLOCK'+id+'@@\n';
 });
 let s=escapeHtml(source);

 // Inline Markdown. Process links only after escaping and allow safe URL schemes.
 function inline(value){
   let out=value;
   out=out.replace(/`([^`\n]+)`/g,'<code>$1</code>');
   out=out.replace(/!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)/g,
     '<span class="md-image-alt">[Image: $1]</span>');
   out=out.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)(?:\s+"([^"]*)")?\)/g,
     '<a href="$2" title="$3" target="_blank" rel="noopener noreferrer">$1</a>');
   out=out.replace(/\*\*\*(.+?)\*\*\*/g,'<strong><em>$1</em></strong>');
   out=out.replace(/___(.+?)___/g,'<strong><em>$1</em></strong>');
   out=out.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
   out=out.replace(/__(.+?)__/g,'<strong>$1</strong>');
   out=out.replace(/(?<!\*)\*([^*\n]+)\*(?!\*)/g,'<em>$1</em>');
   out=out.replace(/(?<!_)_([^_\n]+)_(?!_)/g,'<em>$1</em>');
   out=out.replace(/~~(.+?)~~/g,'<del>$1</del>');
   return out;
 }
 const lines=s.split('\n');
 const out=[];
 let paragraph=[];
 function flushParagraph(){
   if(paragraph.length){out.push('<p>'+paragraph.map(inline).join('<br>')+'</p>');paragraph=[];}
 }
 function isSpecial(line){
   return /^\s*(?:@@CODEBLOCK\d+@@|#{1,6}\s+|(?:[-*_]\s*){3,}$|>\s?|[-+*]\s+|\d+[.)]\s+|\|.*\|)\s*$/.test(line)
     || /^\s*@@CODEBLOCK\d+@@\s*$/.test(line);
 }
 function parseTable(tableLines){
   const rows=tableLines.map(line=>line.trim().replace(/^\||\|$/g,'').split('|').map(c=>c.trim()));
   if(rows.length<2 || !rows[1].every(c=>/^:?-{3,}:?$/.test(c))) return null;
   const heads=rows[0];
   let html='<table><thead><tr>'+heads.map(c=>'<th>'+inline(c)+'</th>').join('')+'</tr></thead><tbody>';
   for(const row of rows.slice(2)){
     html+='<tr>'+heads.map((_,i)=>'<td>'+inline(row[i]||'')+'</td>').join('')+'</tr>';
   }
   return html+'</tbody></table>';
 }
 for(let i=0;i<lines.length;){
   const line=lines[i];
   if(!line.trim()){flushParagraph();i++;continue;}
   const codeMatch=line.match(/^\s*@@CODEBLOCK(\d+)@@\s*$/);
   if(codeMatch){
     flushParagraph();
     const b=codeBlocks[Number(codeMatch[1])];
     if(b) out.push('<div class="code-block"><div class="code-head">'+escapeHtml(b.lang)+'<button data-copy="'+encodeURIComponent(b.code)+'">Copy</button></div><pre><code>'+escapeHtml(b.code)+'</code></pre></div>');
     i++;continue;
   }
   if(/^\s*(?:---+|\*\*\*+|___+)\s*$/.test(line)){
     flushParagraph();out.push('<hr class="md-hr">');i++;continue;
   }
   const heading=line.match(/^\s*(#{1,6})\s+(.+?)\s*#*\s*$/);
   if(heading){
     flushParagraph();const level=heading[1].length;
     out.push('<h'+level+'>'+inline(heading[2])+'</h'+level+'>');i++;continue;
   }
   if(/^\s*\|.*\|\s*$/.test(line)){
     let tableLines=[];
     while(i<lines.length && /^\s*\|.*\|\s*$/.test(lines[i])){tableLines.push(lines[i]);i++;}
     flushParagraph();const table=parseTable(tableLines);
     if(table)out.push(table);else out.push('<p>'+tableLines.map(inline).join('<br>')+'</p>');
     continue;
   }
   if(/^\s*>\s?/.test(line)){
     flushParagraph();let quote=[];
     while(i<lines.length && /^\s*>\s?/.test(lines[i])){quote.push(lines[i].replace(/^\s*>\s?/,''));i++;}
     out.push('<blockquote>'+quote.map(inline).join('<br>')+'</blockquote>');continue;
   }
   if(/^\s*[-+*]\s+/.test(line)){
     flushParagraph();let items=[];
     while(i<lines.length && /^\s*[-+*]\s+/.test(lines[i])){items.push(lines[i].replace(/^\s*[-+*]\s+/,''));i++;}
     out.push('<ul>'+items.map(item=>'<li>'+inline(item)+'</li>').join('')+'</ul>');continue;
   }
   if(/^\s*\d+[.)]\s+/.test(line)){
     flushParagraph();let items=[];
     while(i<lines.length && /^\s*\d+[.)]\s+/.test(lines[i])){items.push(lines[i].replace(/^\s*\d+[.)]\s+/,''));i++;}
     out.push('<ol>'+items.map(item=>'<li>'+inline(item)+'</li>').join('')+'</ol>');continue;
   }
   paragraph.push(line);i++;
 }
 flushParagraph();
 let html=out.join('');
 codeBlocks.forEach((b,i)=>{ /* code blocks are inserted while parsing */ });
 return html;
}
function render(){
 const root=document.getElementById('messages');
 root.querySelectorAll('.message').forEach(function(node){node.remove();});
 const welcome=document.getElementById('welcome');
 if(welcome)welcome.style.display=messages.length?'none':'flex';
 for(const m of messages){
  const el=document.createElement('div');el.className='message '+(m.role==='user'?'user':'assistant');
  const label=document.createElement('div');label.className='role';label.textContent=m.role==='user'?'You':'Spawn AI';
  const body=document.createElement('div');body.className='body';
  if(m.role==='thinking')body.innerHTML='<span class="thinking"><i></i><i></i><i></i></span>';
  else body.innerHTML=markdown(m.content||'');
  el.appendChild(label);el.appendChild(body);root.appendChild(el);
 }
 root.scrollTop=root.scrollHeight;
}
function updateSendButton(){
 const send=document.getElementById('send');
 const prompt=document.getElementById('prompt');
 const hasText=!!(prompt && prompt.value.trim());
 send.disabled=!aiEnabled || stopping || (!busy && !hasText);
 send.title=stopping?'Stopping generation…':(busy?'Stop generation':'Send');
 send.setAttribute('aria-label',send.title);
}
function setEnabled(value,model){
 aiEnabled=!!value;
 const prompt=document.getElementById('prompt');
 const clear=document.getElementById('clear');
 const hint=document.getElementById('hint');
 if(!aiEnabled){
   prompt.value='';prompt.placeholder='Spawn AI is disabled in Settings';
   hint.textContent='Spawn AI disabled';setStatus('disconnected','Spawn AI disabled.');
   clear.disabled=true;prompt.disabled=true;
 }else{
   prompt.placeholder='Ask anything... (Enter to send, Shift+Enter for newline)';
   hint.textContent=model||'No model selected';prompt.disabled=busy||stopping;
   clear.disabled=busy||stopping;setStatus('connecting','Checking connection...');
 }
 updateSendButton();
}
function setModel(model){document.getElementById('hint').textContent=aiEnabled?(model||'No model selected'):'Spawn AI disabled';}
function setBusy(value){
 busy=!!value;
 if(!busy) stopping=false;
 const send=document.getElementById('send');
 const clear=document.getElementById('clear');
 const input=document.getElementById('prompt');
 const stopPath='<path fill-rule="evenodd" clip-rule="evenodd" d="M5.5 5C5.22386 5 5 5.22386 5 5.5V10.5C5 10.7761 5.22386 11 5.5 11H10.5C10.7761 11 11 10.7761 11 10.5V5.5C11 5.22386 10.7761 5 10.5 5H5.5ZM4 5.5C4 4.67157 4.67157 4 5.5 4H10.5C11.3284 4 12 4.67157 12 5.5V10.5C12 11.3284 11.3284 12 10.5 12H5.5C4.67157 12 4 11.3284 4 10.5V5.5Z"/>';
 const sendPath='<path d="M1.17683 1.11898C1.32953 0.989634 1.54464 0.963786 1.72363 1.05328L14.7236 7.55328C14.893 7.63797 15 7.8111 15 8.00049C15 8.18987 14.893 8.36301 14.7236 8.4477L1.72363 14.9477C1.54464 15.0372 1.32953 15.0113 1.17683 14.882C1.02414 14.7526 .96328 14.5447 1.02213 14.3534L2.97688 8.00049L1.02213 1.64754C.96328 1.45627 1.02414 1.24833 1.17683 1.11898ZM3.8693 8.50049L2.32155 13.5307L13.382 8.00049L2.32155 2.47027L3.8693 7.50049H9.50001C9.77615 7.50049 10 7.72435 10 8.00049C10 8.27663 9.77615 8.50049 9.50001 8.50049H3.8693Z"/>';
 send.innerHTML='<svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" fill="currentColor">'+(busy?stopPath:sendPath)+'</svg>';
 if(!stopping) delete send.dataset.stopping;
 send.title=stopping?'Stopping generation…':(busy?'Stop':'Send');
 send.setAttribute('aria-label',send.title);
 clear.disabled=busy||stopping||!aiEnabled;
 input.disabled=busy||stopping||!aiEnabled;
 updateSendButton();
}
function setStatus(state,title){const dot=document.getElementById('status-dot');const colors={connected:'#73c991',connecting:'#d4aa00',disconnected:'#f14c4c',error:'#f14c4c'};dot.style.background=colors[state]||colors.disconnected;dot.title=title||state;}
// Spawn AI owns its chat interactions; disable the browser's default context menu.
document.addEventListener('contextmenu', event => {
 event.preventDefault();
 return false;
});
document.getElementById('messages').addEventListener('click',e=>{const b=e.target.closest('[data-copy]');if(b)post({type:'copy_code',text:decodeURIComponent(b.dataset.copy)});});
document.getElementById('send').addEventListener('click',()=>{if(!aiEnabled||stopping)return;if(busy){stopping=true;const send=document.getElementById('send');send.disabled=true;send.dataset.stopping='true';send.title='Stopping generation…';send.setAttribute('aria-label','Stopping generation');document.getElementById('hint').textContent='Stopping…';setStatus('connecting','Stopping generation…');post({type:'stop_generation'});return;}const input=document.getElementById('prompt');const text=input.value.trim();if(!text)return;addMessage('user',text);input.value='';setBusy(true);addMessage('thinking','');document.getElementById('hint').textContent='Generating…';setStatus('connecting','Generating response…');post({type:'send_message',text});});
document.getElementById('prompt').addEventListener('input',updateSendButton);
document.getElementById('prompt').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();document.getElementById('send').click();}});
document.getElementById('clear').addEventListener('click',()=>{if(busy||!aiEnabled)return;messages.length=0;render();post({type:'clear_chat'});});
document.getElementById('theme').addEventListener('click',function(event){
 event.preventDefault();
 const light=document.body.classList.toggle('light');
 document.documentElement.style.colorScheme=light?'light':'dark';
 this.title=light?'Switch to dark theme':'Switch to light theme';
 this.setAttribute('aria-label',this.title);
 this.setAttribute('aria-pressed',light?'true':'false');
});
window.spawnAI={receive(data){
 if(data.type==='config'){
   setEnabled(!!data.enabled,data.model||'');
   if(data.enabled){setStatus(data.state||'connecting',data.tooltip||'Checking connection...');}
 }else if(data.type==='model'){
   setModel(data.model||'');
 }else if(data.type==='status'){
   setStatus(data.state||((data.ok)?'connected':'disconnected'),data.tooltip||data.text||'Connection status');
   if(data.model)document.getElementById('hint').textContent=data.model;
 }else if(data.type==='token'){
   latestStreamText=data.text||'';
   if(!streamUpdatePending){
     streamUpdatePending=true;
     streamUpdateTimer=setTimeout(()=>{
       streamUpdatePending=false;
       const idx=messages.findIndex(m=>m.role==='thinking'||m.role==='streaming');
       if(idx>=0){messages[idx]={role:'streaming',content:latestStreamText};render();}
     },120);
   }
 }else if(data.type==='assistant'){
   if(streamUpdateTimer){clearTimeout(streamUpdateTimer);streamUpdateTimer=null;}
   streamUpdatePending=false;latestStreamText='';
   const idx=messages.findIndex(m=>m.role==='thinking'||m.role==='streaming');
   if(idx>=0){messages[idx]={role:'assistant',content:data.text};render();}
   else addMessage('assistant',data.text);
   setBusy(false);
   document.getElementById('hint').textContent=data.model||'Local model';
   setStatus('connected','Connected to LM Studio');
 }else if(data.type==='stopped'){
   if(streamUpdateTimer){clearTimeout(streamUpdateTimer);streamUpdateTimer=null;}
   streamUpdatePending=false;latestStreamText='';
   const idx=messages.findIndex(m=>m.role==='thinking'||m.role==='streaming');
   if(idx>=0){if(data.text){messages[idx]={role:'assistant',content:data.text};render();}else if(messages[idx].role==='thinking'){messages.splice(idx,1);render();}}
   else if(data.text)addMessage('assistant',data.text);
   setBusy(false);document.getElementById('hint').textContent=data.model||'Generation stopped';
 }else if(data.type==='error'){
   const thinking=messages.findIndex(m=>m.role==='thinking');
   if(thinking>=0)messages.splice(thinking,1);
   addMessage('assistant','Error: '+data.text);setBusy(false);
   document.getElementById('hint').textContent='Request failed';
   setStatus('error','Connection or generation error');
 }else if(data.type==='stopping'){
   stopping=true;
   const send=document.getElementById('send');
   send.disabled=true;send.title='Stopping generation…';send.setAttribute('aria-label','Stopping generation');
   document.getElementById('prompt').disabled=true;
   document.getElementById('clear').disabled=true;
   document.getElementById('hint').textContent='Stopping…';
 }else if(data.type==='copied'){
   const toast=document.getElementById('copy-toast');toast.textContent=data.text||'Copied to clipboard';toast.classList.add('visible');
   clearTimeout(window.__copyToastTimer);window.__copyToastTimer=setTimeout(()=>toast.classList.remove('visible'),1800);
 }else if(data.type==='busy'){
   setBusy(!!data.value);
 }
}};
</script></body></html>'''


class AIDockPanel(wx.Panel):
    """Chat view; settings are supplied by SpawnIDE/config_manager integration."""

    def __init__(self, parent, config_getter=None):
        super().__init__(parent)
        self.config_getter = config_getter
        self.config_setter = None
        self._runtime_model = ""
        self.history: list[dict[str, str]] = []
        self._request_lock = threading.Lock()
        self._busy = False
        self._destroyed = False
        self._request_id = 0
        self._web_ready = False
        self._pending_web_payloads = []
        self.Bind(wx.EVT_WINDOW_DESTROY, self._on_window_destroy)
        self.webview = wx.html2.WebView.New(self)
        # Suppress the native WebView context menu as well as the HTML context menu.
        try:
            self.webview.EnableContextMenu(False)
        except (AttributeError, RuntimeError):
            pass
        self.webview.SetPage(HTML_PAGE, "")
        self.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, self._on_loaded)
        if hasattr(self.webview, "AddScriptMessageHandler"):
            self.webview.AddScriptMessageHandler("wx")
            self.webview.Bind(wx.html2.EVT_WEBVIEW_SCRIPT_MESSAGE_RECEIVED, self._on_script_message)
        else:
            # Older backends can still display the UI, but require the message bridge API.
            wx.CallAfter(self._set_status, "WebView message bridge unavailable")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.webview, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def _on_window_destroy(self, event):
        # Ignore late worker callbacks after the dock/panel has been closed.
        if event.GetEventObject() is self:
            self._destroyed = True
            self._web_ready = False
            cancel_event = getattr(self, "_cancel_event", None)
            if cancel_event is not None:
                cancel_event.set()
        event.Skip()

    @staticmethod
    def _page_for_system_theme() -> str:
        """Use native system colours as a sensible fallback for the IDE theme."""
        def colour(system_id, fallback):
            try:
                c = wx.SystemSettings.GetColour(system_id)
                if c.IsOk():
                    return f"#{c.Red():02x}{c.Green():02x}{c.Blue():02x}"
            except Exception:
                pass
            return fallback
        background = colour(wx.SYS_COLOUR_WINDOW, "#1e1e1e")
        foreground = colour(wx.SYS_COLOUR_WINDOWTEXT, "#d4d4d4")
        panel = colour(wx.SYS_COLOUR_BTNFACE, "#252526")
        border = colour(wx.SYS_COLOUR_3DDKSHADOW, "#3c3c3c")
        page = HTML_PAGE.replace("--bg:#1e1e1e", f"--bg:{background}")
        page = page.replace("--text:#ddd", f"--text:{foreground}").replace("--text:#d4d4d4", f"--text:{foreground}")
        page = page.replace("--panel:#252526", f"--panel:{panel}").replace("--border:#3c3c3c", f"--border:{border}")
        return page

    def _settings(self) -> dict:
        defaults = {
            "enabled": False, "provider": "lm_studio",
            "base_url": "http://localhost:1234/v1", "api_key": "", "model": "",
        }
        if callable(self.config_getter):
            try:
                value = self.config_getter()
                if isinstance(value, dict):
                    # Accept either the editor.ai subsection, editor section, or whole config.
                    if isinstance(value.get("editor"), dict):
                        value = value["editor"].get("ai", {})
                    elif isinstance(value.get("ai"), dict):
                        value = value["ai"]
                    return {**defaults, **value}
            except Exception:
                pass
        return defaults

    def refresh_settings(self):
        """Apply saved settings without blocking the GUI thread."""
        cfg = self._settings()
        enabled = bool(cfg.get("enabled", False))
        model = str(cfg.get("model", "") or "").strip() or self._runtime_model
        self._runtime_model = model
        self._send_to_web({
            "type": "config", "enabled": enabled, "model": model,
            "state": "connecting" if enabled else "disconnected",
            "tooltip": "Checking connection..." if enabled else "Spawn AI disabled.",
        })
        if not enabled:
            return
        # Connection checks run in a worker; never wait for HTTP on the UI thread.
        self._test_connection()

    def _client(self) -> LMStudioClient:
        cfg = self._settings()
        return AIService(cfg)

    def _on_loaded(self, event):
        self._web_ready = True
        pending = list(self._pending_web_payloads)
        self._pending_web_payloads.clear()
        for payload in pending:
            self._send_to_web(payload)
        wx.CallAfter(self.refresh_settings)
        event.Skip()

    def _on_script_message(self, event):
        try:
            payload = json.loads(event.GetString())
        except (ValueError, TypeError):
            return
        if not isinstance(payload, dict):
            return
        action = payload.get("type")
        if action == "send_message":
            text = payload.get("text", "")
            if isinstance(text, str) and text.strip():
                self._send_message(text.strip())
        elif action == "stop_generation":
            self.stop_generation()
        elif action == "clear_chat":
            if not self._busy:
                self.history.clear()
        elif action == "copy_code":
            text = payload.get("text", "")
            if isinstance(text, str):
                wx.CallAfter(self._copy_text, text)
        elif action == "test_connection":
            self._test_connection()

    def _copy_text(self, text: str):
        copied = False
        if wx.TheClipboard.Open():
            try:
                copied = bool(wx.TheClipboard.SetData(wx.TextDataObject(text)))
            finally:
                wx.TheClipboard.Close()
        self._send_to_web({
            "type": "copied" if copied else "status",
            "text": "Copied to clipboard" if copied else "Could not copy code",
            "state": "connected" if copied else "disconnected",
            "tooltip": "Copied to clipboard" if copied else "Clipboard is unavailable",
            "ok": copied,
        })

    def _test_connection(self):
        if self._busy:
            return
        cfg = self._settings()
        if not cfg.get("enabled", False):
            self._send_to_web({"type": "config", "enabled": False, "model": "",
                               "state": "disconnected",
                               "tooltip": "Spawn AI disabled."})
            return
        model = str(cfg.get("model", "") or "").strip()
        self._send_to_web({"type": "config", "enabled": True, "model": model,
                           "state": "connecting", "tooltip": "Checking connection..."})
        threading.Thread(target=self._connection_worker, daemon=True).start()

    def _connection_worker(self):
        try:
            cfg = self._settings()
            models = AIService(cfg).test_connection()
            selected = str(cfg.get("model", "") or "").strip()
            ids = [str(item.get("id")) for item in models]
            # Embedding/reranking models cannot generate chat completions. Hide them
            # from the chat model selection and never silently choose one.
            chat_ids = [
                model_id for model_id in ids
                if not any(token in model_id.lower()
                           for token in ("embedding", "embed-", "rerank", "reranker"))
            ]
            if selected and any(token in selected.lower()
                                for token in ("embedding", "embed-", "rerank", "reranker")):
                selected = ""
            if not selected and chat_ids:
                selected = chat_ids[0]
                self._runtime_model = selected
                setter = getattr(self, "config_setter", None)
                if callable(setter):
                    try:
                        wx.CallAfter(setter, "editor.ai.model", selected)
                    except Exception:
                        pass
            elif selected:
                self._runtime_model = selected
            wx.CallAfter(self._send_to_web, {"type": "model", "model": selected or "No model selected"})
            if chat_ids:
                message = "Connected" if selected in chat_ids else "Select a chat model"
                tooltip = ("Connected to LM Studio" if message == "Connected"
                           else "Choose a chat completion model in Settings → AI; embedding models cannot chat")
                wx.CallAfter(self._set_status, message, state="connected",
                             tooltip=tooltip)
            else:
                wx.CallAfter(self._set_status, "No chat models available", state="connected",
                             tooltip="LM Studio is reachable, but only embedding/reranking models or no models were returned")
        except Exception as exc:
            wx.CallAfter(self._set_status, "Connection failed", state="disconnected",
                         tooltip=str(exc))

    def _send_message(self, text: str):
        if self._busy:
            return
        cfg = self._settings()
        if not cfg.get("enabled", False):
            self._send_to_web({"type": "config", "enabled": False, "model": "",
                               "state": "disconnected",
                               "tooltip": "Spawn AI disabled"})
            return
        model = str(cfg.get("model", "") or "").strip() or self._runtime_model
        if not model:
            self._send_to_web({"type": "error", "text": "No chat model selected. Open Settings → AI and select a text-generation/chat model. Embedding models cannot generate replies."})
            return
        if any(token in model.lower() for token in ("embedding", "embed-", "rerank", "reranker")):
            self._send_to_web({"type": "error", "text": "The selected model is an embedding/reranking model, not a chat model. Select a chat completion model in Settings → AI."})
            return
        self._busy = True
        self._request_id += 1
        request_id = self._request_id
        self._last_token_ui_update = 0.0
        self._latest_token_text = ""
        self._cancel_event = threading.Event()
        self._active_client = self._client()
        # Keep UI history separate from model input. Each request sends only the
        # current prompt; previous assistant answers are not reattached to later calls.
        self.history.clear()
        self.history.append({"role": "user", "content": text})
        request_messages = [{"role": "user", "content": text}]
        self._send_to_web({"type": "busy", "value": True})
        self._send_to_web({"type": "status", "text": "Generating", "state": "connecting",
                           "tooltip": "Thinking...", "model": model})
        threading.Thread(
            target=self._request_worker,
            args=(request_messages, model, self._cancel_event, self._active_client, request_id),
            daemon=True,
        ).start()

    def stop_generation(self):
        if self._busy and getattr(self, "_cancel_event", None):
            self._cancel_event.set()
            active_client = getattr(self, "_active_client", None)
            if active_client is not None and hasattr(active_client, "cancel_current_request"):
                active_client.cancel_current_request()
            self._send_to_web({"type": "status", "text": "Stopping", "state": "connecting",
                               "tooltip": "Stopping generation..."})
            self._send_to_web({"type": "stopping"})

    def _request_worker(self, messages, model, cancel_event, client, request_id):
        try:
            chunks = []
            def on_token(token):
                chunks.append(token)
                # Limit cross-thread WebView calls; full history is rendered at most ~8 times/sec.
                import time
                now = time.monotonic()
                full_text = "".join(chunks)
                if now - getattr(self, "_last_token_ui_update", 0.0) >= 0.12:
                    self._last_token_ui_update = now
                    wx.CallAfter(self._deliver_token, request_id, full_text)
            answer = client.chat(messages, model, stream=True, on_token=on_token,
                                 cancel_event=cancel_event)
            if cancel_event.is_set():
                payload = {"type": "stopped", "text": "".join(chunks), "model": model}
            elif not isinstance(answer, str) or not answer.strip():
                raise AIClientError("The model returned an empty response.")
            else:
                payload = {"type": "assistant", "text": answer, "model": model}
        except Exception as exc:
            if cancel_event.is_set():
                payload = {"type": "stopped", "text": "".join(chunks), "model": model}
            else:
                payload = {"type": "error", "text": str(exc)}
        wx.CallAfter(self._finish_request, payload, request_id)

    def _deliver_token(self, request_id, text):
        if self._destroyed or not self._busy or request_id != self._request_id:
            return
        self._send_to_web({"type": "token", "text": text})

    def _finish_request(self, payload, request_id):
        if self._destroyed or request_id != self._request_id:
            return
        # Commit assistant turns on the UI thread, paired with the user turn that
        # was already added before the request. This keeps future requests coherent.
        if payload.get("type") == "assistant":
            answer = payload.get("text", "")
            if isinstance(answer, str) and answer.strip():
                if not self.history or self.history[-1].get("role") != "assistant":
                    self.history.append({"role": "assistant", "content": answer})
        self._busy = False
        self._request_id += 1  # Discard any token updates queued before completion.
        self._send_to_web(payload)
        self._send_to_web({"type": "busy", "value": False})
        if payload.get("type") in ("assistant", "stopped"):
            self._set_status("Connected", state="connected", tooltip="Connected")
        elif payload.get("type") == "error":
            self._set_status("Connection error", state="disconnected", tooltip=payload.get("text", "Request failed"))

    def _send_to_web(self, payload: dict):
        if getattr(self, "_destroyed", False):
            return
        try:
            if self.IsBeingDeleted():
                return
        except (RuntimeError, wx.PyDeadObjectError):
            return
        if not getattr(self, "_web_ready", False):
            self._pending_web_payloads.append(payload)
            return
        encoded = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
        script = f"if (window.spawnAI && typeof window.spawnAI.receive === 'function') {{ window.spawnAI.receive({encoded}); }}"
        try:
            self.webview.RunScript(script)
        except Exception:
            # Do not let a transient WebView navigation error disrupt the IDE.
            self._pending_web_payloads.append(payload)

    def _set_status(self, text: str, state: str = "disconnected", tooltip: str | None = None):
        try:
            cfg = self._settings()
            model = str(cfg.get("model", "") or "").strip() or self._runtime_model
        except Exception:
            model = getattr(self, "_runtime_model", "")
        self._send_to_web({
            "type": "status", "text": text, "model": model,
            "state": state, "tooltip": tooltip or text,
        })

    def set_config_getter(self, getter):
        self.config_getter = getter
        self.refresh_settings()

    def set_config_setter(self, setter):
        """Optional callback: setter(path, value) persists a global config setting."""
        self.config_setter = setter
