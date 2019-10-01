import React from 'react';
import ReactDOM from "react-dom";
import {StylesProvider, createGenerateClassName} from "@material-ui/styles";
import {createMuiTheme, MuiThemeProvider} from "@material-ui/core/styles";

import SourceView from "./SourceView";


const theme = createMuiTheme({
  palette: {
    primary: {
      main: '#e75e27',
    },
    secondary: {
      main: '#fff7d1',
    }
  },
  typography: {
    fontFamilySerif: "'Linux Libertine',Georgia,serif",
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
    return [...document.querySelectorAll('.source-view')].map(reader => (
      ReactDOM.render(
        <StylesProvider generateClassName={this.classGenerator}>
          <MuiThemeProvider theme={theme}>
            <SourceView id={parseInt(reader.getAttribute('data-id'))} />
          </MuiThemeProvider>
        </StylesProvider>,
        reader,
      )
    ));
  }
}

export default App;
