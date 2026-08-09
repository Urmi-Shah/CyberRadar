const API="http://127.0.0.1:8000";
const charts={};

const $=id=>document.getElementById(id);

const money=n=>
    "₹"+
    Number(n||0).toLocaleString("en-IN",{
        maximumFractionDigits:0
    });

const number=n=>
    Number(n||0).toLocaleString("en-IN");


async function getJSON(url,options={}){
    const r=await fetch(url,options);

    if(!r.ok){
        throw new Error(await r.text());
    }

    return r.json();
}


function toast(message,error=false){
    const t=$("toast");

    if(!t)return;

    t.textContent=message;

    t.className=
        "toast show"+
        (error?" error":"");

    setTimeout(
        ()=>{
            t.className="toast";
        },
        3000
    );
}


function fillSelect(id,values){
    const el=$(id);

    if(!el)return;

    el.innerHTML="<option value='All'>All</option>";

    (values||[]).forEach(v=>{
        const option=document.createElement("option");

        option.value=v;
        option.textContent=v;

        el.appendChild(option);
    });
}


async function loadFilters(){
    const d=
        await getJSON(
            `${API}/analytics/filters`
        );

    [
        "state",
        "city",
        "incident_type",
        "sector",
        "source",
        "status"
    ].forEach(
        k=>fillSelect(k,d[k])
    );
}


function queryParams(){
    const p=new URLSearchParams();

    [
        "period",
        "state",
        "city",
        "incident_type",
        "sector",
        "source",
        "status",
        "search",
        "start",
        "end"
    ].forEach(k=>{
        const v=$(k)?.value||"";

        if(v){
            p.set(k,v);
        }
    });

    p.set(
        "severities",
        [
            ...document.querySelectorAll(
                ".sev:checked"
            )
        ]
        .map(x=>x.value)
        .join(",")
    );

    return p;
}


function chart(
    id,
    type,
    labels,
    values,
    label,
    horizontal=false
){
    const canvas=$(id);

    if(!canvas)return;

    if(charts[id]){
        charts[id].destroy();
    }

    charts[id]=new Chart(
        canvas,
        {
            type:type,

            data:{
                labels:labels,

                datasets:[
                    {
                        label:label,
                        data:values,
                        borderWidth:2,
                        tension:.35,
                        fill:type==="line"
                    }
                ]
            },

            options:{
                responsive:true,
                maintainAspectRatio:false,

                indexAxis:
                    horizontal?"y":"x",

                plugins:{
                    legend:{
                        labels:{
                            color:"#cbd5e1"
                        }
                    },

                    tooltip:{
                        mode:"index",
                        intersect:false
                    }
                },

                scales:
                    type==="doughnut"||
                    type==="pie"
                    ?{}
                    :{
                        x:{
                            ticks:{
                                color:"#94a3b8"
                            },

                            grid:{
                                color:"#1e293b"
                            }
                        },

                        y:{
                            ticks:{
                                color:"#94a3b8"
                            },

                            grid:{
                                color:"#1e293b"
                            }
                        }
                    }
            }
        }
    );
}


