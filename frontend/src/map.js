import { 
    fetchRouteList, 
    fetchMapData, 
    fetchVehicles,
    fetchRouteStats,       // NEW
    fetchStopPredictions,  // NEW
    fetchVehicleNextStops  // NEW
} from './api.js';

const map = new maplibregl.Map({
    container: 'map',
    style: 'https://tiles.openfreemap.org/styles/bright',
    center: [-79.3832, 43.6532],
    zoom: 12
});

let vehicleInterval = null;
let statsInterval = null; // New interval for updating stats

map.on('load', async () => {
    map.loadImage('./assets/bus-icon-2.png', (error, image) => {
        if (error) throw error;
        map.addImage('bus-icon', image);
    });
    map.loadImage('./assets/bus-arrow.png', (error, image) => {
        if (error) throw error;
        map.addImage('arrow-icon', image);
    });

    // 0. Setup Dashboard UI (The top-right stats box)
    createStatsOverlay();

    // 1. Setup Layers
    setupMapLayers();

    // 2. Interactivity
    setupInteractions();

    // 3. UI
    await populateRouteSelect();
});

function createStatsOverlay() {
    // Create the container if it doesn't exist
    if (!document.getElementById('route-stats-overlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'route-stats-overlay';
        
        // Basic styling - you can move this to CSS
        Object.assign(overlay.style, {
            position: 'absolute',
            top: '10px',
            right: '10px',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            padding: '15px',
            borderRadius: '8px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
            fontFamily: 'sans-serif',
            zIndex: '1',
            minWidth: '200px',
            display: 'none' // Hidden by default until route selected
        });

        document.body.appendChild(overlay);
    }
}

function updateStatsOverlay(stats) {
    const overlay = document.getElementById('route-stats-overlay');
    if (!stats) {
        overlay.style.display = 'none';
        return;
    }

    // Format the content
    const live = stats.live;
    const history = stats.history_24h;

    overlay.innerHTML = `
        <h3 style="margin: 0 0 10px 0; color: #d63031;">Route ${stats.route_id}</h3>
        
        <div style="font-size: 0.9em; margin-bottom: 8px;">
            <strong>Live Status</strong><br>
            🚌 Active Buses: <b>${live.active_buses}</b><br>
            🚀 Avg Speed: <b>${live.current_avg_speed_kph} km/h</b>
        </div>
        
        <div style="font-size: 0.9em; border-top: 1px solid #ccc; padding-top: 8px;">
            <strong>24h Performance</strong><br>
            📅 Avg Speed: ${history.avg_speed_kph || '-'} km/h<br>
            ⚡ Max Speed: ${history.max_speed_kph || '-'} km/h
        </div>
    `;
    overlay.style.display = 'block';
}

function setupMapLayers() {
    // Routes
    map.addSource('ttc-routes', { type: 'geojson', data: { type: "FeatureCollection", features: [] } });
    map.addLayer({
        'id': 'routes-layer',
        'type': 'line',
        'source': 'ttc-routes',
        'layout': { 'line-join': 'round', 'line-cap': 'round' },
        'paint': {
            'line-color': ['case', ['has', 'route_color'], ['get', 'route_color'], "#d63031"],
            'line-width': 4,
            'line-opacity': 0.9
        }
    });

    // Stops
    map.addSource('ttc-stops', { type: 'geojson', data: { type: "FeatureCollection", features: [] } });
    map.addLayer({
        'id': 'stops-layer',
        'type': 'circle',
        'source': 'ttc-stops',
        'paint': { 'circle-radius': 5, 'circle-color': '#ffffff', 'circle-stroke-color': '#2d3436', 'circle-stroke-width': 1.5 }
    });

    // Vehicles
    map.addSource('ttc-vehicles', { type: 'geojson', data: { type: "FeatureCollection", features: [] } });
    map.addLayer({
        'id': 'Vehicles-outline',
        'type': 'circle',
        'source': 'ttc-vehicles',
        'paint': { 'circle-radius': 24, 'circle-color': '#000', 'circle-opacity': 1} // Made slightly smaller/transparent
    });
    map.addLayer({
        'id': 'vehicles-layer',
        'type': 'symbol',       
        'source': 'ttc-vehicles',
        'layout': {
            'icon-image': 'bus-icon',
            'icon-size': 0.04,        
            'icon-allow-overlap': true,
            'icon-rotation-alignment': 'map'
        }
    });

    // Vehicle direction arrows
    map.addLayer({
        'id': 'vehicles-layer-dir',
        'type': 'symbol',       
        'source': 'ttc-vehicles',
        'layout': {
            'icon-image': 'arrow-icon',
            'icon-size': 0.46,        
            'icon-allow-overlap': true,
            'icon-rotate': ['get','arrow_bearing'], 
            'icon-rotation-alignment': 'map',
            'icon-offset': [-58,0]
        }
    });
}

function setupInteractions() {
    // --- STOP CLICK ---
    map.on('click', 'stops-layer', async (e) => {
        const coords = e.features[0].geometry.coordinates.slice();
        const props = e.features[0].properties;
        
        // 1. Show Loading Popup immediately
        const popup = new maplibregl.Popup()
            .setLngLat(coords)
            .setHTML(`<strong>${props.stop_name}</strong><br>Loading upcoming buses...`)
            .addTo(map);

        try {
            // 2. Fetch Data
            const data = await fetchStopPredictions(props.stop_id);
            
            // 3. Build Table
            let content = `<strong>${props.stop_name}</strong><br><small>Stop ID: ${props.stop_id}</small><hr style="margin: 5px 0;">`;
            
            if (data.predictions && data.predictions.length > 0) {
                content += `<table style="width:100%; font-size:12px; text-align:left;">
                            <thead><tr><th>Route</th><th>Bus</th><th>Min</th></tr></thead>
                            <tbody>`;
                
                data.predictions.forEach(p => {
                    const delayClass = p.delay_seconds > 180 ? 'color:red;' : 'color:green;';
                    content += `<tr>
                                    <td>${p.route_id}</td>
                                    <td>${p.vehicle_label}</td>
                                    <td style="font-weight:bold; ${delayClass}">${p.minutes_away}m</td>
                                </tr>`;
                });
                content += `</tbody></table>`;
            } else {
                content += `<em>No upcoming buses found.</em>`;
            }

            popup.setHTML(content);

        } catch (err) {
            popup.setHTML(`<strong>Error</strong><br>Could not load predictions.`);
        }
    });
    
    map.on('mouseenter', 'stops-layer', () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', 'stops-layer', () => map.getCanvas().style.cursor = '');

    // --- VEHICLE CLICK ---
    map.on('click', 'vehicles-layer', async (e) => {
        const coords = e.features[0].geometry.coordinates.slice();
        const props = e.features[0].properties;

        // 1. Show Loading Popup
        const popup = new maplibregl.Popup()
            .setLngLat(coords)
            .setHTML(`<strong>Vehicle ${props.vehicle_label || props.vehicle_id}</strong><br>Loading next stops...`)
            .addTo(map);

        try {
            // 2. Fetch Data
            const data = await fetchVehicleNextStops(props.vehicle_id);

            // 3. Build List
            let content = `<strong>Bus ${props.vehicle_label || props.vehicle_id}</strong><br><small>Trip ID: ${props.trip_id}</small><hr style="margin: 5px 0;">`;

            if (data.next_stops && data.next_stops.length > 0) {
                content += `<ul style="padding-left: 20px; margin: 0; font-size: 12px;">`;
                data.next_stops.forEach(s => {
                    content += `<li><strong>${s.minutes_away} min</strong>: ${s.stop_name}</li>`;
                });
                content += `</ul>`;
            } else {
                content += `<em>No upcoming stops data.</em>`;
            }

            popup.setHTML(content);

        } catch (err) {
            popup.setHTML(`<strong>Error</strong><br>Could not load route info.`);
        }
    });
    
    map.on('mouseenter', 'vehicles-layer', () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', 'vehicles-layer', () => map.getCanvas().style.cursor = '');
}

async function populateRouteSelect() {
    try {
        const routes = await fetchRouteList();
        const routeSelect = document.getElementById('route-select');
        
        routes.forEach(route => {
            const option = document.createElement('option');
            option.value = route.route_id;
            option.textContent = `${route.route_id} - ${route.route_long_name}`;
            routeSelect.appendChild(option);
        });
        
        routeSelect.addEventListener('change', async (e) => {
            const routeId = e.target.value;
            await updateMapData(routeId);

            if (!routeId) {
                clearMap();
                return;
            }
        });
    } catch (error) { console.error(error); }
}

async function updateMapData(routeId) {
    if (routeId === "") return;
    
    // 1. Load Static Data (Map Lines & Stops)
    const data = await fetchMapData(routeId);
    map.getSource('ttc-routes').setData(data.routes);
    map.getSource('ttc-stops').setData(data.stops);
    
    fitMapBounds(data.stops);

    // 2. Clear existing intervals
    if (vehicleInterval) clearInterval(vehicleInterval);
    if (statsInterval) clearInterval(statsInterval);

    // 3. Define Pollers
    const pollVehicles = async () => {
        const vehicles = await fetchVehicles(routeId);
        map.getSource('ttc-vehicles').setData(vehicles);
    };

    const pollStats = async () => {
        const stats = await fetchRouteStats(routeId);
        updateStatsOverlay(stats);
    };
    
    // 4. Start Polling
    pollVehicles(); // Run immediately
    pollStats();    // Run immediately

    vehicleInterval = setInterval(pollVehicles, 5000); // Vehicles every 5s
    statsInterval = setInterval(pollStats, 30000);     // Stats every 30s
}

function fitMapBounds(geoJsonData) {
    if (!geoJsonData.features.length) return;
    const bounds = new maplibregl.LngLatBounds();
    geoJsonData.features.forEach(f => {
        const [lon, lat] = f.geometry.coordinates;
        if (!isNaN(lon) && !isNaN(lat)) bounds.extend([lon, lat]);
    });
    map.fitBounds(bounds, { padding: 50, maxZoom: 15 });
}

function clearMap() {
    const empty = { type: "FeatureCollection", features: [] };
    ['ttc-routes', 'ttc-stops', 'ttc-vehicles'].forEach(id => map.getSource(id).setData(empty));
    
    if (vehicleInterval) clearInterval(vehicleInterval);
    if (statsInterval) clearInterval(statsInterval);
    
    // Hide the overlay
    updateStatsOverlay(null);
}