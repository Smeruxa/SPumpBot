import { useState, useEffect } from "react";
import KeyInputScreen from "./screens/KeyInputScreen";
import MainScreen from "./screens/MainScreen";
import socket from "./server/server";
import "./styles/App.css";

function App() {
    const [screen, setScreen] = useState("keyInput");

    useEffect(() => {
        const apiKey = localStorage.getItem("apiKey");
        if (apiKey) {
            socket.emit("agree_key", { key: apiKey });
            socket.once("key_answer", (response) => {
                if (response.status === "ok")
                    setScreen("main");
            });
            setScreen("main");
        }
    }, []);

    return (
        <div className="App">
            {screen === "keyInput" ? (
                <KeyInputScreen setScreen={setScreen} />
            ) : (
                <MainScreen setScreen={setScreen} />
            )}
        </div>
    );
}

export default App;