function render(data){
    const kpis=data.kpis||{};
    const insights=data.insights||{};

    if($("total")){
        $("total").textContent=
            number(kpis.total);
    }

    if($("critical")){
        $("critical").textContent=
            number(kpis.critical);
    }

    if($("loss")){
        $("loss").textContent=
            money(kpis.loss);
    }

    if($("users")){
        $("users").textContent=
            number(kpis.users);
    }

    if($("riskScore")){
        $("riskScore").textContent=
            insights.risk_score??"—";
    }

    if($("riskLevel")){
        $("riskLevel").textContent=
            insights.risk_level||"—";
    }

    if($("topState")){
        $("topState").textContent=
            insights.top_state||"—";
    }

    if($("topAttack")){
        $("topAttack").textContent=
            insights.top_attack||"—";
    }

    if($("topSector")){
        $("topSector").textContent=
            insights.top_sector||"—";
    }

    if($("topCity")){
        $("topCity").textContent=
            insights.top_city||"—";
    }


    const c=data.charts||{};


    chart(
        "monthlyChart",
        "line",
        c.monthly?.labels||[],
        c.monthly?.values||[],
        "Incidents"
    );


    chart(
        "attackChart",
        "doughnut",
        c.attack?.labels||[],
        c.attack?.values||[],
        "Attacks"
    );


    chart(
        "severityChart",
        "bar",
        c.severity?.labels||[],
        c.severity?.values||[],
        "Incidents"
    );


    chart(
        "stateChart",
        "bar",
        c.states?.labels||[],
        c.states?.values||[],
        "Incidents",
        true
    );


    chart(
        "cityChart",
        "bar",
        c.cities?.labels||[],
        c.cities?.values||[],
        "Incidents",
        true
    );


    chart(
        "lossChart",
        "line",
        c.financial?.labels||[],
        c.financial?.values||[],
        "INR Loss"
    );


    chart(
        "sectorChart",
        "doughnut",
        c.sector?.labels||[],
        c.sector?.values||[],
        "Incidents"
    );


    chart(
        "sourceChart",
        "bar",
        c.source?.labels||[],
        c.source?.values||[],
        "Incidents"
    );


    if($("resultCount")){
        $("resultCount").textContent=
            `${Number(kpis.total||0).toLocaleString()} records`;
    }


    if($("incidentRows")){
        $("incidentRows").innerHTML=
            (data.rows||[])
            .map(x=>`
                <tr>
                    <td>${x.incident_id||""}</td>
                    <td>${x.date||""}</td>
                    <td>${x.state||""}</td>
                    <td>${x.city||""}</td>
                    <td>${x.incident_type||""}</td>
                    <td>
                        <span class="badge ${String(
                            x.severity||""
                        ).toLowerCase()}">
                            ${x.severity||""}
                        </span>
                    </td>
                    <td>${x.sector||""}</td>
                    <td>${x.source||""}</td>
                </tr>
            `)
            .join("");
    }
}


async function loadDashboard(){
    try{
        const data=
            await getJSON(
                `${API}/analytics/dashboard?${queryParams()}`
            );

        render(data);

    }catch(e){
        toast(
            "Analysis failed: "+e.message,
            true
        );
    }
}


async function syncPipeline(){
    const b=$("syncBtn");

    if(!b)return;

    b.disabled=true;
    b.textContent="Syncing...";

    try{
        const d=
            await getJSON(
                `${API}/pipeline/sync`,
                {
                    method:"POST"
                }
            );

        toast(
            `Web scraping complete — ${
                d.records_added||0
            } new records added`
        );

        await loadFilters();
        await loadDashboard();

    }catch(e){

        toast(
            "Web scraping failed: "+e.message,
            true
        );

    }finally{

        b.disabled=false;
        b.textContent="Sync Now";
    }
}


function resetFilters(){

    [
        "period",
        "state",
        "city",
        "incident_type",
        "sector",
        "source",
        "status"
    ].forEach(k=>{
        if($(k)){
            $(k).value="All";
        }
    });


    if($("period")){
        $("period").value="all";
    }

    if($("search")){
        $("search").value="";
    }

    if($("start")){
        $("start").value="";
    }

    if($("end")){
        $("end").value="";
    }


    document
        .querySelectorAll(".sev")
        .forEach(
            x=>x.checked=false
        );


    loadDashboard();
}


function openModal(){

    if(!$("modal"))return;

    $("modal").classList.add("open");

    if(
        $("m_date")&&
        !$("m_date").value
    ){
        $("m_date").value=
            new Date()
            .toISOString()
            .slice(0,10);
    }
}


function closeModal(){

    if(!$("modal"))return;

    $("modal").classList.remove("open");
}


async function submitIncident(e){

    e.preventDefault();

    const payload={
        date:$("m_date")?.value,
        state:$("m_state")?.value,
        city:$("m_city")?.value,
        incident_type:$("m_type")?.value,
        severity:$("m_severity")?.value,
        sector:$("m_sector")?.value||"General",

        financial_loss_inr:
            Number(
                $("m_loss")?.value||0
            ),

        affected_users:
            Number(
                $("m_users")?.value||0
            ),

        status:$("m_status")?.value,
        source:"Manual Entry",
        description:
            $("m_description")?.value
    };


    try{

        await getJSON(
            `${API}/incidents`,
            {
                method:"POST",

                headers:{
                    "Content-Type":
                        "application/json"
                },

                body:JSON.stringify(payload)
            }
        );


        closeModal();

        e.target.reset();

        toast(
            "Incident saved and added to analysis"
        );

        await loadFilters();
        await loadDashboard();

    }catch(err){

        toast(
            "Could not save incident: "+
            err.message,
            true
        );
    }
}


