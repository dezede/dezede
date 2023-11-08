import React from 'react';
import ReactDOM from "react-dom";
import {StylesProvider, createGenerateClassName} from "@material-ui/styles";
import {createMuiTheme, MuiThemeProvider} from "@material-ui/core/styles";
import LinearProgress from "@material-ui/core/LinearProgress";

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
    fontFamily: "'Linux Libertine',Georgia,serif",
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
    return [...document.querySelectorAll('.source-view')].map(div => {
      const sourceId = div.getAttribute('data-id');
      return (
        ReactDOM.render(
          <StylesProvider generateClassName={this.classGenerator}>
            <MuiThemeProvider theme={theme}>
              <React.Suspense fallback={
                <LinearProgress style={{position: 'absolute', top: 0, left: 0, width: '100%'}} />
              }>
                {sourceId && <SourceView id={parseInt(sourceId)} />}
              </React.Suspense>
            </MuiThemeProvider>
          </StylesProvider>,
          div,
        )
      );
    });
  }
}

export default App;
