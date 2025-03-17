import React from "react";
import "../styles/ModalWindow.css";

function ModalWindow({ title, text, onClose }) {
    return (
        <div className="modal-overlay">
            <div className="modal-window">
                <h2 className="modal-title">{title}</h2>
                <p className="modal-text">{text}</p>
                <button className="modal-button" onClick={onClose}>Закрыть</button>
            </div>
        </div>
    );
}

export default ModalWindow;