/* =====================================================
   BASIC DASHBOARD EVENTS
===================================================== */


document.addEventListener(
    "DOMContentLoaded",
    function(){

        const period=$("period");

        if(period){

            period.addEventListener(
                "change",
                e=>{

                    const custom=
                        e.target.value==="custom";

                    if($("start")){
                        $("start").style.display=
                            custom?"block":"none";
                    }

                    if($("end")){
                        $("end").style.display=
                            custom?"block":"none";
                    }
                }
            );
        }


        const search=$("search");

        if(search){

            search.addEventListener(
                "keydown",
                e=>{
                    if(e.key==="Enter"){
                        loadDashboard();
                    }
                }
            );
        }

    }
);


/* =====================================================
   INDIA THREAT MAP
===================================================== */


let indiaMap=null;
let indiaLayer=null;
let indiaStateData={};


function getRiskColor(level){

    switch(
        String(level||"LOW").toUpperCase()
    ){

        case "CRITICAL":
            return "#ef4444";

        case "HIGH":
            return "#f97316";

        case "MEDIUM":
            return "#eab308";

        case "LOW":
            return "#22c55e";

        default:
            return "#22c55e";
    }
}


async function loadMapStateData(){

    try{

        const response=
            await fetch(
                `${API}/map/states`
            );


        if(!response.ok){

            throw new Error(
                "State analytics API returned "+
                response.status
            );
        }


        const data=
            await response.json();


        console.log(
            "MAP API RESPONSE:",
            data
        );


        indiaStateData=
            data.states||
            data.data?.states||
            data.data||
            data||
            {};


        console.log(
            "STATE DATA LOADED:",
            indiaStateData
        );


        return indiaStateData;

    }catch(error){

        console.error(
            "STATE DATA ERROR:",
            error
        );

        indiaStateData={};

        return {};
    }
}


function findStateData(stateName){

    if(!stateName){
        return null;
    }


    const normalize=name=>
        String(name||"")
        .trim()
        .toLowerCase()
        .replace(/\s+/g," ");


    const target=
        normalize(stateName);


    const matchedKey=
        Object.keys(indiaStateData)
        .find(
            key=>
                normalize(key)===target
        );


    if(matchedKey){
        return indiaStateData[matchedKey];
    }


    const aliases={
        "orissa":"Odisha",
        "uttaranchal":"Uttarakhand",
        "pondicherry":"Puducherry",
        "nct of delhi":"Delhi",
        "delhi ncr":"Delhi",
        "jammu & kashmir":
            "Jammu and Kashmir"
    };


    const alias=
        aliases[target];


    if(
        alias&&
        indiaStateData[alias]
    ){
        return indiaStateData[alias];
    }


    return null;
}


function createIndiaMap(){

    if(indiaMap){
        return;
    }


    const mapElement=
        $("indiaMap");


    if(!mapElement){

        console.error(
            "indiaMap element not found"
        );

        return;
    }


    indiaMap=
        L.map(
            "indiaMap",
            {
                zoomControl:true,
                scrollWheelZoom:true,
                attributionControl:true
            }
        );


    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom:10,
            attribution:
                "&copy; OpenStreetMap contributors"
        }
    ).addTo(indiaMap);


    indiaMap.setView(
        [22.5,79],
        5
    );


    console.log(
        "Leaflet India map created"
    );
}


