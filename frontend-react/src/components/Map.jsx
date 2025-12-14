import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { 
    fetchMapData, 
    fetchVehicles, 
    fetchRouteStats, 
    fetchStopPredictions, 
    fetchVehicleNextStops 
} from '../services/api';

// Images (Ensure these are in your public/assets folder or imported)
import busIconUrl from '../assets/bus-icon-2.png'; 
import arrowIconUrl from '../assets/bus-arrow.png';

const Map = ({ selectedRoute, onStatsUpdate }) => {
    const mapContainer = useRef(null);
    const map = useRef(null);
    const [isMapLoaded, setIsMapLoaded] = useState(false);
    
    // Refs for intervals to clear them properly
    const vehicleInterval = useRef(null);
    const statsInterval = useRef(null);

    // 1. Initialize Map
    useEffect(() => {
        if (map.current) return; // Initialize only once

        map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: 'https://tiles.openfreemap.org/styles/bright',
            center: [-79.3832, 43.6532],
            zoom: 12
        });

        map.current.on('load', () => {
            const m = map.current;
            
            // Load Images
            m.loadImage(busIconUrl, (error, image) => {
                if (!error) m.addImage('bus-icon', image);
            });
            m.loadImage(arrowIconUrl, (error, image) => {
                if (!error) m.addImage('arrow-icon', image);
            });

            // Initialize Sources
            m.addSource('ttc-routes', { type: 'geojson', data: { type: "FeatureCollection", features: [] } });
            m.addSource('ttc-stops', { type: 'geojson', data: { type: "FeatureCollection", features: [] } });
            m.addSource('ttc-vehicles', { type: 'geojson', data: { type: "FeatureCollection", features: [] } });

            // Add Layers
            addLayers(m);
            
            // Setup Click Interactions
            setupInteractions(m);

            setIsMapLoaded(true);
        });
    }, []);

    // 2. Handle Route Changes & Polling
    useEffect(() => {
        if (!isMapLoaded) return;

        const cleanup = () => {
            if (vehicleInterval.current) clearInterval(vehicleInterval.current);
            if (statsInterval.current) clearInterval(statsInterval.current);
            
            // Clear map data
            const empty = { type: "FeatureCollection", features: [] };
            ['ttc-routes', 'ttc-stops', 'ttc-vehicles'].forEach(id => {
                if (map.current.getSource(id)) map.current.getSource(id).setData(empty);
            });
            onStatsUpdate(null);
        };

        const updateMap = async () => {
            if (!selectedRoute) {
                cleanup();
                return;
            }

            // Cleanup previous pollers
            if (vehicleInterval.current) clearInterval(vehicleInterval.current);
            if (statsInterval.current) clearInterval(statsInterval.current);

            try {
                // Fetch Static Data
                const data = await fetchMapData(selectedRoute);
                map.current.getSource('ttc-routes').setData(data.routes);
                map.current.getSource('ttc-stops').setData(data.stops);
                fitMapBounds(map.current, data.stops);

                // Define Pollers
                const pollVehicles = async () => {
                    const vehicles = await fetchVehicles(selectedRoute);
                    map.current.getSource('ttc-vehicles').setData(vehicles);
                };

                const pollStats = async () => {
                    const stats = await fetchRouteStats(selectedRoute);
                    onStatsUpdate(stats);
                };

                // Run immediately and set intervals
                pollVehicles();
                pollStats();

                vehicleInterval.current = setInterval(pollVehicles, 5000);
                statsInterval.current = setInterval(pollStats, 30000);
            } catch (err) {
                console.error("Error updating map:", err);
            }
        };

        updateMap();

        return cleanup; // Cleanup on unmount or route change
    }, [selectedRoute, isMapLoaded]); // Run when route changes or map loads

    return <div ref={mapContainer} style={{ width: '100%', height: '100vh', position: 'absolute', top: 0, left: 0 }} />;
};

// --- Helper Functions ---

function addLayers(map) {
    // Route Lines
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
    map.addLayer({
        'id': 'stops-layer',
        'type': 'circle',
        'source': 'ttc-stops',
        'paint': { 'circle-radius': 5, 'circle-color': '#ffffff', 'circle-stroke-color': '#2d3436', 'circle-stroke-width': 1.5 }
    });

    // Vehicles
    map.addLayer({
        'id': 'Vehicles-outline',
        'type': 'circle',
        'source': 'ttc-vehicles',
        'paint': { 'circle-radius': 24, 'circle-color': '#000', 'circle-opacity': 1}
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

function setupInteractions(map) {
    // Stop Click
    map.on('click', 'stops-layer', async (e) => {
        const props = e.features[0].properties;
        const coords = e.features[0].geometry.coordinates.slice();

        const popup = new maplibregl.Popup()
            .setLngLat(coords)
            .setHTML(`<strong>${props.stop_name}</strong><br>Loading...`)
            .addTo(map);

        try {
            const data = await fetchStopPredictions(props.stop_id);
            let content = `<strong>${props.stop_name}</strong><br><small>Stop ID: ${props.stop_id}</small><hr style="margin: 5px 0;">`;
            
            if (data.predictions && data.predictions.length > 0) {
                content += `<table style="width:100%; font-size:12px; text-align:left;">
                            <thead><tr><th>Route</th><th>Bus</th><th>Min</th></tr></thead>
                            <tbody>`;
                data.predictions.forEach(p => {
                    const color = p.delay_seconds > 180 ? 'red' : 'green';
                    content += `<tr>
                                    <td>${p.route_id}</td>
                                    <td>${p.vehicle_label}</td>
                                    <td style="font-weight:bold; color:${color};">${p.minutes_away}m</td>
                                </tr>`;
                });
                content += `</tbody></table>`;
            } else {
                content += `<em>No upcoming buses found.</em>`;
            }
            popup.setHTML(content);
        } catch (err) {
            popup.setHTML(`Error loading predictions.`);
        }
    });

    // Vehicle Click
    map.on('click', 'vehicles-layer', async (e) => {
        const props = e.features[0].properties;
        const coords = e.features[0].geometry.coordinates.slice();
        
        const popup = new maplibregl.Popup()
            .setLngLat(coords)
            .setHTML(`<strong>Vehicle ${props.vehicle_label || props.vehicle_id}</strong><br>Loading...`)
            .addTo(map);

        try {
            const data = await fetchVehicleNextStops(props.vehicle_id);
            let content = `<strong>Bus ${props.vehicle_label || props.vehicle_id}</strong><br><small>Trip: ${props.trip_id}</small><hr style="margin: 5px 0;">`;
            
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
            popup.setHTML(`Error loading vehicle info.`);
        }
    });

    map.on('mouseenter', ['stops-layer', 'vehicles-layer'], () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', ['stops-layer', 'vehicles-layer'], () => map.getCanvas().style.cursor = '');
}

function fitMapBounds(map, geoJsonData) {
    if (!geoJsonData.features.length) return;
    const bounds = new maplibregl.LngLatBounds();
    geoJsonData.features.forEach(f => {
        const [lon, lat] = f.geometry.coordinates;
        if (!isNaN(lon) && !isNaN(lat)) bounds.extend([lon, lat]);
    });
    map.fitBounds(bounds, { padding: 50, maxZoom: 15 });
}

export default Map;