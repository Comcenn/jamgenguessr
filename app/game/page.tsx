"use client";

import SelectBlock from "@/components/form/select";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { useEffect, useReducer, useState } from "react";
import { BarLoader } from "react-spinners";


const subjectOptions = [
  { title: "duck", value: "duck" },
  { title: "dog", value: "dog" },
  { title: "tractor", value: "tractor" },
  { title: "banana", value: "banana" },
];
const locationOptions = [
  { title: "the sky", value: "the sky" },
  { title: "a bath", value: "a bath" },
  { title: "the desert", value: "the desert" },
  { title: "the ocean", value: "the ocean" },
];

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

type ImageResult = {
  id: string;
  status: "completed" | "error" | "waiting" | "processing";
  image_url?: string;
};

enum Role {
  CONTROLLER = "CONTROLLER",
  GUESSER = "GUESSER"
};

interface IGameData{
  playerId: string
  score: number
  role: "CONTROLLER" | "GUESSER" | null
  round: number
  imageUrl: string
};

type Action =
  | {type: "CONFIG", nextScore: number, roundNumber: number, controllerId: string, imageUrl: string, target: string}
  | {type: "GUESS"}
  | {type: "GENERATED", imageUrl: string}
  | {type: "NEW_ROUND", controllerId: string, nextScore: number, roundNumber: number}
  | {type: "UPDATE_PLAYER", playerId: string}

function reducer(state: IGameData, action: Action): IGameData{
  switch (action.type) {
    case "CONFIG": {
      if (action.target === state.playerId){
        return {
          ...state,
          score: action.nextScore,
          round: action.roundNumber,
          role: action.controllerId === state.playerId ? "CONTROLLER" : "GUESSER",
          imageUrl: action.imageUrl
        };
      }
      return {...state};
    }
    case "GENERATED": {
      return {
        ...state,
        imageUrl: action.imageUrl
      };
    }
    case "NEW_ROUND": {
      return {
        ...state,
        role: action.controllerId === state.playerId ? "CONTROLLER" : "GUESSER",
        imageUrl: "",

      };
    }
    case "UPDATE_PLAYER": {
      return {
        ...state,
        playerId: action.playerId
      }
    }
    default: {
      return {
        ...state
      };
    }
  }
};

export default function Game() {
  const searchParams = useSearchParams();
  const gameId = searchParams.get("id");

  const [state, dispatch] = useReducer(reducer, {
        playerId: "",
        score: 0,
        role: null,
        round: 0,
        imageUrl: ""
  });

  const [ws, setWs] = useState<WebSocket | null>();

  const [isConnected, setIsConnected] = useState(false);

  const [subject, setSubject] = useState<string>("duck");
  const [location, setLocation] = useState<string>("the sky");
  const [imageResult, setImageResult] = useState<ImageResult | null>();
  const [error, setError] = useState<string | null>();

  useEffect(() => {
    // Check in local storage for playerId
    let playerId = localStorage.getItem("playerId");

    if (!playerId) {
      console.log("No player ID generating....");
      playerId = Math.random().toString(20).substring(2, 10);
      console.log(`Player ID: ${playerId}`);
      localStorage.setItem("playerId", playerId);
    }

    dispatch({type: "UPDATE_PLAYER", playerId: playerId});

    const socket = new WebSocket("".concat(process.env.NEXT_PUBLIC_API_WS_URL!, gameId!, "/", playerId));

    socket.onopen = () => {
      console.log("Connected...");
      setIsConnected(true);
    };

    socket.onclose = () => {
      console.log(`Disconnected from game ${gameId}`)
      setIsConnected(false);
    };

    socket.onerror = (error) => {
      console.log(error);
    };

    socket.onmessage = (event) => {
      console.log(`Message: ${event.data}`);
      const message = JSON.parse(event.data);
      dispatch(message)
    };

    setWs(socket);

    return () => {
      console.log("Closing Connection....");
      socket.close();
    };
  }, [setWs, dispatch]);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Submitting");

    if (state.role === Role.CONTROLLER) {

      setImageResult({ id: "", status: "waiting" });

      const response = await fetch("/api/images/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: `A photo of a ${subject} in ${location}`,
        }),
      });

      let result = await response.json();

      if (response.status !== 200) {
        setError(`An error occurred.`);
        return;
      }

      setImageResult(result);

      while (result.status !== "completed" && result.status !== "failed") {
        await sleep(6000);
        const response = await fetch("/api/images/result/" + result.id);
        result = await response.json();
        if (response.status !== 200) {
          setError(`An error occurred.`);
          return;
        }
        console.log(result.image_url)
        if (result.image_url){

          ws?.send(JSON.stringify({imageUrl: result.image_url, prompt: `A photo of a ${subject} in ${location}`, type:"GENERATED", playerId: state.playerId, game_id: gameId}));
        }
        setImageResult(result);
      }
    } else {
      console.log("Guessing")
      ws?.send(JSON.stringify({prompt: `A photo of a ${subject} in ${location}`, type: "GUESS", playerId: state.playerId, game_id: gameId}))
    }
  };

  const image = state.role === Role.CONTROLLER && imageResult?.image_url ? imageResult.image_url : state.imageUrl

  return (
    <div className="grid grid-cols-1 m-auto">
      <div className="flex flex-none h-fit mx-auto text-sm uppercase gap-4 p-8">
        <div className="my-auto">You are the</div>
        <div className="border border-white rounded py-2 px-4">{state.role}</div>
      </div>
      {error && (
        <div className="flex flex-none h-fit mx-auto uppercase">
          <div className="mb-4 text-red-400 uppercase">{error}</div>
        </div>
      )}
      <div className="flex flex-1">
        <div className="flex mx-auto border border-white rounded border-opacity-50 aspect-square w-[80vw] max-w-[50vh]">
          {image && (
            <>
              {image ? (
                <div className="relative w-full">
                  <Image
                    src={image}
                    alt="Generated image"
                    priority
                    fill
                  />
                </div>
              ) : (
                <div className="flex flex-col m-auto text-gray-400 p-4 gap-1">
                  <div className="mx-auto">
                    {imageResult?.status.toUpperCase()}
                  </div>
                  <div>
                    <BarLoader color={"#ffffff"} loading={true} />
                  </div>
                </div>
              )}
            </>
          )}

          {!image && (
            <div className="m-auto text-gray-400 p-4 text-center">
              Choose your prompt and generate!
            </div>
          )}
        </div>
      </div>
      <form
        className="flex flex-none flex-row text-sm uppercase mx-auto h-fit p-8"
        onSubmit={handleSubmit}
      >
        <div className="my-auto">A photo of a</div>
        <div className="my-auto">
          <SelectBlock
            items={subjectOptions}
            label="Subject"
            onChange={setSubject}
          />
        </div>
        <div className="my-auto">in</div>
        <div className="my-auto">
          <SelectBlock
            items={locationOptions}
            label="Location"
            onChange={setLocation}
          />
        </div>
        <div>
          <button
            className="bg-white border border-white text-black h-full px-6 text-sm rounded hover:bg-opacity-0 hover:text-white disabled:opacity-10 disabled:hover:bg-white disabled:hover:text-black"
            type="submit"
            disabled={
              imageResult != null &&
              (imageResult.status == "processing" ||
                imageResult.status == "waiting")
            }
          >
            {state.role === Role.CONTROLLER ? "Generate": "Guess"}
          </button>
        </div>
      </form>
      <div>
        {}
      </div>
    </div>
  );
}
