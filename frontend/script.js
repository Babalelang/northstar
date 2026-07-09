 const standings = [
    ["Orlando Pirates",30,21,6,3,58,12],
    ["Mamelodi Sundowns",30,20,8,2,57,21],
    ["Kaizer Chiefs",30,15,9,6,33,19],
    ["AmaZulu",30,13,8,9,32,28],
    ["Sekhukhune United",30,11,11,8,32,27],
    ["Golden Arrows",30,11,8,11,34,33],
    ["Polokwane City",30,9,13,8,21,21],
    ["Durban City",30,10,9,11,25,26],
    ["Stellenbosch",30,9,10,11,26,30],
    ["Siwelele",30,8,13,9,24,28],
    ["Richards Bay",30,7,13,10,23,30],
    ["TS Galaxy",30,8,8,14,30,38],
    ["Chippa United",30,6,10,14,24,44],
    ["Marumo Gallants",30,4,13,13,21,38],
    ["Magesi FC",30,5,9,16,24,43],
    ["Orbit College",30,6,6,18,21,47],
  ];
  const tbody = document.querySelector("#table-body tbody");
  standings.forEach((row,i)=>{
    const [team,gp,w,d,l,gf,ga] = row;
    const gd = gf-ga;
    const pts = w*3+d;
    const pos = i+1;
    const tr = document.createElement("tr");
    if(pos===1) tr.className="zone-title";
    else if(pos<=5) tr.className="zone-cont";
    else if(pos>=15) tr.className="zone-rel";
    tr.innerHTML = `<td class="pos">${pos}</td><td class="team">${team}</td>
      <td class="num">${gp}</td><td class="num">${w}</td><td class="num">${d}</td><td class="num">${l}</td>
      <td class="num">${gf}</td><td class="num">${ga}</td><td class="num">${gd>0?"+"+gd:gd}</td><td class="pts">${pts}</td>`;
    tbody.appendChild(tr);
  });

  const news = [
    {tag:"Title race", head:"Sundowns chase top spot after continental heroics", body:"Mamelodi Sundowns look to return to the summit of the Betway Premiership on the back of a strong CAF Champions League run, with the title race tightening at the top of the table.", src:"ESPN"},
    {tag:"Title race", head:"Pirates push to keep their challenge on track", body:"Orlando Pirates aim to keep their title bid alive at home, with matches against fellow top-half sides carrying heavy weight in the run-in.", src:"ESPN"},
    {tag:"Transfer", head:"Mofokeng linked with a move to Europe", body:"Union Saint-Gilloise are reported to be leading the race to sign Pirates playmaker Relebohile Mofokeng, fresh off being named the league's most valuable player and its Transfermarkt Player of the Season.", src:"Transfermarkt"},
    {tag:"Transfer", head:"Nkota completes move to the Saudi Pro League", body:"AmaZulu winger and Bafana Bafana international Mohau Nkota has joined Al-Ettifaq, part of a broader trend of South African talent attracting interest from outside the continent.", src:"ESPN"},
    {tag:"Squad news", head:"Pirates strengthen with a triple signing", body:"Orlando Pirates have confirmed the arrivals of defenders Neo Rapoo and Aphiwe Baliti, alongside midfielder Matome Mmolai, bolstering squad depth for the closing stretch of the season.", src:"ESPN"},
    {tag:"National team", head:"Bafana Bafana reflect on a historic World Cup run", body:"South Africa reached the knockout stage of the FIFA World Cup for the first time, recovering from an opening defeat to make history before their eventual exit.", src:"ESPN"},
  ];
  const ng = document.getElementById("news-grid");
  news.forEach(n=>{
    const div = document.createElement("div");
    div.className="news-card";
    div.innerHTML = `<div class="news-tag">${n.tag}</div><div class="news-head">${n.head}</div><div class="news-body">${n.body}</div><span class="news-src">Source: ${n.src}</span>`;
    ng.appendChild(div);
  });

  const players = [
    {name:"Relebohile Mofokeng", role:"Attacking midfielder — Orlando Pirates", index:88, pace:82, vision:90, dribbling:89, finishing:78, value:"€3.0m"},
    {name:"Teboho Mokoena", role:"Central midfielder — Mamelodi Sundowns", index:86, pace:70, vision:88, dribbling:80, finishing:70, value:"€2.8m"},
    {name:"Iqraam Rayners", role:"Centre-forward — Mamelodi Sundowns", index:85, pace:76, vision:68, dribbling:74, finishing:88, value:"€2.8m"},
    {name:"Oswin Appollis", role:"Winger — Orlando Pirates", index:83, pace:88, vision:74, dribbling:85, finishing:76, value:"€2.5m"},
    {name:"Thalente Mbatha", role:"Midfielder — Orlando Pirates", index:80, pace:74, vision:82, dribbling:78, finishing:66, value:"€2.0m"},
    {name:"Aubrey Modiba", role:"Left-back — Mamelodi Sundowns", index:78, pace:80, vision:72, dribbling:75, finishing:52, value:"€1.8m"},
  ];
  const pg = document.getElementById("player-grid");
  function bar(label,val){
    return `<div class="skill-row"><div class="skill-label">${label}</div><div class="skill-bar"><div class="skill-fill" style="width:${val}%"></div></div><div class="skill-val">${val}</div></div>`;
  }
  players.forEach(p=>{
    const card = document.createElement("div");
    card.className="pcard";
    card.innerHTML = `
      <div class="pcard-top">
        <div><div class="pcard-name">${p.name}</div><div class="pcard-role">${p.role}</div></div>
        <div class="pcard-index">${p.index}</div>
      </div>
      <div class="pcard-body">
        ${bar("Pace",p.pace)}
        ${bar("Vision",p.vision)}
        ${bar("Dribbling",p.dribbling)}
        ${bar("Finishing",p.finishing)}
      </div>
      <div class="pcard-foot"><span>VUVA Index</span><span>Value ${p.value}</span></div>
    `;
    pg.appendChild(card);
  });

  const marketValues = [
    {name:"Relebohile Mofokeng", club:"Orlando Pirates", pos:"AM", value:3.0},
    {name:"Teboho Mokoena", club:"Mamelodi Sundowns", pos:"CM", value:2.8},
    {name:"Iqraam Rayners", club:"Mamelodi Sundowns", pos:"CF", value:2.8},
    {name:"Oswin Appollis", club:"Orlando Pirates", pos:"RW", value:2.5},
    {name:"Thalente Mbatha", club:"Orlando Pirates", pos:"CM", value:2.0},
    {name:"Jayden Adams", club:"Mamelodi Sundowns", pos:"CM", value:1.8},
    {name:"Aubrey Modiba", club:"Mamelodi Sundowns", pos:"LB", value:1.8},
  ];
  const mvBody = document.getElementById("mv-body");
  const maxVal = Math.max(...marketValues.map(m=>m.value));
  marketValues.forEach((m,i)=>{
    const tr = document.createElement("tr");
    const pct = Math.round((m.value/maxVal)*100);
    tr.innerHTML = `<td class="rank">${i+1}</td><td class="name">${m.name}</td><td class="club">${m.club}</td><td class="club">${m.pos}</td>
      <td class="bar-cell"><div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div></td>
      <td class="val">€${m.value.toFixed(1)}m</td>`;
    mvBody.appendChild(tr);
  });

  document.querySelectorAll("nav.links button").forEach(btn=>{
    btn.addEventListener("click", ()=> showPage(btn.dataset.page));
  });
  document.querySelectorAll(".qn-card").forEach(card=>{
    card.addEventListener("click", ()=> showPage(card.dataset.goto));
  });
  function showPage(id){
    document.querySelectorAll("section.page").forEach(s=>s.classList.remove("active"));
    document.getElementById(id).classList.add("active");
    document.querySelectorAll("nav.links button").forEach(b=>b.classList.toggle("active", b.dataset.page===id));
    window.scrollTo({top:0,behavior:"smooth"});
  }