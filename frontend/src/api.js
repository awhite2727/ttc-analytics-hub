const API_BASE = "http://127.0.0.1:8000/api";

export async function fetchRouteList() {
    const res = await fetch(`${API_BASE}/route_list`);
    return await res.json();
}

export async function fetchDirections(routeId) {
    const res = await fetch(`${API_BASE}/directions?route_id=${routeId}`);
    return await res.json();
}

export async function fetchMapData(routeId, directionId) {
    const [routesResp, stopsResp] = await Promise.all([
        fetch(`${API_BASE}/routes?route_id=${routeId}&direction_id=${directionId}`),
        fetch(`${API_BASE}/stops?route_id=${routeId}&direction_id=${directionId}`)
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