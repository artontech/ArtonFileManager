class ArtonWebsocket {
  constructor() {
    this.host = undefined;
    this.socket = undefined;
  }

  // 连接
  connect = (host) => {
    let self = this;
    if (host != undefined) {
      self.host = host;
    }
    if (self.host == undefined) {
      return;
    }

    // 创建websocket
    if ("WebSocket" in window) {
      self.socket = new WebSocket(self.host);
    } else if ("MozWebSocket" in window) {
      console.log("Browser only support MozWebSocket");
      self.socket = new MozWebSocket(self.host);
    } else {
      console.log("Browser only support SockJS");
      self.socket = new SockJS(self.host);
    }

    // websocket连接建立
    self.socket.onopen = self.onOpen;

    // websocket关闭
    self.socket.onclose = function() {
      setTimeout(function() {
        self.connect(undefined);
      }, 5000);
    };

    // websocket监听消息
    self.socket.onmessage = self.onMessage;

    // websocket异常
    self.socket.onerror = function(event) {
      self.onError(event);
      this.close();
    };
  }

  // 主动关闭WebSocket连接
  close = () => {
    this.host = undefined;
    if (this.socket != undefined) {
      this.socket.close();
    }
  }

  // 发送消息
  send = (message) => {
    if (this.socket != undefined) {
      this.socket.send(message);
    }
  }

  // 连接建立
  onOpen = () => {
    console.log("Socket open");
  }

  // 接收消息
  onMessage = (message) => {
    console.log("Socket message:", message.data);
  }

  // 处理异常
  onError = (event) => {
    console.log("Socket error", event);
  }
}

export default ArtonWebsocket;
