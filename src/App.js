import React from 'react';
import ReactDOM from "react-dom";
import {StylesProvider, createGenerateClassName} from "@material-ui/styles";
import {createMuiTheme, MuiThemeProvider} from "@material-ui/core/styles";

import Reader from "./Reader";


const theme = createMuiTheme({
  palette: {
    primary: {
      main: '#e75e27',
    },
    secondary: {
      main: '#fff7d1',
    }
  },
  overrides: {
    MuiButtonBase: {
      root: {
        '&:hover': {
          color: 'inherit',
        },
      },
    },
  },
});


class App extends React.Component {
  classGenerator = createGenerateClassName({
    productionPrefix: 'c',
  });

  render() {
    return [...document.querySelectorAll('.reader')].map(reader => (
      ReactDOM.render(
        <StylesProvider generateClassName={this.classGenerator}>
          <MuiThemeProvider theme={theme}>
            <Reader
              sourceId={parseInt(reader.getAttribute('data-source-id'))} />
          </MuiThemeProvider>
        </StylesProvider>,
        reader,
      )
    ));
  }
}

export default App;
