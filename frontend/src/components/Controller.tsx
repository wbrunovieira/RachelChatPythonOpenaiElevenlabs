import { useState } from "react";
import axios from "axios";
import Title from "./Title";
import RecordMessage from "./RecordMessage";

const Controller = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [messages, setMessages] = useState<any[]>([]);

    function createBlobURL(data: any) {
        console.log("Creating blob URL...");
        const blob = new Blob([data], { type: "audio/mpeg" });
        const url = window.URL.createObjectURL(blob);
        console.log("Blob URL created:", url);
        return url;
    }

    const handleStop = async (blobUrl: string) => {
        console.log("Recording stopped. Blob URL:", blobUrl);
        setIsLoading(true);

        const myMessage = { sender: "me", blobUrl };
        const messagesArr = [...messages, myMessage];
        setMessages(messagesArr);
        console.log("My message added to messages array:", messagesArr);

        try {
            const response = await fetch(blobUrl);
            const blob = await response.blob();
            console.log("Fetched blob from Blob URL:", blob);

            const formData = new FormData();
            formData.append("file", blob, "myFile.wav");
            console.log("Form data prepared:", formData);

            const res = await axios.post(
                "http://localhost:8000/post-audio",
                formData,
                {
                    headers: {
                        "Content-Type": "audio/mpeg",
                    },
                    responseType: "arraybuffer",
                }
            );

            console.log("Received response from server:", res);

            const responseBlob = res.data;
            const audio = new Audio();
            audio.src = createBlobURL(responseBlob);

            const rachelMessage = {
                sender: "rachel",
                blobUrl: audio.src,
            };
            messagesArr.push(rachelMessage);
            setMessages(messagesArr);
            console.log(
                "Rachel's message added to messages array:",
                messagesArr
            );

            // Play audio
            setIsLoading(false);
            console.log("Playing audio...");
            audio.play();
        } catch (err) {
            console.error("Error occurred:", err);
            setIsLoading(false);
        }
    };

    return (
        <div className="h-screen overflow-y-hidden">
            {/* Title */}
            <Title setMessages={setMessages} />

            <div className="flex flex-col justify-between h-full overflow-y-scroll pb-96">
                {/* Conversation */}
                <div className="mt-5 px-5">
                    {messages?.map((audio, index) => {
                        return (
                            <div
                                key={index + audio.sender}
                                className={
                                    "flex flex-col " +
                                    (audio.sender === "rachel" &&
                                        "flex items-end")
                                }
                            >
                                {/* Sender */}
                                <div className="mt-4 ">
                                    <p
                                        className={
                                            audio.sender === "rachel"
                                                ? "text-right mr-2 italic text-green-500"
                                                : "ml-2 italic text-blue-500"
                                        }
                                    >
                                        {audio.sender}
                                    </p>

                                    {/* Message */}
                                    <audio
                                        src={audio.blobUrl}
                                        className="appearance-none"
                                        controls
                                    />
                                </div>
                            </div>
                        );
                    })}

                    {messages.length === 0 && !isLoading && (
                        <div className="text-center font-light italic mt-10">
                            Send Rachel a message...
                        </div>
                    )}

                    {isLoading && (
                        <div className="text-center font-light italic mt-10 animate-pulse">
                            Give me a few seconds...
                        </div>
                    )}
                </div>

                {/* Recorder */}
                <div className="fixed bottom-0 w-full py-6 border-t text-center bg-gradient-to-r from-customPurple1 to-customPurple2">
                    <div className="flex justify-center items-center w-full">
                        <div>
                            <RecordMessage handleStop={handleStop} />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Controller;
