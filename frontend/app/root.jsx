import {
  Links,
  Meta,
  Outlet,
  Scripts,
} from "@remix-run/react";

import "./global.css"
import styles from "./root.module.css";
import Footer from "./components/Footer.jsx";

export default function App() {
  return (
    <html>
      <head>
          <title>Cell Coverage Checker</title>
          <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
          <Meta/>
          <Links/>
      </head>
      <body className={styles.layout}>
      <Outlet />
        <Footer/>

        <Scripts />
      </body>
    </html>
  );
}