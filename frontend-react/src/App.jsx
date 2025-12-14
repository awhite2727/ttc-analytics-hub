import React, { useState, useEffect } from 'react';
import Map from './components/Map';
import RouteSelect from './components/RouteSelect';
import StatsOverlay from './components/StatsOverlay';
import { fetchRouteList } from './services/api';
import './App.css';

function App() {
    const [routes, setRoutes] = useState([]);
    const [selectedRoute, setSelectedRoute] = useState("");
    const [routeStats, setRouteStats] = useState(null);

    // Load list of routes on startup
    useEffect(() => {
        const loadRoutes = async () => {
            try {
                const data = await fetchRouteList();
                setRoutes(data);
            } catch (error) {
                console.error("Failed to load routes", error);
            }
        };
        loadRoutes();
    }, []);

    return (
        <div className="app-container">
            <Map 
                selectedRoute={selectedRoute} 
                onStatsUpdate={setRouteStats} 
            />
            
            <div className="ui-overlay">
                <RouteSelect 
                    routes={routes} 
                    selectedRoute={selectedRoute} 
                    onChange={setSelectedRoute} 
                />
            </div>

            <StatsOverlay stats={routeStats} />
        </div>
    );
}

export default App;