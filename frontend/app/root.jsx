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
        <Meta />
        <Links />
      </head>
      <body className={styles.layout}>
        <Outlet />
        <Footer/>

        <Scripts />
      </body>
    </html>
  );
}