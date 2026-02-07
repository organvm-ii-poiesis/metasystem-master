/**
 * Type declarations for node-osc library
 */

declare module 'node-osc' {
  export class Client {
    constructor(host: string, port: number);
    send(address: string, ...args: (number | string)[]): void;
    close(): void;
  }

  export class Server {
    constructor(port: number, host?: string);
    on(event: 'message', callback: (msg: any[], rinfo: any) => void): void;
    on(event: 'error', callback: (error: Error) => void): void;
    close(): void;
  }
}