async function loadIndiaGeoJSON(){

    const paths=[
        "/app/assets/india-states.geojson",
        "assets/india-states.geojson",
        "./assets/india-states.geojson"
    ];


    let geoData=null;
    let lastError=null;


    for(
        const path of paths
    ){

        try{

            console.log(
                "Trying GeoJSON:",
                path
            );


            const response=
                await fetch(path);


            if(!response.ok){

                throw new Error(
                    response.status+
                    " "+
                    response.statusText
                );
            }


            geoData=
                await response.json();


            console.log(
                "GeoJSON loaded:",
                path
            );


            break;

        }catch(error){

            console.warn(
                "GeoJSON failed:",
                path,
                error
            );

            lastError=error;
        }
    }


    if(!geoData){

        throw new Error(
            "India GeoJSON could not be loaded. "+
            (lastError?.message||"")
        );
    }


    return geoData;
}


async function loadIndiaThreatMap(){

    console.log(
        "Loading CyberRadar India Threat Map..."
    );


    try{

        createIndiaMap();


        if(!indiaMap){

            throw new Error(
                "Leaflet map could not be created"
            );
        }


        await loadMapStateData();


        const geoData=
            await loadIndiaGeoJSON();


        console.log(
            "India GeoJSON features:",
            geoData.features?.length
        );


        if(indiaLayer){

            indiaMap.removeLayer(
                indiaLayer
            );

            indiaLayer=null;
        }


        indiaLayer=
            L.geoJSON(
                geoData,
                {

                    style:function(feature){

                        const props=
                            feature.properties||{};


                        const stateName=
                            props.ST_NM||
                            props.NAME_1||
                            props.NAME||
                            props.name||
                            "Unknown";


                        const data=
                            findStateData(
                                stateName
                            );


                        return{

                            color:"#ffffff",

                            weight:1.5,

                            fillColor:
                                getRiskColor(
                                    data?.risk_level||
                                    "LOW"
                                ),

                            fillOpacity:0.65
                        };
                    },


                    onEachFeature:
                        function(
                            feature,
                            layer
                        ){

                            const props=
                                feature.properties||{};


                            const stateName=
                                props.ST_NM||
                                props.NAME_1||
                                props.NAME||
                                props.name||
                                "Unknown";


                            const data=
                                findStateData(
                                    stateName
                                );


                            layer.bindTooltip(
                                `<strong>${stateName}</strong><br>
                                Incidents: ${
                                    Number(
                                        data?.incidents||0
                                    ).toLocaleString(
                                        "en-IN"
                                    )
                                }<br>
                                Risk: ${
                                    data?.risk_level||
                                    "LOW"
                                }`,
                                {
                                    sticky:true
                                }
                            );


                            layer.on(
                                "mouseover",
                                function(e){

                                    e.target.setStyle(
                                        {
                                            weight:3,
                                            color:"#ffffff",
                                            fillOpacity:0.9
                                        }
                                    );


                                    e.target.bringToFront();
                                }
                            );


                            layer.on(
                                "mouseout",
                                function(e){

                                    if(indiaLayer){

                                        indiaLayer.resetStyle(
                                            e.target
                                        );
                                    }
                                }
                            );


                            layer.on(
                                "click",
                                function(e){

                                    L.DomEvent.stopPropagation(
                                        e
                                    );


                                    console.log(
                                        "STATE CLICKED:",
                                        stateName
                                    );


                                    showStateOnMap(
                                        stateName
                                    );
                                }
                            );
                        }
                }
            )
            .addTo(indiaMap);


        const bounds=
            indiaLayer.getBounds();


        if(bounds.isValid()){

            indiaMap.fitBounds(
                bounds,
                {
                    padding:[15,15]
                }
            );
        }


        setTimeout(
            function(){

                if(indiaMap){

                    indiaMap.invalidateSize();
                }

            },
            500
        );


        console.log(
            "CyberRadar India Threat Map loaded successfully!"
        );

    }catch(error){

        console.error(
            "INDIA MAP ERROR:",
            error
        );


        if(typeof toast==="function"){

            toast(
                "India map failed: "+
                error.message,
                true
            );
        }
    }
}


/* =====================================================
   STATE DETAILS
===================================================== */


function setMapValue(id,value){

    const el=$(id);

    if(el){
        el.textContent=value;
    }
}


