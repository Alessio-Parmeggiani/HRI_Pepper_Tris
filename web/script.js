console.log("Hello world")


function body_loaded() {

  const board_matrix = [
    [document.getElementById("t00"), document.getElementById("t01"), document.getElementById("t02")],
    [document.getElementById("t10"), document.getElementById("t11"), document.getElementById("t12")],
    [document.getElementById("t20"), document.getElementById("t21"), document.getElementById("t22")]
  ];

  const board_array = [
    document.getElementById("t00"),
    document.getElementById("t01"),
    document.getElementById("t02"),
    document.getElementById("t10"),
    document.getElementById("t11"),
    document.getElementById("t12"),
    document.getElementById("t20"),
    document.getElementById("t21"),
    document.getElementById("t22")
  ];

  let socket = new WebSocket("ws://localhost:8888/ws");

  socket.onopen = function(e) {
    console.log("[WS open] Connection established");
    console.log("Sending to server");
    socket.send("Hello world");
  };

  socket.onmessage = function(event) {
    const msg = event.data;
    console.log(`[WS message] Data received from server: ${msg}`);

    if (msg.length != 9) {
      console.error("[WS message] Message malformed, its length is not 9");
      return;
    }

    for (let i=0; i<msg.length; i++) {
      let c = msg[i];
      if ("XOxo. ".indexOf(c) == -1) {
        console.error("[WS message] Message malformed, forbidden character");
      }
      c = c.replace("x", "X");
      c = c.replace("o", "O");
      c = c.replace(".", " ");
      // manage classes for text colorization
      board_array[i].classList.remove('has-x');
      board_array[i].classList.remove('has-o');
      if (c=="X") {
        board_array[i].classList.add('has-x');
      }
      if (c=="O") {
        board_array[i].classList.add('has-o');
      }
      // Cool Unicode characters. May not work with Pepper.     ×∘ ○⨯ ◯
      c = c.replace("X", "⨯");
      c = c.replace("O", "○");
      board_array[i].innerText = c;     // temp visualization
    }
  };

  socket.onclose = function(event) {
    if (event.wasClean) {
      console.log(`[WS close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
      // e.g. server process killed
      console.log('[WS close] Connection died');
    }
  };

  socket.onerror = function(error) {
    console.error(`[WS error] ${error.message}`);
  };

}