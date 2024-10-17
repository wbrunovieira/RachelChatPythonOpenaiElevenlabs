import { useState, useEffect } from "react";
import axios from "axios";
import Title from "./Title";
import RecordMessage from "./RecordMessage";

import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

const Controller = () => {
    const MAX_CLASS_DURATION = 10 * 60;
    const MIN_CLASS_DURATION = 10;

    const [isLoading, setIsLoading] = useState(false);

    const [messages, setMessages] = useState<any[]>([]);
    const [currentTopic, setCurrentTopic] = useState<string>("");
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [isAudioReady, setIsAudioReady] = useState<boolean>(false);
    const [transcriptions, setTranscriptions] = useState<any>({});
    const [classStartTime, setClassStartTime] = useState<number | null>(null);
    const [elapsedTime, setElapsedTime] = useState<number>(0);
    const [audioEnabled, setAudioEnabled] = useState<boolean>(false);
    const [classDuration, setClassDuration] =
        useState<number>(MIN_CLASS_DURATION);

    // Duração da aula
    const [isClassStarted, setIsClassStarted] = useState<boolean>(false);

    const [textToDisplay, setTextToDisplay] = useState<string | null>(null);

    useEffect(() => {
        const fetchCurrentTopic = async () => {
            try {
                const res = await axios.get(
                    "http://localhost:8000/current-topic"
                );
                console.log("Current topic:", res.data.current_topic);
                setCurrentTopic(res.data.current_topic);
                setClassStartTime(res.data.class_start_time);
                setClassDuration(res.data.class_duration / 60);
            } catch (err) {
                console.error("Error fetching current topic:", err);
            }
        };

        fetchCurrentTopic();
    }, []);

    useEffect(() => {
        let timer: ReturnType<typeof setInterval>;

        if (isClassStarted && classStartTime) {
            timer = setInterval(() => {
                const now = Date.now() / 1000;
                const elapsed = now - classStartTime;
                setElapsedTime(Math.max(elapsed, 0));

                if (elapsed >= classDuration * 60) {
                    clearInterval(timer);
                    setIsClassStarted(false);
                    setAudioEnabled(false);
                    alert("Class ended! Great job!");
                }
            }, 1000);
        }

        return () => clearInterval(timer);
    }, [isClassStarted, classStartTime, classDuration]);

    const startClass = async () => {
        const now = Date.now() / 1000;
        setClassStartTime(now);
        setIsClassStarted(true);
        setAudioEnabled(true);

        try {
            await axios.post(
                "http://localhost:8000/start-class",
                {
                    start_time: now,
                    duration: classDuration,
                },
                {
                    headers: { "Content-Type": "application/json" },
                }
            );
        } catch (err) {
            console.error("Error starting class:", err);
        }
    };

    const calculateProgress = () => {
        if (!classStartTime || !classDuration || elapsedTime <= 0) return 0;
        return Math.min((elapsedTime / (classDuration * 60)) * 100, 100);
    };

    const formatTime = (timeInSeconds: number) => {
        if (isNaN(timeInSeconds) || timeInSeconds < 0) return "00:00";
        const minutes = Math.floor(timeInSeconds / 60);
        const seconds = Math.floor(timeInSeconds % 60);
        return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(
            2,
            "0"
        )}`;
    };

    const handleDurationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = parseInt(e.target.value, 10);
        if (!isNaN(value) && value >= MIN_CLASS_DURATION) {
            setClassDuration(value);
        }
    };

    function createBlobURL(data: any) {
        console.log("Creating blob URL...");
        const blob = new Blob([data], { type: "audio/mpeg" });
        const url = window.URL.createObjectURL(blob);
        console.log("Blob URL created:", url);
        return url;
    }

    const handleStop = async (blobUrl: string) => {
        console.log("Recording stopped. Blob URL:", blobUrl);
        if (!audioEnabled) return;
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

            <div className="text-center font-bold text-xl mt-4">
                {currentTopic
                    ? `Current Topic: ${currentTopic}`
                    : "No topic set yet"}
            </div>

            <div className="flex justify-center items-center mt-6">
                <div style={{ width: 100, height: 100 }}>
                    <CircularProgressbar
                        value={calculateProgress()}
                        text={
                            isClassStarted
                                ? formatTime(classDuration * 60 - elapsedTime)
                                : formatTime(classDuration * 60)
                        }
                        styles={buildStyles({
                            textColor: "#000",
                            pathColor: "#4caf50",
                            trailColor: "#d6d6d6",
                        })}
                    />
                </div>
            </div>

            <div className="text-center mt-4">
                {!isClassStarted && (
                    <label>
                        Set Class Duration (minutes):
                        <input
                            type="number"
                            value={classDuration || MIN_CLASS_DURATION}
                            onChange={handleDurationChange}
                            min={MIN_CLASS_DURATION}
                            className="ml-2 border p-1"
                        />
                    </label>
                )}

                {!isClassStarted && (
                    <button
                        onClick={startClass}
                        className="mt-4 bg-blue-500 text-white px-4 py-2 rounded"
                    >
                        Start Class
                    </button>
                )}
            </div>

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
                                <div className="mt-4 pb-8">
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

                <div className="fixed bottom-0 w-full py-6 bg-gradient-to-r from-customPurple1 to-customPurple2">
                    <div className="flex justify-center items-center">
                        {audioEnabled && (
                            <RecordMessage handleStop={handleStop} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Controller;
