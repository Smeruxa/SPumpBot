import React, { useState } from "react";
import "../styles/KeyInput.css"
import ModalWindow from "../components/ModalWindow";
import LoadingOverlay from "../components/LoadingOverlay";
import { socket } from "../server/server";

function KeyInputScreen({ setScreen }) {
    const [showModal, setShowModal] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [gotAnswer, setGotAnswer] = useState(false);
    const [modalText, setModalText] = useState(false);
    const [apiKey, setApiKey] = useState("");

    const handleLogin = () => {
        setGotAnswer(false);
        setIsLoading(true);

        socket.emit("agree_key", { key: apiKey });
        socket.once("key_answer", (response) => {
            setIsLoading(false);
            if (response.status !== "ok") {
                setModalText(response.data);
                setShowModal(true);
            }
            else {
                localStorage.setItem("apiKey", apiKey);
                setScreen("main");
            }

            setGotAnswer(true);
        });

        setTimeout(() => {
            if (!gotAnswer) {
                setIsLoading(false);
                setModalText("Сервер не отвечает, попробуйте еще раз..");
                setShowModal(true);
            }
        }, 3000);
    };

    return (
        <div className="key-box">
            <div style={{ textAlign: "center", paddingTop: 0, marginTop: 0 }}>
                <h1 style={{ color: "#fdfdfd" }}><span className="highlight">S</span>PumpBot</h1>
            </div>
            <div className="main">
                <h3 style={{ textWrap: "nowrap" }}>Для того, чтобы продолжить, вам необходимо ввести <span className="highlight">купленный API-ключ</span>.</h3>
                <input className="input-field" type="text" placeholder="Введите API-ключ" onChange={(e) => setApiKey(e.target.value)} />
                <button className="login-button" onClick={handleLogin}>Войти</button>
            </div>
            {showModal && (
                <ModalWindow title="Ошибка" text={modalText} onClose={() => setShowModal(false)} />
            )}
            {isLoading && <LoadingOverlay />}
        </div>
    );
}

export default KeyInputScreen;