// 1. Initialize the Map
const map = new maplibregl.Map({
    container: 'map',
    style: 'https://tiles.openfreemap.org/styles/bright',
    center: [-79.3832, 43.6532], // Toronto
    zoom: 12
});

map.on('load', async () => {
    // ----------------------------------------------------
    // 2. SETUP SOURCES & LAYERS (Empty Initially)
    // ----------------------------------------------------
    
    // Route Line Source
    map.addSource('ttc-routes', {
        type: 'geojson',
        data: { type: "FeatureCollection", features: [] }
    });

    // Route Line Layer
    map.addLayer({
        'id': 'routes-layer',
        'type': 'line',
        'source': 'ttc-routes',
        'layout': {
            'line-join': 'round',
            'line-cap': 'round'
        },
        'paint': {
            'line-color': '#d63031', // TTC Red
            'line-width': 4,
            'line-opacity': 0.9
        }
    });

    // Stops Source
    map.addSource('ttc-stops', {
        type: 'geojson',
        data: { type: "FeatureCollection", features: [] }
    });

    // Stops Circle Layer
    map.addLayer({
        'id': 'stops-layer',
        'type': 'circle',
        'source': 'ttc-stops',
        'paint': {
            'circle-radius': 5,
            'circle-color': '#ffffff',
            'circle-stroke-color': '#2d3436',
            'circle-stroke-width': 1.5
        }
    });

    // ----------------------------------------------------
    // 3. INTERACTIVITY (Popups & Hover)
    // ----------------------------------------------------
    
    // Click on a stop to see its name
    map.on('click', 'stops-layer', (e) => {
        const coordinates = e.features[0].geometry.coordinates.slice();
        const props = e.features[0].properties;

        // Ensure popup appears over the point even if zoomed out
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }

        new maplibregl.Popup()
            .setLngLat(coordinates)
            .setHTML(`<strong>${props.stop_name}</strong><br>ID: ${props.stop_id}`)
            .addTo(map);
    });

    // Change cursor to pointer when hovering over stops
    map.on('mouseenter', 'stops-layer', () => {
        map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'stops-layer', () => {
        map.getCanvas().style.cursor = '';
    });

    // ----------------------------------------------------
    // 4. INITIALIZE UI
    // ----------------------------------------------------
    await populateRouteSelect();
});

// --------------------------------------------------------
// LOGIC FUNCTIONS
// --------------------------------------------------------

// A. Fetch list of routes and fill the first dropdown
async function populateRouteSelect() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/route_list');
        const routes = await response.json();
        
        const routeSelect = document.getElementById('route-select');
        
        routes.forEach(route => {
            const option = document.createElement('option');
            option.value = route.route_id;
            // E.g. "501 - Queen"
            option.textContent = `${route.route_id} - ${route.route_long_name}`;
            routeSelect.appendChild(option);
        });

        // Event Listener: When Route Changes
        routeSelect.addEventListener('change', async (e) => {
            const routeId = e.target.value;
            
            // Reset Direction Dropdown
            const dirSelect = document.getElementById('dir-select');
            dirSelect.innerHTML = '<option value="">-- Select Direction --</option>';
            dirSelect.disabled = true;

            // Clear Map if no route selected
            if (!routeId) {
                clearMap();
                return;
            }

            // Fetch Directions for the new route
            await populateDirectionSelect(routeId);
        });

    } catch (error) {
        console.error("Error fetching route list:", error);
    }
}

// B. Fetch directions for a route and fill the second dropdown
async function populateDirectionSelect(routeId) {
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/directions?route_id=${routeId}`);
        const directions = await res.json();
        
        const dirSelect = document.getElementById('dir-select');
        
        directions.forEach(d => {
            const option = document.createElement('option');
            option.value = d.direction_id;
            option.textContent = d.trip_name; // E.g. "East - To Neville Park"
            dirSelect.appendChild(option);
        });

        dirSelect.disabled = false;

        // Auto-select the first direction to immediately show data
        if (directions.length > 0) {
            dirSelect.value = directions[0].direction_id;
            // Trigger update
            updateMapData(routeId, directions[0].direction_id);
        }

        // Event Listener: When Direction Changes
        dirSelect.onchange = (e) => {
            const selectedDir = e.target.value;
            // Note: selectedDir might be "0", so don't just check if(selectedDir)
            if (selectedDir !== "") {
                updateMapData(routeId, selectedDir);
            }
        };

    } catch (error) {
        console.error("Error fetching directions:", error);
    }
}

// C. Fetch Data and Render
async function updateMapData(routeId, directionId) {
    if (!routeId || directionId === undefined || directionId === "") return;

    try {
        console.log(`Fetching Route: ${routeId}, Direction: ${directionId}`);

        // Fetch Routes and Stops in Parallel
        const [routesResp, stopsResp] = await Promise.all([
            fetch(`http://127.0.0.1:8000/api/routes?route_id=${routeId}&direction_id=${directionId}`),
            fetch(`http://127.0.0.1:8000/api/stops?route_id=${routeId}&direction_id=${directionId}`)
        ]);

        const routesData = await routesResp.json();
        const stopsData = await stopsResp.json();

        // Update Map Sources
        const routeSource = map.getSource('ttc-routes');
        const stopSource = map.getSource('ttc-stops');

        if (routeSource) routeSource.setData(routesData);
        if (stopSource) stopSource.setData(stopsData);

        // Fit Camera to Bounds
        fitMapBounds(stopsData);

    } catch (error) {
        console.error("Error loading map data:", error);
    }
}

// D. Helper: Zoom map to fit features
function fitMapBounds(geoJsonData) {
    if (!geoJsonData.features || geoJsonData.features.length === 0) {
        console.warn("No features to zoom to.");
        return;
    }

    const bounds = new maplibregl.LngLatBounds();
    let validPoints = 0;

    geoJsonData.features.forEach(feature => {
        const coords = feature.geometry.coordinates;
        // Check for valid [lon, lat]
        if (Array.isArray(coords) && coords.length === 2) {
            const lon = parseFloat(coords[0]);
            const lat = parseFloat(coords[1]);
            
            if (!isNaN(lon) && !isNaN(lat)) {
                bounds.extend([lon, lat]);
                validPoints++;
            }
        }
    });

    if (validPoints > 0) {
        map.fitBounds(bounds, {
            padding: 75,
            maxZoom: 15
        });
    }
}

// E. Helper: Clear map
function clearMap() {
    const empty = { type: "FeatureCollection", features: [] };
    map.getSource('ttc-routes').setData(empty);
    map.getSource('ttc-stops').setData(empty);
}