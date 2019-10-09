import i18n from 'i18next';
import XHR from "i18next-xhr-backend";
import {initReactI18next} from "react-i18next";


i18n
  .use(XHR)
  .use(initReactI18next)
  .init({
    lng: document.getElementsByTagName('html')[0].getAttribute('lang'),
    fallbackLng: 'en',
    backend: {
      loadPath: '/static/locales/{{lng}}/{{ns}}.json',
    },
    ns: [],
    keySeparator: false,
    interpolation: {
      escapeValue: false,
    },
  });


export default i18n;