function showStateOnMap(stateName){

    console.log(
        "CLICKED STATE:",
        stateName
    );


    setMapValue(
        "stateName",
        stateName
    );


    setMapValue(
        "incidentCount",
        "Loading..."
    );


    setMapValue(
        "criticalCount",
        "Loading..."
    );


    setMapValue(
        "financialLoss",
        "Loading..."
    );


    setMapValue(
        "affectedUsers",
        "Loading..."
    );


    /* IMPORTANT:
       Map card uses mapTopAttack,
       mapTopCity and mapTopSector.
       Do NOT use topAttack/topCity/topSector here.
    */


    setMapValue(
        "mapTopAttack",
        "Loading..."
    );


    setMapValue(
        "mapTopCity",
        "Loading..."
    );


    setMapValue(
        "mapTopSector",
        "Loading..."
    );


    setMapValue(
        "riskBadge",
        "Loading..."
    );


    loadStateAnalytics(
        stateName
    );
}


async function loadStateAnalytics(
    stateName
){

    try{

        const response=
            await fetch(
                `${API}/map/state/${encodeURIComponent(
                    stateName
                )}`
            );


        if(!response.ok){

            throw new Error(
                "State API failed: "+
                response.status
            );
        }


        const data=
            await response.json();


        console.log(
            "STATE ANALYTICS:",
            data
        );


        /* -------------------------
           BASIC STATE KPIs
        ------------------------- */


        setMapValue(
            "incidentCount",
            Number(
                data.incidents||0
            ).toLocaleString("en-IN")
        );


        setMapValue(
            "criticalCount",
            Number(
                data.critical||0
            ).toLocaleString("en-IN")
        );


        setMapValue(
            "financialLoss",
            "₹"+
            Number(
                data.financial_loss||0
            ).toLocaleString("en-IN")
        );


        setMapValue(
            "affectedUsers",
            Number(
                data.affected_users||0
            ).toLocaleString("en-IN")
        );


        /* -------------------------
           FIXED MAP VALUES
        ------------------------- */


        setMapValue(
            "mapTopAttack",
            data.top_attack||
            data.topAttack||
            "—"
        );


        setMapValue(
            "mapTopCity",
            data.top_city||
            data.topCity||
            "—"
        );


        setMapValue(
            "mapTopSector",
            data.top_sector||
            data.topSector||
            "—"
        );


        /* -------------------------
           RISK BADGE
        ------------------------- */


        const risk=
            data.risk_level||
            "LOW";


        const score=
            data.risk_score??0;


        const badge=
            $("riskBadge");


        if(badge){

            badge.textContent=
                `${risk} • ${score}/100`;


            badge.className=
                "risk-badge risk-"+
                String(
                    risk
                ).toLowerCase();
        }


    }catch(error){

        console.error(
            "State analytics error:",
            error
        );


        setMapValue(
            "incidentCount",
            "0"
        );


        setMapValue(
            "criticalCount",
            "0"
        );


        setMapValue(
            "financialLoss",
            "₹0"
        );


        setMapValue(
            "affectedUsers",
            "0"
        );


        setMapValue(
            "mapTopAttack",
            "—"
        );


        setMapValue(
            "mapTopCity",
            "—"
        );


        setMapValue(
            "mapTopSector",
            "—"
        );
    }
}


/* =====================================================
   MAP REFRESH
===================================================== */


async function refreshIndiaMap(){

    await loadIndiaThreatMap();
}


/* =====================================================
   INITIALIZATION
===================================================== */


document.addEventListener(
    "DOMContentLoaded",
    async function(){

        /* Dashboard */

        try{

            await loadFilters();
            await loadDashboard();

        }catch(e){

            console.error(
                "Dashboard initialization error:",
                e
            );

            toast(
                "Could not connect to CyberRadar backend",
                true
            );
        }


        /* India Map */

        const mapElement=
            $("indiaMap");


        if(mapElement){

            console.log(
                "India map element found"
            );


            loadIndiaThreatMap();

        }else{

            console.log(
                "India map element not found on this page"
            );
        }


        /* Period filter */

        const period=
            $("period");


        if(period){

            const custom=
                period.value==="custom";


            if($("start")){
                $("start").style.display=
                    custom?"block":"none";
            }


            if($("end")){
                $("end").style.display=
                    custom?"block":"none";
            }
        }
    }
);