import React from "react";
import "../styles/LoadingOverlay.css";

function LoadingOverlay() {
    return (
        <div className="loading-overlay">
            <div className="loading-content">
                <div className="loading-spinner"></div>
                <p>Загрузка...</p>
            </div>
        </div>
    );
}

export default LoadingOverlay;