import { useState, useEffect } from "react";
import axios from "axios";
import Title from "./Title";
import RecordMessage from "./RecordMessage";

const Controller = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [messages, setMessages] = useState<any[]>([]);
    const [currentTopic, setCurrentTopic] = useState<string>("");
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [isAudioReady, setIsAudioReady] = useState<boolean>(false);
    const [transcriptions, setTranscriptions] = useState<any>({});

    const [textToDisplay, setTextToDisplay] = useState<string | null>(null);

    useEffect(() => {
        const fetchCurrentTopic = async () => {
            try {
                const res = await axios.get(
                    "http://localhost:8000/current-topic"
                );
                console.log("Current topic:", res.data.current_topic);
                setCurrentTopic(res.data.current_topic);
            } catch (err) {
                console.error("Error fetching current topic:", err);
            }
        };

        fetchCurrentTopic();
    }, []);

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

        const myMessage = {
            sender: "me",
            blobUrl,
            showStudentTranscription: false,
            studentTranscription: "",
        };
        const messagesArr = [...messages, myMessage];
        setMessages(messagesArr);
        console.log("My message added to messages array:", messagesArr);

        try {
            const response = await fetch(blobUrl);
            const blob = await response.blob();
            console.log("Fetched blob from Blob URL:", blob);

            const formData = new FormData();
            formData.append("file", blob, "audio.wav");
            console.log("Form data prepared:", formData);

            const fetchResponse = await fetch(
                "http://localhost:8000/post-audio/",
                {
                    method: "POST",
                    body: formData,
                }
            );

            console.log("Received response from server:", fetchResponse);
            const transcriptionId =
                fetchResponse.headers.get("x-transcription-id");
            console.log("transcriptionId", transcriptionId);

            if (!transcriptionId) {
                console.error("No Transcription ID found in response headers");
                throw new Error("Transcription ID missing");
            }
            console.log("Transcription ID:", transcriptionId);

            const audioBlob = await fetchResponse.arrayBuffer();
            const audioUrl = createBlobURL(
                new Blob([audioBlob], { type: "audio/mpeg" })
            );

            const transcriptionData = await fetchTranscription(transcriptionId);
            console.log("Transcription data:", transcriptionData);

            setAudioUrl(audioUrl);
            setIsAudioReady(true);

            myMessage.studentTranscription =
                transcriptionData?.student || "No transcription available";

            const updatedMessages = messagesArr.map((msg) =>
                msg.sender === "me" && msg.blobUrl === blobUrl
                    ? {
                          ...msg,
                          studentTranscription: myMessage.studentTranscription,
                      }
                    : msg
            );

            const rachelMessage = {
                sender: "rachel",
                blobUrl: audioUrl,
                transcriptionId: transcriptionId,
                studentTranscription:
                    transcriptionData?.student || "No transcription available",
                responseTranscription:
                    transcriptionData?.response || "No transcription available",
                showStudentTranscription: false,
                showTeacherTranscription: false,
            };

            updatedMessages.push(rachelMessage);
            setMessages(updatedMessages);
            console.log(
                "Rachel's message added to messages array:",
                updatedMessages
            );

            setIsLoading(false);
        } catch (err) {
            console.error("Error occurred:", err);
            setIsLoading(false);
        }
    };

    const toggleTranscription = (index: number, type: string) => {
        const updatedMessages = messages.map((msg, idx) => {
            if (idx === index) {
                return {
                    ...msg,
                    showStudentTranscription:
                        type === "student"
                            ? !msg.showStudentTranscription
                            : msg.showStudentTranscription,
                    showTeacherTranscription:
                        type === "teacher"
                            ? !msg.showTeacherTranscription
                            : msg.showTeacherTranscription,
                };
            }
            return msg;
        });
        setMessages(updatedMessages);
    };

    const fetchTranscription = async (transcriptionId: string) => {
        try {
            const res = await axios.get(
                `http://localhost:8000/get-transcriptions/${transcriptionId}`
            );
            return res.data;
        } catch (err) {
            console.error("Error fetching transcription:", err);
            return null;
        }
    };

    const playAudio = () => {
        if (audioUrl) {
            const audio = new Audio(audioUrl);
            audio
                .play()
                .then(() => {
                    console.log("Audio is playing...");
                    setIsAudioReady(false);
                })
                .catch((error) => {
                    console.error("Playback failed:", error);
                });
        }
    };

    return (
        <div className="h-screen overflow-y-hidden">
            <Title setMessages={setMessages} />

            {currentTopic && (
                <div className="text-center font-bold text-xl mt-4">
                    Current Topic: {currentTopic}
                </div>
            )}

            <div className="flex flex-col justify-between h-full overflow-y-scroll pb-96">
                <div className="mt-5 px-5">
                    {messages?.map((audio, index) => {
                        return (
                            <div
                                key={index + audio.sender}
                                className={
                                    "flex flex-col " +
                                    (audio.sender === "rachel"
                                        ? "items-end"
                                        : "")
                                }
                            >
                                <div className="mt-4">
                                    <p
                                        className={
                                            audio.sender === "rachel"
                                                ? "text-right mr-2 italic text-green-500"
                                                : "ml-2 italic text-blue-500"
                                        }
                                    >
                                        {audio.sender}
                                    </p>

                                    <audio
                                        src={audio.blobUrl}
                                        className="appearance-none"
                                        controls
                                    />

                                    {audio.sender === "me" && (
                                        <>
                                            <button
                                                onClick={() =>
                                                    toggleTranscription(
                                                        index,
                                                        "student"
                                                    )
                                                }
                                                className="text-blue-500 mt-2 underline"
                                            >
                                                {audio.showStudentTranscription
                                                    ? "Hide Student Transcription"
                                                    : "Show Student Transcription"}
                                            </button>
                                            {audio.showStudentTranscription && (
                                                <p className="mt-2 text-sm text-gray-500 w-96">
                                                    <strong>Student:</strong>{" "}
                                                    {audio.studentTranscription}
                                                </p>
                                            )}
                                        </>
                                    )}

                                    {audio.sender === "rachel" && (
                                        <>
                                            <button
                                                onClick={() =>
                                                    toggleTranscription(
                                                        index,
                                                        "teacher"
                                                    )
                                                }
                                                className="text-green-500 mt-2 underline"
                                            >
                                                {audio.showTeacherTranscription
                                                    ? "Hide Teacher Transcription"
                                                    : "Show Teacher Transcription"}
                                            </button>
                                            {audio.showTeacherTranscription && (
                                                <p className="mt-2 text-sm text-gray-500 w-96">
                                                    <strong>Teacher:</strong>{" "}
                                                    {
                                                        audio.responseTranscription
                                                    }
                                                </p>
                                            )}
                                        </>
                                    )}
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

                <div className="fixed bottom-0 w-full py-6 border-t text-center bg-gradient-to-r from-customPurple1 to-customPurple2">
                    <div className="flex justify-center items-center w-full">
                        <div className="duration-300 text-customYellow hover:scale-105">
                            <RecordMessage handleStop={handleStop} />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Controller;
