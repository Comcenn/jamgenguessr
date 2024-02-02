import { useCallback, useEffect, useState } from "react";

export type WsConnectHandler = (ev: Event) => any;
export type WsMessageHandler = (ev: MessageEvent<any>) => any;
export type WsDisconnectHandler = (ev: Event) => any;

export interface Contextable {
    context: string;
  }
  
  export type ConnectFN = (
    gameCode: string
  ) => void;
  
  export type SessionHook = [
    ConnectFN,
    (args: string) => void,
    () => void
  ];

export function useSession(
    onOpen: WsConnectHandler,
    onMessage: WsMessageHandler,
    onClose: WsDisconnectHandler
): SessionHook {
    const [session, setSession] = useState(null as unknown as WebSocket);

    function addConnectHandler(){
        if (!session) return;
        session.addEventListener("open", onOpen);
        return () => {
            session.removeEventListener("open", onOpen);
        };
    };

    function addMessageHandler(){
        if (!session) return;
        session.addEventListener("message", onMessage);
        return () => {
            session.removeEventListener("message", onMessage);
        };
    };

    function addDisconnectHandler(){
        if (!session) return;
        session.addEventListener("close", onClose);
        return () => {
            session.removeEventListener("close", onClose);
        };
    };

    useEffect(addConnectHandler, [session, onOpen]);
    useEffect(addMessageHandler, [session, onMessage]);
    useEffect(addDisconnectHandler, [session, onClose]);

    const connect = useCallback((gameCode: string) => {
        const socket = new WebSocket(`${"".concat(process.env.NEXT_PUBLIC_API_WS_URL!, gameCode)}`);
        setSession(socket);
    }, []);

    const sendJson = (args: string) => {
        session.send(JSON.stringify(args));
    };

    const close = useCallback(() => {
        if (!session) {
            return;
        };
        if (session.readyState === session.OPEN) {
            session.close(1001);
        };
    }, [session]);

    return [connect, sendJson, close];
};