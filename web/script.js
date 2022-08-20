/*
For the highlight (and text colorization too): it seems classList is not supported on old browsers for 2011,
so in the unlikely case it's not compatible with Pepper, check our TODO.md for an alternative
*/

console.log("Hello world")


function body_loaded() {

  const pages = document.getElementsByClassName("page");

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
    // console.log("Sending to server");
    // socket.send("Hello world");
  };

  socket.onmessage = function(event) {
    const msg = event.data;
    console.log(`[WS message] Data received from server: ${msg}`);

    // check if it's an event message
    tokens = msg.split(" ");
    if (tokens[0] == "event") {

      if (tokens[1] == "user-approached") {
        document.getElementById("idle").hidden = true;
        document.getElementById("idle-approached").hidden = false;
      }

      else if (tokens[1] == "enter-profiling") {
        document.getElementById("idle-approached").hidden = true;
        document.getElementById("age-select").hidden = false;
      }

      else if (tokens[1] == "pause-game") {
        document.getElementById("game-pause").hidden = false;
        document.getElementById("game-pause-warning").hidden = true;
        document.getElementById("game").hidden = true;
      }

      else if (tokens[1] == "pause-game-warning") {
        document.getElementById("game-pause-warning").hidden = false;
      }

      else if (tokens[1] == "resume-game") {
        document.getElementById("game-pause").hidden = true;
        document.getElementById("game").hidden = false;

      }

      else if (tokens[1] == "interaction-end") {
        for (let i = 0; i < pages.length; i++) {
          pages[i].hidden = true;
        };
        document.getElementById("idle").hidden = false;
      }

      else if (tokens[1] == "loading-start") {
        for (let i = 0; i < pages.length; i++) {
          pages[i].hidden = true;
        };
        document.getElementById("loading").hidden = false;
      }

      else if (tokens[1] == "loading-complete") {
        document.getElementById("loading").hidden = true;
        document.getElementById("game").hidden = false;
      }

      else {
        console.error("[WS message] Event unrecognized.");
      }

      return;

    }

    // or it may be a highlight message
    else if (tokens[0] == "highlight") {
      let hl = tokens[1];

      if (hl.length != 9) {
        console.error("[WS message] Highlight malformed, its length is not 9");
        return;
      }

      for (let i=0; i<hl.length; i++) {
        let c = hl[i];
        if ("Hh. ".indexOf(c) == -1) {
          console.error("[WS message] Highlight malformed, forbidden character");
        }
        c = c.replace("h", "H");
        // manage class for highlight
        if (c == "H") {
          board_array[i].classList.add('highlight');
        }
        else {
          board_array[i].classList.remove('highlight');
        }
      }

      return;
    }

    // if no recognizable prefix, it's a board message

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
      board_array[i].innerText = c;
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


  function get_age_clicked_handler(age) {
    return () => {
      socket.send("age "+age);
      console.log("age "+age);
      document.getElementById("age-select").hidden = true;
      document.getElementById("experience-select").hidden = false;
    }
  }
  function get_experience_clicked_handler(exp) {
    return () => {
      socket.send("experience "+exp);
      console.log("experience "+exp);
      document.getElementById("experience-select").hidden = true;
      document.getElementById("loading").hidden = false;
    }
  }

  //age buttons
  age1_button = document.getElementById("baby");
  age2_button = document.getElementById("teen");
  age3_button = document.getElementById("young");
  age4_button = document.getElementById("old");
  //experience buttons
  experience1_button = document.getElementById("beginner");
  experience2_button = document.getElementById("expert");
  //function on button click
  age1_button.onclick = get_age_clicked_handler(0.25);
  age2_button.onclick = get_age_clicked_handler(0.5);
  age3_button.onclick = get_age_clicked_handler(0.75);
  age4_button.onclick = get_age_clicked_handler(1.0);
  experience1_button.onclick = get_experience_clicked_handler(0.25);
  experience2_button.onclick = get_experience_clicked_handler(0.75);






  function get_tile_click_handler(row, col) {
    return () => {
      socket.send("click "+row+" "+col);
      console.log("click "+row+" "+col);
    }
  }

  for (let i=0; i<board_matrix.length; i++) {
    for (let j=0; j<board_matrix[i].length; j++) {
      board_matrix[i][j].onclick = get_tile_click_handler(i, j);
    }
  }

}
