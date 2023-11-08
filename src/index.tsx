import React from "react";
import ReactDOM from "react-dom";

import "./i18n";
import App from "./App";

[...document.querySelectorAll(".source-view")].forEach((div) => {
  ReactDOM.render(<App div={div} />, div);
});
