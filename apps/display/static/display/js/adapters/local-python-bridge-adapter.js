import {WebSocketDetectionAdapter} from "./websocket-adapter.js";

// Local Python services publish the same normalized contract over WebSocket.
// The display never imports model-specific Python or inference code.
export class LocalPythonBridgeAdapter extends WebSocketDetectionAdapter {}
