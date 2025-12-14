import React from 'react';

const StatsOverlay = ({ stats }) => {
    if (!stats) return null;

    const { live, history_24h: history, route_id } = stats;

    return (
        <div className="stats-overlay">
            <h3>Route {route_id}</h3>
            
            <div className="stats-section">
                <strong>Live Status</strong>
                <div>🚌 Active Buses: <b>{live.active_buses}</b></div>
                <div>🚀 Avg Speed: <b>{live.current_avg_speed_kph} km/h</b></div>
            </div>
            
            <div className="stats-section border-top">
                <strong>24h Performance</strong>
                <div>📅 Avg Speed: {history.avg_speed_kph || '-'} km/h</div>
                <div>⚡ Max Speed: {history.max_speed_kph || '-'} km/h</div>
            </div>
        </div>
    );
};

export default StatsOverlay;