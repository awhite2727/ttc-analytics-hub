// src/services/api.js
const API_BASE = "http://127.0.0.1:8000/api";

export async function fetchRouteList() {
    const res = await fetch(`${API_BASE}/route_list`);
    return await res.json();
}

export async function fetchMapData(routeId) {
    const [routesResp, stopsResp] = await Promise.all([
        fetch(`${API_BASE}/routes?route_id=${routeId}`),
        fetch(`${API_BASE}/stops?route_id=${routeId}`)
    ]);
    return {
        routes: await routesResp.json(),
        stops: await stopsResp.json()
    };
}

export async function fetchVehicles(routeId) {
    const res = await fetch(`${API_BASE}/vehicles?route_id=${routeId}`);
    return await res.json();
}

export async function fetchRouteStats(routeId) {
    const res = await fetch(`${API_BASE}/route/${routeId}/stats`);
    return await res.json();
}

export async function fetchStopPredictions(stopId) {
    const res = await fetch(`${API_BASE}/stop/${stopId}/predictions`);
    return await res.json();
}

export async function fetchVehicleNextStops(vehicle_id) {
    const res = await fetch(`${API_BASE}/vehicle/${vehicle_id}/next-stops`);
    return await res.json();
}