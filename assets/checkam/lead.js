/* Business enquiry form: saves to the CheckAm admin (Business leads) through a public, rate-limited function. */
(function(){
  var U='https://ifbkvqazedhghtguanjf.supabase.co/rest/v1/rpc/',K='sb_publishable_9I-s_mRycqI_gv4i7mXN4Q_l0zph5nq';
  function post(fn,body){return fetch(U+fn,{method:'POST',keepalive:true,headers:{'Content-Type':'application/json',apikey:K,Authorization:'Bearer '+K},body:JSON.stringify(body)});}
  var q=new URLSearchParams(location.search),ref='',src=q.get('utm_source')||q.get('src')||'';
  try{ref=document.referrer?new URL(document.referrer).hostname.replace(/^www\./,''):''}catch(e){}
  if(!src)src=ref||'direct';

  var f=document.getElementById('lead');
  if(f){
    var msg=document.getElementById('lead-msg');
    f.addEventListener('submit',function(e){
      e.preventDefault();
      var v=function(n){var el=f.elements[n];return el?String(el.value||'').trim():'';};
      var ticks=[].map.call(f.querySelectorAll('input[name="interest"]:checked'),function(i){return i.value;});
      if(f.dataset.needTick&&!ticks.length){msg.hidden=false;msg.dataset.k='err';msg.textContent=f.dataset.needTick;return;}
      var btn=f.querySelector('button[type=submit]');btn.disabled=true;btn.textContent='Sending…';msg.hidden=true;
      post('submit_business_lead',{p_kind:f.dataset.kind,p_name:v('name'),p_company:v('company'),p_email:v('email'),p_role:v('role')||null,p_phone:v('phone')||null,
        p_company_type:v('company_type')||null,p_team_size:v('size')||null,p_interest:ticks,p_message:v('message')||null,p_source:src.slice(0,80),p_website:v('website')||null})
        .then(function(r){return r.json().then(function(j){if(!r.ok)throw new Error(j&&j.message||'Something went wrong.');return j;});})
        .then(function(){
          var d=document.createElement('div');d.className='done';d.setAttribute('role','status');
          d.innerHTML='<div class="kicker">Request received</div><h3>Thank you, '+v('name').split(' ')[0].replace(/[<>&"]/g,'')+'.</h3><p>We will reply to <b>'+v('email').replace(/[<>&"]/g,'')+'</b> within two working days. If it is urgent, email hello@openfraudlabs.com.</p>';
          f.replaceWith(d);d.scrollIntoView({behavior:'smooth',block:'center'});
        })
        .catch(function(err){msg.hidden=false;msg.dataset.k='err';msg.textContent=(err&&err.message)||'Could not send. Please email hello@openfraudlabs.com.';btn.disabled=false;btn.textContent=f.dataset.label||'Send request';});
    });
  }

  /* Anonymous visit counter, same as the CheckAm page: no cookies, no IP. */
  if(document.body.dataset.track){
    var vid=null;try{vid=localStorage.getItem('ckv');if(!vid){vid=(crypto.randomUUID?crypto.randomUUID():String(Math.random()).slice(2));localStorage.setItem('ckv',vid);}}catch(e){}
    var s=src==='direct'?'direct':/facebook|fb\./.test(src)?'facebook':/linkedin|lnkd/.test(src)?'linkedin':/whatsapp|wa\.me/.test(src)?'whatsapp':/google\./.test(src)?'google':/openfraudlabs/.test(src)?'openfraudlabs':src;
    try{post('log_visit',{p_event:'view',p_path:location.pathname,p_source:s,p_ref:ref||null,p_vid:vid});}catch(e){}
  }
})();
