import React from 'react';

const RouteSelect = ({ routes, selectedRoute, onChange }) => {
    return (
        <div className="control-panel">
            <label htmlFor="route-select">Route:</label>
            <select 
                id="route-select" 
                value={selectedRoute} 
                onChange={(e) => onChange(e.target.value)}
            >
                <option value="">-- Select Route --</option>
                {routes.map(route => (
                    <option key={route.route_id} value={route.route_id}>
                        {route.route_id} - {route.route_long_name}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default RouteSelect;